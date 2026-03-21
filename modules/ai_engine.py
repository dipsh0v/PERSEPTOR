"""
PERSEPTOR v2.0 - AI Engine
Multi-provider threat analysis with CoT prompting, output validation, and caching.
"""

import json
import logging
import os
import re
from typing import Optional
from modules.ai.base_provider import AIProvider, Message
from modules.ai.provider_factory import get_provider
from modules.ai.retry_handler import with_retry
from modules.prompts.templates import PromptTemplates
from modules.prompts.few_shot import FewShotExamples
from modules.pipeline.output_validator import OutputValidator
from modules.pipeline.cache import get_cache, ResponseCache
from modules.logging_config import get_logger

logger = get_logger("ai_engine")

# Prompt version — increment when prompts change to invalidate cached results
PROMPT_VERSION = "v2.1"


################################################################################
# Token Usage Tracking
################################################################################

def _track_usage(response, endpoint: str = "unknown"):
    """Record AI token usage to the database for the Usage dashboard."""
    try:
        from modules.database import TokenUsageRepository
        if response and hasattr(response, 'usage') and response.usage:
            TokenUsageRepository.record({
                "session_id": None,  # will be enriched if session context available
                "provider": getattr(response, 'provider', 'unknown'),
                "model": getattr(response, 'model', 'unknown'),
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "endpoint": endpoint,
                "latency_ms": getattr(response, 'latency_ms', 0),
            })
    except Exception as e:
        logger.debug(f"Token usage tracking failed (non-critical): {e}")


################################################################################
# Utility Functions
################################################################################

def safe_json_parse(json_str: str) -> dict:
    """Safely parse a JSON string, returning a dictionary or empty {} on error."""
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"JSON parse error: {e}")
        return {}


def extract_json_from_response(text: str) -> str:
    """Extract JSON from an AI response that may contain markdown code blocks."""
    text = text.strip()

    # Handle ```json or ```JSON (case-insensitive) with optional whitespace
    fence_match = re.search(r'```\s*[jJ][sS][oO][nN]\s*\n', text)
    if fence_match:
        start = fence_match.end()
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
        return text[start:].strip()

    # Handle generic ``` code blocks
    if "```" in text:
        start = text.find("```") + 3
        # Skip language identifier on the same line (e.g., ```python)
        newline_pos = text.find("\n", start)
        if newline_pos != -1 and newline_pos - start < 20:
            start = newline_pos + 1
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
        return text[start:].strip()

    # Try to find JSON object
    json_start = text.find("{")
    json_end = text.rfind("}") + 1
    if json_start != -1 and json_end > json_start:
        return text[json_start:json_end]

    # Try to find JSON array
    arr_start = text.find("[")
    arr_end = text.rfind("]") + 1
    if arr_start != -1 and arr_end > arr_start:
        return text[arr_start:arr_end]

    return text


################################################################################
# Provider Resolution (backward compatibility)
################################################################################

def _resolve_provider(
    provider: Optional[AIProvider] = None,
    openai_api_key: str = "",
    provider_name: str = "openai",
    model_name: Optional[str] = None,
) -> AIProvider:
    """Resolve an AIProvider from various input patterns."""
    if provider is not None:
        return provider

    if openai_api_key:
        if openai_api_key.startswith("sk-ant-"):
            provider_name = "anthropic"
        elif openai_api_key.startswith("AIza"):
            provider_name = "google"
        else:
            provider_name = "openai"

    return get_provider(
        provider_name=provider_name,
        api_key=openai_api_key,
        model=model_name,
    )


