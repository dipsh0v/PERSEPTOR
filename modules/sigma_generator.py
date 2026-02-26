"""
PERSEPTOR v2.0 - Sigma Rule Generator
Multi-category detection with MITRE ATT&CK mapping and structured YAML output.
"""

import yaml
import uuid
import re
from datetime import datetime
from typing import List, Dict, Optional
from modules.logging_config import get_logger

logger = get_logger("sigma_generator")

# MITRE ATT&CK Tactic-to-Tag Mapping
MITRE_TACTIC_MAP = {
    "initial_access": "attack.initial_access",
    "execution": "attack.execution",
    "persistence": "attack.persistence",
    "privilege_escalation": "attack.privilege_escalation",
    "defense_evasion": "attack.defense_evasion",
    "credential_access": "attack.credential_access",
    "discovery": "attack.discovery",
    "lateral_movement": "attack.lateral_movement",
    "collection": "attack.collection",
    "command_and_control": "attack.command_and_control",
    "exfiltration": "attack.exfiltration",
    "impact": "attack.impact",
}

# IoC Category to Sigma Logsource Mapping
LOGSOURCE_MAP = {
    "process": {
        "category": "process_creation",
        "product": "windows",
    },
    "network": {
        "category": "firewall",
        "product": "windows",
    },
    "dns": {
        "category": "dns_query",
        "product": "windows",
    },
    "file": {
        "category": "file_event",
        "product": "windows",
    },
    "registry": {
        "category": "registry_set",
        "product": "windows",
    },
    "image_load": {
        "category": "image_load",
        "product": "windows",
    },
}

# IoC type to detection category mapping
IOC_CATEGORY_MAP = {
    "malicious_commands": "process",
    "process_names": "process",
    "filenames": "file",
    "registry_keys": "registry",
    "ips": "network",
    "domains": "dns",
    "urls": "network",
    "file_hashes": "file",
}

# IoC type to Sigma detection field mapping
IOC_FIELD_MAP = {
    "malicious_commands": "CommandLine",
    "process_names": "Image",
    "filenames": "TargetFilename",
    "registry_keys": "TargetObject",
    "ips": "DestinationIp",
    "domains": "QueryName",
    "urls": "RequestUrl",
    "file_hashes": "Hashes",
}


def _sanitize_title(title: str) -> str:
    """Sanitize a string for use in Sigma rule title."""
    sanitized = re.sub(r'[^\w\s\-\.]', '', title)
    return sanitized[:80].strip()


def _detect_tactics(ioc_type: str, indicators: list) -> List[str]:
    """Detect MITRE ATT&CK tactics based on IoC type and content."""
    tactics = set()

    tactic_keywords = {
        "execution": ["cmd", "powershell", "wscript", "cscript", "mshta", "rundll32", "regsvr32"],
        "persistence": ["registry", "scheduled", "startup", "service", "run\\"],
        "defense_evasion": ["bypass", "hidden", "encoded", "base64", "-enc", "-w hidden"],
        "credential_access": ["mimikatz", "lsass", "sam", "credential", "password", "ntds"],
        "discovery": ["whoami", "ipconfig", "netstat", "systeminfo", "tasklist", "net user"],
        "lateral_movement": ["psexec", "wmic", "winrm", "rdp", "smb"],
        "command_and_control": ["beacon", "callback", "c2", "tunnel"],
        "exfiltration": ["upload", "exfil", "compress", "archive"],
    }

    # Default tactics by IoC type
    type_tactics = {
        "malicious_commands": ["execution"],
        "process_names": ["execution"],
        "filenames": ["persistence"],
        "registry_keys": ["persistence"],
        "ips": ["command_and_control"],
        "domains": ["command_and_control"],
        "urls": ["command_and_control"],
        "file_hashes": ["execution"],
    }

    if ioc_type in type_tactics:
        for t in type_tactics[ioc_type]:
            tactics.add(t)

    # Keyword-based tactic detection
    all_text = " ".join(str(i).lower() for i in indicators)
    for tactic, keywords in tactic_keywords.items():
        if any(kw in all_text for kw in keywords):
            tactics.add(tactic)

    return [MITRE_TACTIC_MAP.get(t, f"attack.{t}") for t in tactics]


