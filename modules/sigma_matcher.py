"""
PERSEPTOR v3.0 — Advanced Global Sigma Matching Engine
Multi-signal scoring: MITRE ATT&CK technique match + IoC-type logsource routing
+ IoC value detection match + TF-IDF keyword match.
Produces "Direct Hit" quality results that SOC analysts can deploy immediately.
"""

import os
import re
import math
import yaml
import concurrent.futures
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional
from modules.logging_config import get_logger

logger = get_logger("sigma_matcher")

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader

SIGMAHQ_BASE_URL = os.environ.get(
    "SIGMAHQ_BASE_URL", "https://github.com/SigmaHQ/sigma/blob/master"
)

# ─── IoC-Type → Logsource Category Mapping ──────────────────────────────────
IOC_TO_LOGSOURCE: Dict[str, List[str]] = {
    "ips": ["network_connection", "firewall"],
    "domains": ["dns_query", "dns"],
    "urls": ["proxy", "network_connection", "webserver"],
    "malicious_commands": ["process_creation", "ps_script", "ps_module", "ps_classic"],
    "process_names": ["process_creation", "image_load"],
    "filenames": ["file_event", "file_change", "file_access", "file_delete", "file_rename"],
    "registry_keys": ["registry_set", "registry_add", "registry_event", "registry_delete"],
    "file_hashes": ["file_event", "process_creation", "driver_load"],
}

# ─── MITRE Technique Pattern ────────────────────────────────────────────────
_TECHNIQUE_RE = re.compile(r"attack\.t(\d{4}(?:\.\d{3})?)", re.IGNORECASE)

# ─── Stopwords ──────────────────────────────────────────────────────────────
_CUSTOM_STOPWORDS = {
    "of", "c:", "and", "the", "a", "an", "to", "in", "for", "by", "on",
    "with", "or", "if", "is", "at", "as", "all", "windows", "microsoft",
    "this", "that", "it", "not", "be", "are", "was", "were", "has", "have",
    "had", "do", "does", "did", "will", "would", "shall", "should", "may",
    "might", "can", "could", "no", "yes", "from", "but", "so", "than",
    "too", "very", "just", "about", "up", "out", "into",
}

# ─── Sigma Field Name Blocklist ──────────────────────────────────────────────
# These are Sigma rule structure field names / detection block keys that should
# NEVER appear as "matched keywords" shown to the user. They are rule syntax,
# not indicator values.
_SIGMA_FIELD_BLOCKLIST = {
    # Detection block keys
    "selection", "filter", "condition", "detection", "logsource",
    "image", "user", "status", "level", "title", "description",
    "author", "date", "references", "tags", "fields", "falsepositives",
    # Common selection/filter sub-key patterns
    "selection_process", "selection_main", "selection_img", "selection_cli",
    "selection_parent", "selection_hash", "selection_registry",
    "selection_network", "selection_file", "selection_service",
    "selection_user", "selection_command", "selection_pipe",
    "selection_powershell", "selection_encoded", "selection_renamed",
    # Sigma field names (these are field references, not values)
    "commandline", "parentimage", "parentcommandline", "originalfilename",
    "targetfilename", "sourcefilename", "destinationfilename",
    "targetobject", "newprocessname", "parentprocessname", "processname",
    "imphash", "sha256", "sha1", "md5", "hashes", "signed", "signature",
    "signaturestatus", "product", "category", "service",
    "eventid", "eventtype", "channel", "provider_name",
    "logonid", "logontype", "targetusername", "sourceusername",
    "subjectuserdsid", "subjectusername", "subjectlogonid",
    "destinationport", "destinationip", "sourceport", "sourceip",
    "imagepath", "imageloaded", "calltracestring",
    "accessmask", "objecttype", "objectname",
    "queryname", "querystatus", "queryresults",
}

def _is_sigma_field_name(token: str) -> bool:
    """Check if a token is a Sigma field name or structural key, not a real IoC value."""
    t = token.lower().strip()
    # Direct blocklist match
    if t in _SIGMA_FIELD_BLOCKLIST:
        return True
    # Patterns: filter_*, selection_*, *_filter, *_selection
    if t.startswith(("filter_", "filter.", "selection_", "selection.")):
        return True
    if t.endswith(("_filter", "_selection")):
        return True
    # Very short generic tokens
    if len(t) <= 3 and t.isalpha():
        return True
    return False