################################################################################
# Summarize Threat Report (CoT)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def summarize_threat_report(
    text: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> str:
    """Summarize threat report using Chain-of-Thought prompting."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("summarize", PROMPT_VERSION, text[:500], provider_name, model_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached threat summary")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.THREAT_ANALYST_SYSTEM),
            Message(role="user", content=PromptTemplates.THREAT_SUMMARY_COT.format(text=text)),
        ]

        logger.info(f"Generating threat summary using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "summarize_threat_report")
        result = response.content.strip()

        cache.set(cache_key, result)
        logger.info(
            f"Threat summary generated",
            extra={"provider": ai.provider_name, "model": response.model, "tokens": response.usage.total_tokens},
        )
        return result

    except Exception as e:
        logger.error(f"Error summarizing threat report: {e}", exc_info=True)
        return "Could not generate threat summary."


################################################################################
# Extract IoCs and TTPs (CoT + Few-Shot + Validation)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def extract_iocs_ttps_gpt(
    text: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
):
    """Extract IoCs and TTPs with CoT prompting and output validation."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("ioc_extract", PROMPT_VERSION, text[:500], provider_name, model_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached IoC extraction")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.IOC_EXTRACTOR_SYSTEM),
            # Direct CoT extraction — no few-shot to avoid IoC contamination
            Message(role="user", content=PromptTemplates.IOC_EXTRACTION_COT.format(text=text)),
        ]

        logger.info(f"Extracting IoCs/TTPs using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "extract_iocs_ttps")

        raw_content = response.content
        logger.info(f"IoC raw response length: {len(raw_content)}, first 500: {raw_content[:500]}")

        # Dump raw response only when DEBUG logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            try:
                debug_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "ioc_raw_response.txt")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(raw_content)
                logger.debug(f"Raw IoC response dumped to {debug_path} ({len(raw_content)} bytes)")
            except Exception as dump_err:
                logger.debug(f"Failed to dump raw response: {dump_err}")

        # Extract JSON from response (handles thinking blocks, markdown, etc.)
        cleaned = extract_json_from_response(raw_content)

        # Validate and repair output
        parsed_ok = False
        is_valid, parsed = OutputValidator.validate_json(cleaned)
        if is_valid and isinstance(parsed, dict):
            _, validated, warnings = OutputValidator.validate_ioc_response(parsed)
            if warnings:
                logger.warning(f"IoC validation warnings: {warnings}")
            result = json.dumps(validated)
            parsed_ok = True
        else:
            # Second attempt: try the full raw content directly
            is_valid2, parsed2 = OutputValidator.validate_json(raw_content)
            if is_valid2 and isinstance(parsed2, dict):
                _, validated2, warnings2 = OutputValidator.validate_ioc_response(parsed2)
                result = json.dumps(validated2)
                parsed_ok = True
                logger.info("IoC extraction: second-pass JSON parse succeeded")
            else:
                logger.warning(f"IoC extraction returned invalid JSON. Cleaned first 300: {cleaned[:300]}")
                result = "{}"  # Return empty JSON, not raw text

        # ── Anti-hallucination: cross-check extracted data against source text ──
        if parsed_ok:
            try:
                parsed_result = json.loads(result) if isinstance(result, str) else result
                text_lower = text.lower()
                hallucination_warnings = []

                # Cross-check threat_actors FIRST (needed for tools dedup)
                original_actors = parsed_result.get("threat_actors", [])
                verified_actors = []
                for actor in original_actors:
                    actor_str = str(actor).strip()
                    if actor_str.lower() in text_lower:
                        verified_actors.append(actor_str)
                    else:
                        hallucination_warnings.append(f"threat_actor '{actor_str}' NOT in source text — removed")
                parsed_result["threat_actors"] = verified_actors
                actors_lower = {a.lower() for a in verified_actors}

                # Cross-check tools_or_malware — each must appear in source text
                # AND must NOT be a threat actor name (AI often confuses the two)
                original_tools = parsed_result.get("tools_or_malware", [])
                verified_tools = []
                for tool in original_tools:
                    tool_str = str(tool).strip()
                    if tool_str.lower() in actors_lower:
                        hallucination_warnings.append(f"tools_or_malware '{tool_str}' is a threat actor — removed")
                        continue
                    if tool_str.lower() in text_lower:
                        verified_tools.append(tool_str)
                    else:
                        hallucination_warnings.append(f"tools_or_malware '{tool_str}' NOT in source text — removed")
                parsed_result["tools_or_malware"] = verified_tools

                # Cross-check file_hashes — each must appear in source text
                ioc = parsed_result.get("indicators_of_compromise", {})
                original_hashes = ioc.get("file_hashes", [])
                verified_hashes = []
                for h in original_hashes:
                    h_str = str(h).strip()
                    if h_str.lower() in text_lower:
                        verified_hashes.append(h_str)
                    else:
                        hallucination_warnings.append(f"file_hash '{h_str[:20]}...' NOT in source text — removed")
                ioc["file_hashes"] = verified_hashes

                # Cross-check domains — each must appear in source text
                original_domains = ioc.get("domains", [])
                verified_domains = []
                for d in original_domains:
                    d_str = str(d).strip()
                    if d_str.lower() in text_lower:
                        verified_domains.append(d_str)
                    else:
                        hallucination_warnings.append(f"domain '{d_str}' NOT in source text — removed")
                ioc["domains"] = verified_domains

                # Cross-check IPs
                original_ips = ioc.get("ips", [])
                verified_ips = []
                for ip in original_ips:
                    ip_str = str(ip).strip()
                    # Also check defanged versions
                    if ip_str in text or ip_str.replace('.', '[.]') in text:
                        verified_ips.append(ip_str)
                    else:
                        hallucination_warnings.append(f"ip '{ip_str}' NOT in source text — removed")
                ioc["ips"] = verified_ips

                # Cross-check URLs
                original_urls = ioc.get("urls", [])
                verified_urls = []
                for u in original_urls:
                    u_str = str(u).strip()
                    # Check both original and defanged forms
                    u_check = u_str.replace('http://', '').replace('https://', '').split('/')[0]
                    if u_check.lower() in text_lower or u_str.lower() in text_lower:
                        verified_urls.append(u_str)
                    else:
                        hallucination_warnings.append(f"url domain NOT in source text — removed")
                ioc["urls"] = verified_urls

                parsed_result["indicators_of_compromise"] = ioc

                if hallucination_warnings:
                    logger.warning(
                        f"Anti-hallucination filter removed {len(hallucination_warnings)} items: "
                        + "; ".join(hallucination_warnings[:10])
                    )

                # ── Auto-extract tools_or_malware if AI missed them ──────────
                # Scan the source text for common malware/tool patterns
                if not parsed_result.get("tools_or_malware"):
                    logger.info("tools_or_malware empty — running text-based extraction fallback")
                    # Known malware/tool naming patterns: CamelCase words, words with "Loader",
                    # "Backdoor", "RAT", "Dropper", "Stealer" suffixes, etc.
                    import re as _re
                    # Extract capitalized compound words that look like malware names
                    # Pattern: Words like ShadowPad, CobaltStrike, SpyderLoader, RPipeCommander
                    candidates = set()

                    # Pattern 1: CamelCase or compound names (2+ capital letters in a word)
                    for m in _re.finditer(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', text):
                        candidates.add(m.group(1))

                    # Pattern 2: Known suffixes for tools/malware
                    tool_suffixes = [
                        r'(?:Loader|Backdoor|RAT|Dropper|Stealer|Implant|Beacon|Agent|'
                        r'Commander|Injector|Downloader|Rootkit|Wiper|Ransomware|Trojan|'
                        r'Keylogger|Exploit|Payload|Shell|Miner|Botnet|Proxy|Tunnel)'
                    ]
                    for suffix_pat in tool_suffixes:
                        for m in _re.finditer(r'\b(\w+' + suffix_pat + r')\b', text):
                            candidates.add(m.group(1))

                    # Pattern 3: Known malware names commonly seen in threat reports
                    known_malware = [
                        'ShadowPad', 'Cobalt Strike', 'Mimikatz', 'Metasploit',
                        'PlugX', 'Spyder', 'RPipeCommander', 'ScatterBee',
                        'NightDoor', 'Brute Ratel', 'Sliver', 'SodaMaster',
                        'IcedID', 'QakBot', 'Emotet', 'TrickBot', 'BazarLoader',
                        'Beacon', 'Meterpreter', 'BloodHound', 'Rubeus',
                        'SharpHound', 'LaZagne', 'PsExec', 'WinPEAS',
                        'LinPEAS', 'Chisel', 'Ngrok', 'Impacket',
                        'DynoWiper', 'PromptSpy', 'MiniDump',
                    ]
                    for name in known_malware:
                        if name.lower() in text_lower:
                            candidates.add(name)

                    # Filter: must appear at least twice in text (reduces noise)
                    # and must not be a known threat actor group name
                    known_actors_lower = {a.lower() for a in parsed_result.get("threat_actors", [])}
                    # Also exclude campaign names (they go in "campaigns", not tools)
                    known_campaigns_lower = {c.lower() for c in parsed_result.get("campaigns", [])}
                    # Common non-malware words and security vendor names to exclude
                    exclude_lower = {
                        # Generic words
                        'microsoft', 'windows', 'linux', 'google', 'facebook',
                        'twitter', 'github', 'figure', 'table', 'overview',
                        'appendix', 'references', 'conclusion', 'background',
                        'however', 'moreover', 'furthermore', 'therefore',
                        'indicators', 'compromise', 'research', 'attribution',
                        'javascript', 'powershell', 'typescript', 'dockerfile',
                        # Abbreviations that aren't tools
                        'iocs', 'ttps', 'cves', 'apts',
                        # Security vendors (not malware)
                        'sentinelone', 'crowdstrike', 'mandiant', 'fireeye',
                        'kaspersky', 'symantec', 'mcafee', 'trendmicro',
                        'paloalto', 'fortinet', 'checkpoint', 'sophos',
                        'bitdefender', 'carbonblack', 'cylance', 'webroot',
                        'malwarebytes', 'avast', 'norton', 'eset',
                        # Common non-tool CamelCase words
                        'youtube', 'linkedin', 'facebook', 'stackoverflow',
                        'wordpress', 'outlook', 'onedrive', 'sharepoint',
                        'virustotal', 'hybridanalysis', 'anyrun',
                    }

                    extracted_tools = []
                    for candidate in candidates:
                        c_lower = candidate.lower()
                        if c_lower in known_actors_lower:
                            continue
                        if c_lower in known_campaigns_lower:
                            continue
                        if c_lower in exclude_lower:
                            continue
                        if len(candidate) < 3:
                            continue
                        # Must appear in text (already guaranteed by regex, but double-check)
                        occurrences = text_lower.count(c_lower)
                        if occurrences >= 2:
                            extracted_tools.append(candidate)

                    if extracted_tools:
                        parsed_result["tools_or_malware"] = extracted_tools
                        logger.info(f"Text-based extraction found {len(extracted_tools)} tools/malware: {extracted_tools}")

                result = json.dumps(parsed_result)
            except Exception as halluc_err:
                logger.warning(f"Anti-hallucination check failed (non-critical): {halluc_err}")

        # ── Sparse result retry ───────────────────────────────────────
        # If the AI returned very few IoCs despite a long article, retry
        # with a simplified, extraction-focused prompt (no restrictive rules)
        if parsed_ok and len(text) > 2000:
            try:
                parsed_result = json.loads(result) if isinstance(result, str) else result
                ioc = parsed_result.get("indicators_of_compromise", {})
                total_iocs = sum(len(v) for v in ioc.values() if isinstance(v, list))
                total_ttps = len(parsed_result.get("ttps", []))

                if total_iocs + total_ttps < 5:
                    logger.warning(
                        f"Sparse IoC result ({total_iocs} IoCs, {total_ttps} TTPs) from "
                        f"{len(text)} char article. Retrying with simplified extraction prompt."
                    )
                    # Use a DIFFERENT, simpler prompt — no few-shot, no restrictive rules
                    retry_prompt = (
                        "Extract EVERY indicator of compromise and MITRE ATT&CK technique from this threat report.\n"
                        "Be exhaustive. Include ALL: IP addresses, domains, URLs, email addresses, "
                        "file hashes (MD5/SHA1/SHA256), filenames, file paths, registry keys, "
                        "process names, command-line strings, and behavioral TTPs.\n"
                        "Include tools/malware names, threat actor names, CVEs, and campaigns.\n"
                        "For TTPs, map EVERY observed behavior to the most specific MITRE technique.\n\n"
                        "Return ONLY valid JSON with this structure:\n"
                        '{"sigma_title":"...","sigma_description":"...",'
                        '"indicators_of_compromise":{"ips":[],"domains":[],"urls":[],"email_addresses":[],'
                        '"file_hashes":[],"filenames":[],"registry_keys":[],"process_names":[],"malicious_commands":[]},'
                        '"ttps":[{"mitre_id":"TXXXX.XXX","technique_name":"","tactic":"","description":""}],'
                        '"suspicious_patterns":[],"process_chains":[],"cves":[],'
                        '"tools_or_malware":[],"threat_actors":[],"campaigns":[],'
                        '"malicious_execution_chains":[],"image_based_indicators":[],'
                        '"obfuscations_refanged":[],"confidence_level":"high/medium/low","notes":""}\n\n'
                        "THREAT REPORT:\n" + text
                    )
                    retry_messages = [
                        Message(role="system", content=(
                            "You are a threat intelligence IoC extraction engine. "
                            "Extract ALL indicators exhaustively. Output valid JSON only."
                        )),
                        Message(role="user", content=retry_prompt),
                    ]
                    retry_response = ai.generate(retry_messages, temperature=0.2)
                    _track_usage(retry_response, "extract_iocs_ttps_retry")

                    retry_cleaned = extract_json_from_response(retry_response.content)
                    retry_valid, retry_parsed = OutputValidator.validate_json(retry_cleaned)
                    if retry_valid and isinstance(retry_parsed, dict):
                        retry_ioc = retry_parsed.get("indicators_of_compromise", {})
                        retry_total = sum(len(v) for v in retry_ioc.values() if isinstance(v, list))
                        retry_ttps = len(retry_parsed.get("ttps", []))

                        if retry_total + retry_ttps > total_iocs + total_ttps:
                            _, retry_validated, _ = OutputValidator.validate_ioc_response(retry_parsed)
                            result = json.dumps(retry_validated)
                            logger.info(
                                f"Retry improved results: {retry_total} IoCs, {retry_ttps} TTPs "
                                f"(was {total_iocs} IoCs, {total_ttps} TTPs)"
                            )
                        else:
                            logger.info("Retry did not improve results, keeping original")
            except Exception as retry_err:
                logger.warning(f"Sparse result retry failed (non-critical): {retry_err}")

        # Only cache successfully parsed results
        if parsed_ok:
            cache.set(cache_key, result)
        logger.info(
            f"IoC/TTP extraction complete",
            extra={"provider": ai.provider_name, "model": response.model, "tokens": response.usage.total_tokens},
        )
        return result

    except Exception as e:
        logger.error(f"Error in IoC/TTP extraction: {e}", exc_info=True)
        return "{}"


################################################################################
# Refine Sigma Queries
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def refine_sigma_queries_with_gpt(
    sigma_yaml: str,
    splunk_queries: list,
    qradar_queries: list,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "medium",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
):
    """Refine Sigma rules and SIEM queries."""
    try:
        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)
        splunk_str = "\n".join(splunk_queries) if splunk_queries else "(No Splunk Queries)"
        qradar_str = "\n".join(qradar_queries) if qradar_queries else "(No QRadar Queries)"

        messages = [
            Message(role="system", content=PromptTemplates.SIEM_SPECIALIST_SYSTEM),
            Message(role="user", content=f"""Review and refine the following detection rules and queries.

REFINEMENT GOALS:
1. Fix any syntax errors in the Sigma rule
2. Optimize Splunk queries for search performance
3. Ensure QRadar AQL uses correct property names
4. Add missing detection fields or conditions
5. Reduce false positive potential

Output in plain text with these sections:
1) Refined Sigma Rule (valid YAML)
2) Refined Splunk Queries (valid SPL)
3) Refined QRadar Queries (valid AQL)

Sigma YAML:
{sigma_yaml}

Splunk queries:
{splunk_str}

QRadar queries:
{qradar_str}"""),
        ]

        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "mitre_mapping")
        return response.content.strip()

    except Exception as e:
        logger.error(f"Error refining queries: {e}", exc_info=True)
        return "Error refining output."