def _build_detection(field: str, indicators: list, use_contains: bool = True) -> dict:
    """Build Sigma detection block from indicators."""
    if not indicators:
        return {}

    if len(indicators) == 1:
        if use_contains:
            return {
                "selection": {f"{field}|contains": indicators[0]},
                "condition": "selection",
            }
        return {
            "selection": {field: indicators[0]},
            "condition": "selection",
        }

    if use_contains:
        return {
            "selection": {f"{field}|contains": indicators},
            "condition": "selection",
        }
    return {
        "selection": {field: indicators},
        "condition": "selection",
    }


def _determine_level(ioc_type: str, count: int) -> str:
    """Determine Sigma rule severity level."""
    high_types = {"malicious_commands", "file_hashes"}
    medium_types = {"process_names", "registry_keys", "ips"}

    if ioc_type in high_types:
        return "high" if count <= 5 else "critical"
    if ioc_type in medium_types:
        return "medium"
    return "low"


def _fields_for_category(category: str) -> list:
    """Get relevant output fields for a detection category."""
    fields_map = {
        "process": ["CommandLine", "ParentCommandLine", "ParentImage", "User", "IntegrityLevel"],
        "network": ["DestinationIp", "DestinationPort", "SourceIp", "SourcePort"],
        "dns": ["QueryName", "QueryType", "QueryResults"],
        "file": ["TargetFilename", "Image", "CreationUtcTime"],
        "registry": ["TargetObject", "Details", "Image"],
        "image_load": ["ImageLoaded", "Image", "Signed", "SignatureStatus"],
    }
    return fields_map.get(category, [])


def generate_sigma_rules_for_analysis(
    analysis_data: dict,
    article_url: str = "",
    gpt_title: str = "",
    gpt_description: str = "",
) -> List[dict]:
    """
    Generate structured Sigma rules from analysis data.

    Returns a list of dicts, each with keys: title, rule_yaml, category, level, tags.
    """
    rules = []
    iocs = analysis_data.get("indicators_of_compromise", {})
    current_date = datetime.now().strftime("%Y/%m/%d")

    for ioc_type, indicators in iocs.items():
        if not indicators or ioc_type not in IOC_CATEGORY_MAP:
            continue

        # Limit indicators per rule to keep rules manageable
        indicators = indicators[:50]

        category = IOC_CATEGORY_MAP[ioc_type]
        field = IOC_FIELD_MAP[ioc_type]
        logsource = LOGSOURCE_MAP.get(category, {"category": "process_creation", "product": "windows"})
        tactics = _detect_tactics(ioc_type, indicators)
        level = _determine_level(ioc_type, len(indicators))

        # Determine if field should use contains modifier
        use_contains = ioc_type in {"malicious_commands", "process_names", "filenames", "urls"}

        detection = _build_detection(field, indicators, use_contains=use_contains)
        if not detection:
            continue

        title = _sanitize_title(
            gpt_title if gpt_title else f"PERSEPTOR - Suspicious {ioc_type.replace('_', ' ').title()} Detection"
        )

        rule_doc = {
            "title": title,
            "id": str(uuid.uuid4()),
            "status": "experimental",
            "description": gpt_description if gpt_description else (
                f"Detects suspicious {ioc_type.replace('_', ' ')} indicators "
                f"identified by PERSEPTOR AI analysis."
            ),
            "references": [article_url] if article_url else [],
            "author": "PERSEPTOR - Aytek AYTEMUR",
            "date": current_date,
            "tags": tactics,
            "logsource": logsource,
            "detection": detection,
            "fields": _fields_for_category(category),
            "falsepositives": [
                "Legitimate administrative activity",
                "Security tools using similar patterns",
            ],
            "level": level,
        }

        rule_yaml = yaml.dump(rule_doc, default_flow_style=False, sort_keys=False, allow_unicode=True)

        rules.append({
            "title": title,
            "rule_yaml": rule_yaml,
            "category": category,
            "level": level,
            "tags": tactics,
            "ioc_type": ioc_type,
            "ioc_count": len(indicators),
        })

        logger.info(
            f"Generated Sigma rule: {title}",
            extra={"category": category, "level": level, "ioc_count": len(indicators)},
        )

    if not rules:
        # Generate a placeholder rule if no IoCs found
        placeholder = {
            "title": gpt_title or "PERSEPTOR - No IoC Detected",
            "id": str(uuid.uuid4()),
            "status": "experimental",
            "description": gpt_description or "No malicious indicators detected in AI analysis",
            "references": [article_url] if article_url else [],
            "author": "PERSEPTOR - Aytek AYTEMUR",
            "date": current_date,
            "tags": ["attack.execution"],
            "logsource": {"category": "process_creation", "product": "windows"},
            "detection": {
                "selection": {"CommandLine|contains": "placeholder"},
                "condition": "selection",
            },
            "fields": ["CommandLine", "ParentCommandLine"],
            "falsepositives": ["N/A"],
            "level": "low",
        }
        rule_yaml = yaml.dump(placeholder, default_flow_style=False, sort_keys=False, allow_unicode=True)
        rules.append({
            "title": placeholder["title"],
            "rule_yaml": rule_yaml,
            "category": "process",
            "level": "low",
            "tags": ["attack.execution"],
            "ioc_type": "none",
            "ioc_count": 0,
        })

    logger.info(f"Total Sigma rules generated: {len(rules)}")
    return rules