_stopwords_cache: Optional[Set[str]] = None


def _get_stopwords() -> Set[str]:
    global _stopwords_cache
    if _stopwords_cache is not None:
        return _stopwords_cache
    sw = set(_CUSTOM_STOPWORDS)
    try:
        from nltk.corpus import stopwords
        sw |= set(stopwords.words("english"))
    except Exception:
        pass
    _stopwords_cache = sw
    return sw


# ─── Tokenization ───────────────────────────────────────────────────────────
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9\-\.:;\\/_]+")


def _tokenize(text: str) -> List[str]:
    sw = _get_stopwords()
    return [t for t in _TOKEN_PATTERN.findall(text) if len(t) >= 3 and t.lower() not in sw]


def _tokenize_lower(text: str) -> Set[str]:
    sw = _get_stopwords()
    return {t.lower() for t in _TOKEN_PATTERN.findall(text) if len(t) >= 3 and t.lower() not in sw}


# ─── YAML Loading ───────────────────────────────────────────────────────────

def _load_yaml_file(file_path: str, root_directory: str):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            docs = list(yaml.load_all(f, Loader=Loader))
        results = []
        relative = os.path.relpath(file_path, root_directory)
        for doc in docs:
            if isinstance(doc, dict) and "title" in doc:
                results.append({
                    "file_path": file_path,
                    "relative_path": relative,
                    "rule_data": doc,
                })
        return results if results else None
    except Exception:
        return None


def load_sigma_rules_local(root_directory: str) -> List[dict]:
    """Load all Sigma rules from a directory tree."""
    file_paths = []
    for subdir, _, files in os.walk(root_directory):
        for f in files:
            if f.endswith((".yml", ".yaml")):
                file_paths.append(os.path.join(subdir, f))

    logger.info(f"Found {len(file_paths)} YAML files in {root_directory}")

    sigma_rules: List[dict] = []
    errors = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_load_yaml_file, fp, root_directory): fp for fp in file_paths}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    sigma_rules.extend(result)
                else:
                    errors += 1
            except Exception:
                errors += 1

    logger.info(f"Loaded {len(sigma_rules)} Sigma rules ({errors} errors)")
    return sigma_rules


# ─── Enhanced Inverted Index ────────────────────────────────────────────────