################################################################################
# Generate Sigma Rules (CoT + Few-Shot)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def generate_more_sigma_rules_from_article(
    article_text: str,
    images_ocr_text: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> str:
    """Generate Sigma rules with CoT prompting and few-shot examples."""
    try:
        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.DETECTION_ENGINEER_SYSTEM),
            # Few-shot example
            Message(role="user", content="Generate a Sigma rule for PowerShell download-and-execute behavior"),
            Message(role="assistant", content=FewShotExamples.SIGMA_RULE_EXAMPLE),
            # Actual request with CoT
            Message(role="user", content=PromptTemplates.SIGMA_GENERATION_COT.format(
                article_text=article_text,
                images_ocr_text=images_ocr_text,
            )),
        ]

        logger.info(f"Generating Sigma rules from article using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "generate_sigma_rules")
        result = response.content.strip()

        # Validate Sigma output
        is_valid, warnings = OutputValidator.validate_sigma_yaml(result)
        if warnings:
            logger.warning(f"Sigma validation warnings: {warnings}")

        return result

    except Exception as e:
        logger.error(f"Error generating Sigma rules: {e}", exc_info=True)
        return "Error generating extra Sigma rules."


################################################################################
# Convert Sigma to SIEM Queries (CoT + Few-Shot + Validation)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def convert_sigma_to_siem_queries(
    sigma_rules: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> dict:
    """Convert Sigma rules to SIEM queries with validation."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("siem_convert", PROMPT_VERSION, sigma_rules[:500], provider_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached SIEM queries")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.SIEM_SPECIALIST_SYSTEM),
            # Few-shot example
            Message(role="user", content="Convert this Sigma rule to SIEM queries: PowerShell download and execute detection"),
            Message(role="assistant", content=FewShotExamples.SIEM_QUERY_EXAMPLE),
            # Actual request with CoT
            Message(role="user", content=PromptTemplates.SIEM_CONVERSION_COT.format(sigma_rules=sigma_rules)),
        ]

        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "convert_siem_queries")

        # Strip markdown code fences before JSON parsing
        cleaned_content = extract_json_from_response(response.content)

        # Validate and repair output
        is_valid, parsed = OutputValidator.validate_json(cleaned_content)
        if is_valid and isinstance(parsed, dict):
            _, validated, warnings = OutputValidator.validate_siem_response(parsed)
            if warnings:
                logger.warning(f"SIEM validation warnings: {warnings}")
            siem_queries = validated
        else:
            logger.warning("SIEM conversion returned invalid JSON, using fallback")
            siem_queries = create_fallback_siem_queries(sigma_rules)

        cache.set(cache_key, siem_queries)
        logger.info(
            f"SIEM query conversion complete",
            extra={"provider": ai.provider_name, "model": response.model},
        )
        return siem_queries

    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error in SIEM conversion: {e}")
        return create_fallback_siem_queries(sigma_rules)
    except Exception as e:
        logger.error(f"Error converting Sigma to SIEM: {e}", exc_info=True)
        return create_fallback_siem_queries(sigma_rules)


################################################################################
# Generate Atomic Red Team Test Scenarios
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def generate_atomic_tests_from_sigma(
    sigma_rules: str,
    threat_context: str = "",
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> list:
    """Generate Atomic Red Team test scenarios for each Sigma rule."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("atomic_tests", PROMPT_VERSION, sigma_rules[:500], provider_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached atomic tests")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        # Build threat context summary (truncate to avoid token overflow)
        ctx = threat_context[:3000] if threat_context else "No additional threat context available."

        messages = [
            Message(role="system", content=PromptTemplates.ATOMIC_TEST_ENGINEER_SYSTEM),
            # Few-shot example
            Message(role="user", content="Generate an atomic test scenario for a Sigma rule detecting PowerShell download and execute behavior"),
            Message(role="assistant", content=FewShotExamples.ATOMIC_TEST_EXAMPLE),
            # Actual request with CoT
            Message(role="user", content=PromptTemplates.ATOMIC_TEST_GENERATION_COT.format(
                sigma_rules=sigma_rules,
                threat_context=ctx,
            )),
        ]

        logger.info(f"Generating atomic test scenarios using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "generate_atomic_tests")

        # Parse JSON array from response
        raw_content = response.content
        cleaned = extract_json_from_response(raw_content)

        # Try to parse as JSON array
        is_valid, parsed = OutputValidator.validate_json(cleaned)
        if is_valid and isinstance(parsed, list):
            cache.set(cache_key, parsed)
            logger.info(f"Generated {len(parsed)} atomic test scenarios")
            return parsed

        # Fallback: try wrapping in array
        if is_valid and isinstance(parsed, dict):
            result = [parsed]
            cache.set(cache_key, result)
            logger.info("Generated 1 atomic test scenario (wrapped)")
            return result

        # Second attempt on raw content
        is_valid2, parsed2 = OutputValidator.validate_json(raw_content)
        if is_valid2 and isinstance(parsed2, list):
            cache.set(cache_key, parsed2)
            return parsed2

        # Handle "Extra data" — AI returned multiple JSON objects/arrays concatenated
        # Try to find and parse the first complete JSON array [...] in the response
        import re as _re
        bracket_start = cleaned.find('[')
        if bracket_start >= 0:
            depth = 0
            for ci in range(bracket_start, len(cleaned)):
                if cleaned[ci] == '[':
                    depth += 1
                elif cleaned[ci] == ']':
                    depth -= 1
                    if depth == 0:
                        candidate = cleaned[bracket_start:ci+1]
                        try:
                            result = json.loads(candidate)
                            if isinstance(result, list):
                                cache.set(cache_key, result)
                                logger.info(f"Generated {len(result)} atomic tests (bracket extraction)")
                                return result
                        except json.JSONDecodeError:
                            pass
                        break

        # Try fixing common JSON issues: trailing commas, etc.
        try:
            fixed = _re.sub(r',\s*([}\]])', r'\1', cleaned)
            result = json.loads(fixed)
            if isinstance(result, list):
                cache.set(cache_key, result)
                logger.info(f"Generated {len(result)} atomic tests (fixed JSON)")
                return result
        except json.JSONDecodeError:
            pass

        logger.warning(f"Atomic test generation returned invalid JSON. First 300 chars: {cleaned[:300]}")
        return []

    except Exception as e:
        logger.error(f"Error generating atomic tests: {e}", exc_info=True)
        return []


################################################################################
# Generate Threat Hunting Queries
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def generate_threat_hunting_queries(
    threat_summary: str,
    ttps_summary: str,
    iocs_summary: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> dict:
    """Generate comprehensive behavior-based threat hunting queries for each SIEM platform."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("hunting", PROMPT_VERSION, threat_summary[:300], provider_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached hunting queries")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.THREAT_HUNTING_SYSTEM),
            Message(role="user", content=PromptTemplates.THREAT_HUNTING_GENERATION_COT.format(
                threat_summary=threat_summary[:2000],
                ttps_summary=ttps_summary[:1500],
                iocs_summary=iocs_summary[:1500],
            )),
        ]

        logger.info(f"Generating threat hunting queries using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "generate_hunting_queries")

        cleaned = extract_json_from_response(response.content)
        is_valid, parsed = OutputValidator.validate_json(cleaned)

        if is_valid and isinstance(parsed, dict):
            cache.set(cache_key, parsed)
            logger.info("Threat hunting queries generated successfully")
            return parsed

        logger.warning("Hunting query generation returned invalid JSON")
        return {}

    except Exception as e:
        logger.error(f"Error generating hunting queries: {e}", exc_info=True)
        return {}


def create_fallback_siem_queries(sigma_rules: str) -> dict:
    """Create basic SIEM queries as fallback when AI conversion fails."""
    try:
        rules_text = sigma_rules.lower()

        splunk_query = "index=* "
        if "process" in rules_text:
            splunk_query += '| search ProcessName=* '
        if "command" in rules_text:
            splunk_query += '| search CommandLine=* '
        if "file" in rules_text:
            splunk_query += '| search FileName=* '

        qradar_query = "SELECT * FROM events WHERE "
        conditions = []
        if "process" in rules_text:
            conditions.append("processname IS NOT NULL")
        if "command" in rules_text:
            conditions.append("commandline IS NOT NULL")
        qradar_query += " AND ".join(conditions) if conditions else "1=1"

        elastic_query = {"query": {"bool": {"must": []}}}
        if "process" in rules_text:
            elastic_query["query"]["bool"]["must"].append({"exists": {"field": "process.name"}})
        if "command" in rules_text:
            elastic_query["query"]["bool"]["must"].append({"exists": {"field": "process.command_line"}})

        sentinel_query = "SecurityEvent | where "
        s_conditions = []
        if "process" in rules_text:
            s_conditions.append('ProcessName contains ""')
        if "command" in rules_text:
            s_conditions.append('CommandLine contains ""')
        sentinel_query += " and ".join(s_conditions) if s_conditions else "1=1"

        fallback_note = "Basic fallback query. Please customize for your environment."
        return {
            "splunk": {"description": "Splunk SPL (fallback)", "query": splunk_query, "notes": fallback_note},
            "qradar": {"description": "QRadar AQL (fallback)", "query": qradar_query, "notes": fallback_note},
            "elastic": {"description": "Elasticsearch (fallback)", "query": json.dumps(elastic_query, indent=2), "notes": fallback_note},
            "sentinel": {"description": "Sentinel KQL (fallback)", "query": sentinel_query, "notes": fallback_note},
        }
    except Exception as e:
        logger.error(f"Error creating fallback SIEM queries: {e}")
        err_entry = {"description": "Error", "query": "Error", "notes": str(e)}
        return {"splunk": err_entry, "qradar": err_entry, "elastic": err_entry, "sentinel": err_entry}