def sigma_rules_to_yaml(rules: List[dict]) -> str:
    """Combine multiple Sigma rule dicts into a multi-document YAML string."""
    yaml_parts = []
    for r in rules:
        yaml_parts.append(r["rule_yaml"])
    return "\n---\n".join(yaml_parts)


# ─── Legacy Compatibility ─────────────────────────────────────────────────────

def generate_sigma_rules_for_commands(
    malicious_cmds: list,
    gpt_title: str = "",
    gpt_description: str = "",
    article_url: str = "",
):
    """
    Legacy-compatible wrapper. Returns (rules_list, yaml_string).
    """
    analysis_data = {
        "indicators_of_compromise": {
            "malicious_commands": malicious_cmds or [],
        }
    }
    rules = generate_sigma_rules_for_analysis(
        analysis_data, article_url, gpt_title, gpt_description
    )
    yaml_str = sigma_rules_to_yaml(rules)
    return rules, yaml_str


def generate_splunk_and_qradar_queries(analysis_data: dict):
    """Legacy function - builds basic Splunk/QRadar queries from IoCs."""
    splunk_queries = []
    qradar_queries = []

    iocs = analysis_data.get("indicators_of_compromise", {})
    malicious_cmds = iocs.get("malicious_commands", [])
    suspicious_processes = iocs.get("process_names", [])

    or_terms_splunk = []
    or_terms_qradar = []

    for cmd in malicious_cmds:
        safe_cmd = cmd.replace('"', '\\"')
        or_terms_splunk.append(f'CommandLine="*{safe_cmd}*"')
        or_terms_qradar.append(f'UTF8(payload) LIKE "%{safe_cmd}%"')

    for proc in suspicious_processes:
        safe_proc = proc.replace('"', '\\"')
        or_terms_splunk.append(f'(Image="*{safe_proc}*" OR ParentImage="*{safe_proc}*")')
        or_terms_qradar.append(f'UTF8(payload) LIKE "%{safe_proc}%"')

    if or_terms_splunk:
        splunk_q = (
            'index=wineventlog (EventID=4688 OR EventCode=1) '
            f'({ " OR ".join(or_terms_splunk) })'
        )
        splunk_queries.append(splunk_q)

    if or_terms_qradar:
        qradar_q = (
            'SELECT * FROM events '
            'WHERE (EventID=4688 OR EventCode=1) AND '
            f'({ " OR ".join(or_terms_qradar) })'
        )
        qradar_queries.append(qradar_q)

    return splunk_queries, qradar_queries