class SigmaIndex:
    """Multi-signal inverted index for high-precision Sigma rule matching."""

    def __init__(self, rules: List[dict]):
        self.rules = rules
        # Existing keyword index
        self.index: Dict[str, Set[int]] = defaultdict(set)
        self.rule_keywords: Dict[int, List[str]] = {}
        self.rule_phrases: Dict[int, List[str]] = {}
        self.doc_count = len(rules)
        self.df: Dict[str, int] = defaultdict(int)

        # NEW: MITRE technique index
        self.technique_index: Dict[str, Set[int]] = defaultdict(set)
        self.rule_techniques: Dict[int, Set[str]] = {}

        # NEW: Logsource index
        self.logsource_index: Dict[str, Set[int]] = defaultdict(set)
        self.rule_logsource: Dict[int, dict] = {}

        # NEW: Quality metadata
        self.rule_status: Dict[int, str] = {}
        self.rule_level: Dict[int, str] = {}

        self._build_index()

    def _build_index(self):
        """Build multi-signal inverted index from all rules."""
        for idx, rule_info in enumerate(self.rules):
            rule_data = rule_info["rule_data"]
            detection = rule_data.get("detection", {})
            keywords, phrases = self._extract_detection_terms(detection)

            self.rule_keywords[idx] = keywords
            self.rule_phrases[idx] = phrases

            # Keyword inverted index
            seen: Set[str] = set()
            for kw in keywords:
                kw_lower = kw.lower()
                self.index[kw_lower].add(idx)
                if kw_lower not in seen:
                    self.df[kw_lower] += 1
                    seen.add(kw_lower)

            # ── MITRE technique index ──
            techniques: Set[str] = set()
            tags = rule_data.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str):
                        m = _TECHNIQUE_RE.search(tag)
                        if m:
                            tid = "t" + m.group(1).lower()
                            techniques.add(tid)
                            self.technique_index[tid].add(idx)
                            # Also index parent technique (e.g., t1059 from t1059.001)
                            parent = tid.split(".")[0]
                            if parent != tid:
                                techniques.add(parent)
                                self.technique_index[parent].add(idx)
            self.rule_techniques[idx] = techniques

            # ── Logsource index ──
            logsource = rule_data.get("logsource", {})
            category = logsource.get("category", "unknown") if isinstance(logsource, dict) else "unknown"
            product = logsource.get("product", "unknown") if isinstance(logsource, dict) else "unknown"
            composite_key = f"{category}:{product}"
            self.logsource_index[composite_key].add(idx)
            # Also index just by category (for cross-product matching)
            self.logsource_index[f"{category}:*"].add(idx)
            self.rule_logsource[idx] = {"category": category, "product": product}

            # ── Quality metadata ──
            self.rule_status[idx] = rule_data.get("status", "experimental")
            self.rule_level[idx] = rule_data.get("level", "medium")

        logger.info(
            f"Built multi-signal index: {len(self.index)} keyword terms, "
            f"{len(self.technique_index)} technique IDs, "
            f"{len(self.logsource_index)} logsource keys, "
            f"{self.doc_count} rules"
        )

    def _extract_detection_terms(self, detection_data) -> Tuple[List[str], List[str]]:
        """Extract keywords and multi-word phrases from detection data."""
        if isinstance(detection_data, dict) and "condition" in detection_data:
            # Process all selections, not just 'selection'
            data_to_process = {
                k: v for k, v in detection_data.items()
                if k != "condition" and isinstance(v, (dict, list, str))
            }
        elif isinstance(detection_data, dict) and "selection" in detection_data:
            data_to_process = detection_data["selection"]
        else:
            data_to_process = detection_data

        keywords: List[str] = []
        phrases: List[str] = []

        def recurse(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    # Skip dict keys — they are Sigma field names (Image, CommandLine, etc.)
                    # NOT indicator values. We only want VALUES.
                    if isinstance(v, str):
                        if " " in v.strip() and len(v.strip()) > 3:
                            phrases.append(v.strip().lower())
                        keywords.extend(_tokenize(v))
                    else:
                        recurse(v)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, str):
                        if " " in item.strip() and len(item.strip()) > 3:
                            phrases.append(item.strip().lower())
                        keywords.extend(_tokenize(item))
                    else:
                        recurse(item)
            elif isinstance(obj, str):
                keywords.extend(_tokenize(obj))

        recurse(data_to_process)
        return list(set(keywords)), list(set(phrases))

    def find_candidates(self, query_tokens: Set[str]) -> Dict[int, int]:
        """Find candidate rules that share tokens with query."""
        candidates: Dict[int, int] = defaultdict(int)
        for token in query_tokens:
            if token in self.index:
                for rule_idx in self.index[token]:
                    candidates[rule_idx] += 1
        return candidates

    def compute_tfidf_score(self, rule_idx: int, query_tokens: Set[str]) -> float:
        """Compute TF-IDF relevance score for a rule against query tokens."""
        keywords = self.rule_keywords.get(rule_idx, [])
        if not keywords:
            return 0.0

        tf: Dict[str, int] = defaultdict(int)
        for kw in keywords:
            tf[kw.lower()] += 1

        score = 0.0
        max_tf = max(tf.values()) if tf else 1

        for token in query_tokens:
            token_lower = token.lower()
            if token_lower in tf:
                term_freq = 0.5 + 0.5 * (tf[token_lower] / max_tf)
                doc_freq = self.df.get(token_lower, 0)
                idf = math.log((self.doc_count + 1) / (doc_freq + 1)) + 1 if doc_freq > 0 else 1.0
                score += term_freq * idf

        return score / (len(keywords) + 1)


# ─── Index Cache ─────────────────────────────────────────────────────────────

_index_cache: Optional[SigmaIndex] = None
_index_cache_dir: Optional[str] = None


def _get_or_build_index(rules: List[dict], root_directory: str) -> SigmaIndex:
    global _index_cache, _index_cache_dir
    if _index_cache is not None and _index_cache_dir == root_directory:
        return _index_cache
    _index_cache = SigmaIndex(rules)
    _index_cache_dir = root_directory
    return _index_cache


# ─── Report Signal Extraction ────────────────────────────────────────────────

def gather_report_keywords(analysis_data: dict) -> Set[str]:
    """Extract tokens from IoC and TTP fields (backward compat)."""
    keywords: Set[str] = set()
    iocs = analysis_data.get("indicators_of_compromise", {})
    for key, value in iocs.items():
        if isinstance(value, list):
            for item in value:
                keywords |= _tokenize_lower(str(item))
        elif isinstance(value, str):
            keywords |= _tokenize_lower(value)

    for ttp in analysis_data.get("ttps", []):
        if isinstance(ttp, dict):
            for val in ttp.values():
                keywords |= _tokenize_lower(str(val))
        elif isinstance(ttp, str):
            keywords |= _tokenize_lower(ttp)

    for actor in analysis_data.get("threat_actors", []):
        keywords |= _tokenize_lower(str(actor))

    for tool in analysis_data.get("tools_or_malware", []):
        keywords |= _tokenize_lower(str(tool))

    return keywords


def gather_report_signals(analysis_data: dict, mitre_techniques: list = None) -> dict:
    """
    Extract multi-dimensional matching signals from analysis data.
    This is the heart of the new matching algorithm.
    """
    signals = {
        "techniques": set(),
        "ioc_types": {},
        "logsource_categories": set(),
        "keywords": set(),
        "ioc_values": set(),
    }

    # ── 1. Extract MITRE technique IDs ──
    # From TTPs in analysis_data
    ttps = analysis_data.get("ttps", [])
    for ttp in ttps:
        ttp_str = str(ttp).upper() if isinstance(ttp, str) else ""
        if isinstance(ttp, dict):
            ttp_str = " ".join(str(v).upper() for v in ttp.values())
        for m in re.finditer(r"T(\d{4}(?:\.\d{3})?)", ttp_str):
            tid = "t" + m.group(1).lower()
            signals["techniques"].add(tid)
            # Also add parent technique
            parent = tid.split(".")[0]
            if parent != tid:
                signals["techniques"].add(parent)

    # From mitre_techniques parameter (passed from pipeline)
    if mitre_techniques:
        for tech in mitre_techniques:
            if isinstance(tech, dict):
                tid_raw = tech.get("technique_id", "") or tech.get("id", "")
            elif isinstance(tech, str):
                tid_raw = tech
            else:
                continue
            for m in re.finditer(r"T(\d{4}(?:\.\d{3})?)", str(tid_raw).upper()):
                tid = "t" + m.group(1).lower()
                signals["techniques"].add(tid)
                parent = tid.split(".")[0]
                if parent != tid:
                    signals["techniques"].add(parent)

    # ── 2. Classify IoCs by type and derive logsource categories ──
    iocs = analysis_data.get("indicators_of_compromise", {})
    for ioc_type, indicators in iocs.items():
        if isinstance(indicators, list) and indicators:
            signals["ioc_types"][ioc_type] = indicators
            signals["ioc_values"].update(str(v).lower().strip() for v in indicators if v)
            if ioc_type in IOC_TO_LOGSOURCE:
                signals["logsource_categories"].update(IOC_TO_LOGSOURCE[ioc_type])

    # Also add tool/malware names as IoC values (they appear in detection blocks)
    for tool in analysis_data.get("tools_or_malware", []):
        if tool:
            signals["ioc_values"].add(str(tool).lower().strip())

    for actor in analysis_data.get("threat_actors", []):
        if actor:
            signals["ioc_values"].add(str(actor).lower().strip())

    # ── 3. Keywords (existing behavior) ──
    signals["keywords"] = gather_report_keywords(analysis_data)

    logger.info(
        f"Report signals: {len(signals['techniques'])} techniques, "
        f"{len(signals['ioc_values'])} IoC values, "
        f"{len(signals['logsource_categories'])} logsource cats, "
        f"{len(signals['keywords'])} keywords"
    )

    return signals


# ─── Fuzzy Match ─────────────────────────────────────────────────────────────

def _fuzzy_match(keyword: str, candidates: Set[str], threshold: float = 0.8) -> bool:
    kw_lower = keyword.lower()
    for candidate in candidates:
        if kw_lower == candidate:
            return True
        if len(kw_lower) >= 4 and kw_lower in candidate:
            return True
        if len(candidate) >= 4 and candidate in kw_lower:
            return True
        if abs(len(kw_lower) - len(candidate)) <= 2 and len(kw_lower) >= 4:
            common = sum(1 for a, b in zip(kw_lower, candidate) if a == b)
            ratio = common / max(len(kw_lower), len(candidate))
            if ratio >= threshold:
                return True
    return False


# ─── GitHub Link Builder ─────────────────────────────────────────────────────

def build_github_link(rule_info: dict) -> str:
    """
    Build correct SigmaHQ GitHub URL.
    Uses logsource metadata to derive the correct directory path.
    """
    rule_data = rule_info["rule_data"]
    filename = os.path.basename(rule_info["file_path"])

    # Method 1: Use logsource metadata (most reliable)
    logsource = rule_data.get("logsource", {})
    if isinstance(logsource, dict):
        category = logsource.get("category", "")
        product = logsource.get("product", "")
        if category and product:
            return f"{SIGMAHQ_BASE_URL}/rules/{product}/{category}/{filename}"

    # Method 2: Infer from filename prefix
    prefix_map = {
        "proc_creation_win_": "rules/windows/process_creation",
        "proc_creation_lnx_": "rules/linux/process_creation",
        "proc_creation_macos_": "rules/macos/process_creation",
        "dns_query_win_": "rules/windows/dns_query",
        "dns_query_": "rules/windows/dns_query",
        "net_connection_win_": "rules/windows/network_connection",
        "net_connection_": "rules/windows/network_connection",
        "registry_set_": "rules/windows/registry/registry_set",
        "registry_add_": "rules/windows/registry/registry_add",
        "registry_event_": "rules/windows/registry/registry_event",
        "registry_delete_": "rules/windows/registry/registry_delete",
        "file_event_": "rules/windows/file_event",
        "file_change_": "rules/windows/file_change",
        "file_access_": "rules/windows/file_access",
        "file_delete_": "rules/windows/file_delete",
        "file_rename_": "rules/windows/file_rename",
        "image_load_": "rules/windows/image_load",
        "driver_load_": "rules/windows/driver_load",
        "ps_classic_": "rules/windows/powershell/powershell_classic",
        "ps_module_": "rules/windows/powershell/powershell_module",
        "ps_script_": "rules/windows/powershell/powershell_script",
        "create_remote_thread_": "rules/windows/create_remote_thread",
        "pipe_created_": "rules/windows/pipe_created",
        "process_access_": "rules/windows/process_access",
        "wmi_event_": "rules/windows/wmi_event",
        "sysmon_": "rules/windows/sysmon",
        "cloud_": "rules/cloud",
        "web_": "rules/web",
    }
    for prefix, path in prefix_map.items():
        if filename.startswith(prefix):
            return f"{SIGMAHQ_BASE_URL}/{path}/{filename}"

    # Fallback: assume Windows process creation
    return f"{SIGMAHQ_BASE_URL}/rules/windows/process_creation/{filename}"


# ─── Multi-Signal Matching Engine ────────────────────────────────────────────

def _compute_ioc_field_score(
    index: SigmaIndex,
    rule_idx: int,
    ioc_values: Set[str],
) -> Tuple[float, List[str]]:
    """
    Check how many IoC values appear in the rule's detection keywords/phrases.
    Returns (score 0-1, list_of_matched_ioc_values).
    """
    if not ioc_values:
        return 0.0, []

    rule_kws = set(kw.lower() for kw in index.rule_keywords.get(rule_idx, []))
    rule_phrases = set(index.rule_phrases.get(rule_idx, []))
    all_detection = rule_kws | rule_phrases

    if not all_detection:
        return 0.0, []

    matched_iocs: List[str] = []
    for ioc_val in ioc_values:
        if not ioc_val or len(ioc_val) < 3:
            continue
        for det_term in all_detection:
            if ioc_val in det_term or det_term in ioc_val:
                matched_iocs.append(ioc_val)
                break

    if not matched_iocs:
        return 0.0, []

    # Even 1-2 IoC value matches in a rule is highly significant
    score = min(1.0, len(matched_iocs) / max(1, min(len(ioc_values), 5)))
    return score, matched_iocs


def match_sigma_rules_with_report(
    sigma_rules: List[dict],
    analysis_data: dict,
    report_text: str,
    root_directory: str,
    mitre_techniques: list = None,
    sigma_repo_path: str = "",       # kept for backward compat, ignored
    threshold: float = 25.0,
    max_results: int = 15,
    use_fuzzy: bool = True,
) -> List[dict]:
    """
    Multi-signal Sigma rule matching engine.

    Scoring Pipeline:
      Stage 1: MITRE ATT&CK technique match (40% weight)
      Stage 2: IoC-type → logsource routing (15% weight)
      Stage 3: IoC value match in detection block (25% weight)
      Stage 4: Keyword / TF-IDF match (20% weight)
      Stage 5: Quality filter + score combination

    Returns:
        Sorted list of high-confidence matching rules with metadata
    """
    # Extract multi-dimensional signals
    signals = gather_report_signals(analysis_data, mitre_techniques)

    # Fallback: if no structured signals, use raw text
    if not signals["keywords"] and report_text:
        raw_tokens = _tokenize_lower(report_text)
        signals["keywords"] = {t for t in raw_tokens if len(t) >= 4}
        if len(signals["keywords"]) > 500:
            signals["keywords"] = set(list(signals["keywords"])[:500])

    if not signals["keywords"] and not signals["techniques"] and not signals["ioc_values"]:
        logger.warning("No report signals extracted, skipping matching")
        return []

    # Build or retrieve index
    index = _get_or_build_index(sigma_rules, root_directory)

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 1: MITRE Technique Match — highest precision signal
    # ═══════════════════════════════════════════════════════════════════════
    technique_matches: Dict[int, Set[str]] = defaultdict(set)
    for technique_id in signals["techniques"]:
        if technique_id in index.technique_index:
            for rule_idx in index.technique_index[technique_id]:
                technique_matches[rule_idx].add(technique_id)

    logger.info(f"Stage 1 (MITRE): {len(technique_matches)} rules matched via techniques")

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 2: IoC-Type → Logsource Routing
    # ═══════════════════════════════════════════════════════════════════════
    logsource_relevant: Set[int] = set()
    for category in signals["logsource_categories"]:
        for ls_key in index.logsource_index:
            if category in ls_key:
                logsource_relevant.update(index.logsource_index[ls_key])

    logger.info(f"Stage 2 (Logsource): {len(logsource_relevant)} rules via IoC-type routing")

    # ═══════════════════════════════════════════════════════════════════════
    # STAGE 4: Keyword / TF-IDF candidates (run before stage 3 to build candidate set)
    # ═══════════════════════════════════════════════════════════════════════
    keyword_candidates = index.find_candidates(signals["keywords"]) if signals["keywords"] else {}

    logger.info(f"Stage 4 (Keywords): {len(keyword_candidates)} keyword candidates")

    # ═══════════════════════════════════════════════════════════════════════
    # COMBINE CANDIDATES from all stages
    # ═══════════════════════════════════════════════════════════════════════
    all_candidates = set(technique_matches.keys()) | logsource_relevant | set(keyword_candidates.keys())
    logger.info(f"Total unique candidates: {len(all_candidates)}")

    # ═══════════════════════════════════════════════════════════════════════
    # SCORE each candidate
    # ═══════════════════════════════════════════════════════════════════════
    results = []

    for rule_idx in all_candidates:
        rule_info = index.rules[rule_idx]
        rule_data = rule_info["rule_data"]

        # ── MITRE score (0 or 1) ──
        mitre_score = 1.0 if rule_idx in technique_matches else 0.0
        mitre_matched = sorted(technique_matches.get(rule_idx, set()))

        # ── Logsource score (0 or 1) ──
        logsource_score = 1.0 if rule_idx in logsource_relevant else 0.0

        # ── IoC field value match score (0 to 1) ──
        ioc_score, ioc_matched_values = _compute_ioc_field_score(
            index, rule_idx, signals["ioc_values"]
        )

        # ── Keyword / TF-IDF score (0 to 1) ──
        keyword_score = 0.0
        matched_keywords: Set[str] = set()
        phrase_matches: List[str] = []

        keywords = index.rule_keywords.get(rule_idx, [])
        phrases = index.rule_phrases.get(rule_idx, [])

        if keywords or phrases:
            # Keyword matching
            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in signals["keywords"]:
                    matched_keywords.add(kw_lower)
                elif use_fuzzy and _fuzzy_match(kw_lower, signals["keywords"]):
                    matched_keywords.add(kw_lower)

            # Phrase matching
            for phrase in phrases:
                if phrase in report_text:
                    phrase_matches.append(phrase)
                    matched_keywords.add(phrase)

            total_terms = len(set(kw.lower() for kw in keywords)) + len(phrases)
            if total_terms > 0:
                match_ratio = len(matched_keywords) / total_terms
                tfidf = index.compute_tfidf_score(rule_idx, signals["keywords"])
                keyword_score = (match_ratio * 0.5) + (min(tfidf, 1.0) * 0.5)

        # ═══ COMBINED SCORE (0-100) ═══
        raw_score = (
            mitre_score * 40 +
            ioc_score * 25 +
            logsource_score * 15 +
            keyword_score * 20
        )

        # Quality multiplier
        status = index.rule_status.get(rule_idx, "experimental")
        quality_mult = {"stable": 1.15, "test": 1.0, "experimental": 0.85}.get(status, 1.0)

        combined_score = raw_score * quality_mult

        # Cap at 100
        combined_score = min(100.0, combined_score)

        # ── Threshold filter ──
        if combined_score < threshold:
            continue

        # Filter out sigma field names from matched_keywords for display
        display_keywords = {kw for kw in matched_keywords if not _is_sigma_field_name(kw)}

        # Minimum 3 displayable keyword matches required for ANY result
        if len(display_keywords) < 3:
            continue

        # ── Confidence label ──
        if combined_score >= 80:
            confidence = "Direct Hit"
        elif combined_score >= 60:
            confidence = "Strong Match"
        elif combined_score >= 40:
            confidence = "Relevant"
        else:
            confidence = "Related"

        # ── GitHub link ──
        github_link = build_github_link(rule_info)

        level = index.rule_level.get(rule_idx, "medium")

        results.append({
            "id": rule_data.get("id", "unknown"),
            "title": rule_data.get("title", "Untitled Sigma Rule"),
            "description": rule_data.get("description", ""),
            "level": level,
            "status": status,
            "match_ratio": round(combined_score, 2),
            "combined_score": round(combined_score, 2),
            "confidence": confidence,
            "mitre_matched": mitre_matched,
            "logsource": index.rule_logsource.get(rule_idx, {}),
            "matched_keywords": sorted(display_keywords),
            "phrase_matches": phrase_matches,
            "tags": rule_data.get("tags", []),
            "github_link": github_link,
            "score_breakdown": {
                "mitre": round(mitre_score * 40, 1),
                "ioc_field": round(ioc_score * 25, 1),
                "logsource": round(logsource_score * 15, 1),
                "keyword": round(keyword_score * 20, 1),
            },
        })

    # Sort by combined score descending
    results.sort(key=lambda x: x["combined_score"], reverse=True)

    # Deduplicate by rule ID
    seen_ids: Set[str] = set()
    deduped: List[dict] = []
    for r in results:
        if r["id"] not in seen_ids:
            seen_ids.add(r["id"])
            deduped.append(r)

    logger.info(
        f"Sigma matching complete: {len(deduped)} rules matched (returning top {max_results})"
    )
    return deduped[:max_results]
