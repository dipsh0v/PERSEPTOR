"""
PERSEPTOR v2.0 - MITRE ATT&CK Mapping Module
Maps IoCs and TTPs to MITRE ATT&CK framework techniques.
"""

from typing import List, Dict, Optional
from modules.logging_config import get_logger

logger = get_logger("mitre_mapping")

# MITRE ATT&CK Technique Database (commonly encountered in threat reports)
TECHNIQUE_DB = {
    # Initial Access
    "T1566": {"name": "Phishing", "tactic": "initial_access", "keywords": ["phishing", "spear-phishing", "email attachment", "malicious link"]},
    "T1566.001": {"name": "Spearphishing Attachment", "tactic": "initial_access", "keywords": ["attachment", "doc", "xls", "macro", "office"]},
    "T1566.002": {"name": "Spearphishing Link", "tactic": "initial_access", "keywords": ["spearphishing link", "phishing link", "malicious url", "credential harvesting"]},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "initial_access", "keywords": ["exploit", "vulnerability", "cve", "rce"]},
    "T1133": {"name": "External Remote Services", "tactic": "initial_access", "keywords": ["vpn", "rdp", "remote desktop", "citrix"]},
    "T1195": {"name": "Supply Chain Compromise", "tactic": "initial_access", "keywords": ["supply chain", "trojanized", "supply chain compromise", "trojanized package"]},

    # Execution
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "execution", "keywords": ["scripting interpreter", "command interpreter", "script execution"]},
    "T1059.001": {"name": "PowerShell", "tactic": "execution", "keywords": ["powershell", "ps1", "invoke-expression", "iex", "-encodedcommand", "-enc"]},
    "T1059.003": {"name": "Windows Command Shell", "tactic": "execution", "keywords": ["cmd.exe", "cmd /c", "command prompt", "batch"]},
    "T1059.005": {"name": "Visual Basic", "tactic": "execution", "keywords": ["vbscript", "vbs", "wscript", "cscript", "macro"]},
    "T1059.007": {"name": "JavaScript", "tactic": "execution", "keywords": ["javascript", "jscript", "wscript.exe", "node.exe"]},
    "T1204": {"name": "User Execution", "tactic": "execution", "keywords": ["user execution", "double click", "malicious document", "lure"]},
    "T1047": {"name": "Windows Management Instrumentation", "tactic": "execution", "keywords": ["wmi", "wmic", "wmiprvse"]},
    "T1053": {"name": "Scheduled Task/Job", "tactic": "execution", "keywords": ["schtasks", "scheduled task", "cron", "at.exe"]},

    # Persistence
    "T1547.001": {"name": "Registry Run Keys / Startup Folder", "tactic": "persistence", "keywords": ["run key", "startup", "hkcu\\software\\microsoft\\windows\\currentversion\\run", "autorun"]},
    "T1543.003": {"name": "Windows Service", "tactic": "persistence", "keywords": ["sc create", "sc.exe", "new-service", "install service"]},
    "T1136": {"name": "Create Account", "tactic": "persistence", "keywords": ["net user", "create account", "add user"]},
    "T1505.003": {"name": "Web Shell", "tactic": "persistence", "keywords": ["webshell", "web shell", "aspx", "jsp"]},

    # Privilege Escalation
    "T1548.002": {"name": "Bypass UAC", "tactic": "privilege_escalation", "keywords": ["uac", "bypass", "eventvwr", "fodhelper"]},
    "T1068": {"name": "Exploitation for Privilege Escalation", "tactic": "privilege_escalation", "keywords": ["privilege escalation", "local exploit", "kernel exploit"]},

    # Defense Evasion
    "T1027": {"name": "Obfuscated Files or Information", "tactic": "defense_evasion", "keywords": ["obfuscated", "encoded", "base64", "encryption", "packed"]},
    "T1036": {"name": "Masquerading", "tactic": "defense_evasion", "keywords": ["masquerad", "renamed", "disguised", "legitimate"]},
    "T1070": {"name": "Indicator Removal", "tactic": "defense_evasion", "keywords": ["clear logs", "delete logs", "wevtutil", "indicator removal"]},
    "T1562.001": {"name": "Disable or Modify Tools", "tactic": "defense_evasion", "keywords": ["disable defender", "tamper protection", "disable antivirus", "kill av"]},
    "T1055": {"name": "Process Injection", "tactic": "defense_evasion", "keywords": ["process injection", "dll injection", "process hollowing", "createremotethread", "virtualallocex", "writeprocessmemory", "ntcreatethreadex"]},
    "T1218": {"name": "System Binary Proxy Execution", "tactic": "defense_evasion", "keywords": ["mshta", "rundll32", "regsvr32", "certutil", "lolbin"]},

    # Credential Access
    "T1003": {"name": "OS Credential Dumping", "tactic": "credential_access", "keywords": ["credential dump", "lsass", "mimikatz", "procdump", "ntds"]},
    "T1003.001": {"name": "LSASS Memory", "tactic": "credential_access", "keywords": ["lsass", "mimikatz", "sekurlsa"]},
    "T1110": {"name": "Brute Force", "tactic": "credential_access", "keywords": ["brute force", "password spray", "credential stuffing"]},
    "T1552": {"name": "Unsecured Credentials", "tactic": "credential_access", "keywords": ["plaintext password", "credentials in files", "password file"]},

    # Discovery
    "T1082": {"name": "System Information Discovery", "tactic": "discovery", "keywords": ["systeminfo", "hostname", "systeminfo.exe", "system information discovery"]},
    "T1083": {"name": "File and Directory Discovery", "tactic": "discovery", "keywords": ["dir /s", "dir /b", "get-childitem", "file listing", "tree /f"]},
    "T1087": {"name": "Account Discovery", "tactic": "discovery", "keywords": ["net user", "net group", "whoami", "account discovery", "net localgroup"]},
    "T1057": {"name": "Process Discovery", "tactic": "discovery", "keywords": ["tasklist", "get-process", "process list", "tasklist.exe"]},
    "T1049": {"name": "System Network Connections Discovery", "tactic": "discovery", "keywords": ["netstat", "netstat -an", "network connections", "get-nettcpconnection"]},

    # Lateral Movement
    "T1021.001": {"name": "Remote Desktop Protocol", "tactic": "lateral_movement", "keywords": ["rdp", "mstsc", "remote desktop", "3389"]},
    "T1021.002": {"name": "SMB/Windows Admin Shares", "tactic": "lateral_movement", "keywords": ["smb", "admin$", "c$", "ipc$", "net use"]},
    "T1570": {"name": "Lateral Tool Transfer", "tactic": "lateral_movement", "keywords": ["copy", "transfer", "move laterally", "psexec"]},

    # Collection
    "T1005": {"name": "Data from Local System", "tactic": "collection", "keywords": ["collect data", "local files", "sensitive data"]},
    "T1113": {"name": "Screen Capture", "tactic": "collection", "keywords": ["screenshot", "screen capture", "screen grab"]},
    "T1056.001": {"name": "Keylogging", "tactic": "collection", "keywords": ["keylogger", "keylogging", "keystroke"]},

    # Command and Control
    "T1071": {"name": "Application Layer Protocol", "tactic": "command_and_control", "keywords": ["c2 over http", "c2 channel", "command and control", "c2 communication"]},
    "T1071.001": {"name": "Web Protocols", "tactic": "command_and_control", "keywords": ["http beacon", "https callback", "web c2", "http c2"]},
    "T1071.004": {"name": "DNS", "tactic": "command_and_control", "keywords": ["dns tunnel", "dns c2", "dns exfiltration"]},
    "T1105": {"name": "Ingress Tool Transfer", "tactic": "command_and_control", "keywords": ["download payload", "wget", "curl -o", "certutil -urlcache", "bitsadmin /transfer"]},
    "T1572": {"name": "Protocol Tunneling", "tactic": "command_and_control", "keywords": ["tunnel", "ssh tunnel", "vpn tunnel", "socks"]},
    "T1573": {"name": "Encrypted Channel", "tactic": "command_and_control", "keywords": ["encrypted c2", "encrypted channel", "ssl c2", "tls tunnel"]},

    # Exfiltration
    "T1041": {"name": "Exfiltration Over C2 Channel", "tactic": "exfiltration", "keywords": ["exfiltrate", "data theft", "steal data"]},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "exfiltration", "keywords": ["ftp exfil", "dns exfil", "icmp exfil"]},
    "T1567": {"name": "Exfiltration Over Web Service", "tactic": "exfiltration", "keywords": ["cloud storage", "dropbox", "google drive", "mega"]},

    # Impact
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "impact", "keywords": ["ransomware", "encrypt", "ransom", "locked files"]},
    "T1490": {"name": "Inhibit System Recovery", "tactic": "impact", "keywords": ["vssadmin", "shadow copy", "bcdedit", "wbadmin"]},
    "T1489": {"name": "Service Stop", "tactic": "impact", "keywords": ["stop service", "net stop", "sc stop", "taskkill"]},
}


TACTIC_NORMALIZE = {
    "initial access": "initial_access",
    "initial-access": "initial_access",
    "initialaccess": "initial_access",
    "execution": "execution",
    "persistence": "persistence",
    "privilege escalation": "privilege_escalation",
    "privilege-escalation": "privilege_escalation",
    "privilegeescalation": "privilege_escalation",
    "defense evasion": "defense_evasion",
    "defense-evasion": "defense_evasion",
    "defenseevasion": "defense_evasion",
    "credential access": "credential_access",
    "credential-access": "credential_access",
    "credentialaccess": "credential_access",
    "discovery": "discovery",
    "lateral movement": "lateral_movement",
    "lateral-movement": "lateral_movement",
    "lateralmovement": "lateral_movement",
    "collection": "collection",
    "command and control": "command_and_control",
    "command-and-control": "command_and_control",
    "commandandcontrol": "command_and_control",
    "c2": "command_and_control",
    "exfiltration": "exfiltration",
    "impact": "impact",
    "resource development": "resource_development",
    "resource-development": "resource_development",
    "reconnaissance": "reconnaissance",
}


def _normalize_tactic(tactic: str) -> str:
    """Normalize tactic name to snake_case format used by MITRE ATT&CK."""
    if not tactic:
        return "unknown"
    normalized = tactic.strip().lower().replace("_", " ").replace("-", " ")
    return TACTIC_NORMALIZE.get(normalized, tactic.strip().lower().replace(" ", "_"))


def map_iocs_to_mitre(analysis_data: dict) -> List[Dict]:
    """
    Map IoCs and TTPs from analysis data to MITRE ATT&CK techniques.

    Returns a list of matched techniques with confidence scores.
    Handles technique IDs not in TECHNIQUE_DB by preserving AI-extracted data.
    """
    matches = []
    seen_techniques = set()

    # First, check if TTPs were already identified by the AI
    ttps = analysis_data.get("ttps", [])
    for ttp in ttps:
        ttp_str = str(ttp).upper() if not isinstance(ttp, dict) else str(ttp.get("mitre_id", "")).upper()
        # Extract technique IDs (T followed by 4 digits, optionally .3 digits)
        technique_ids = set()
        import re
        for m in re.finditer(r'T\d{4}(?:\.\d{3})?', ttp_str):
            technique_ids.add(m.group())

        # Get description and metadata from AI-extracted TTP
        ttp_description = ""
        ttp_technique_name = ""
        ttp_tactic = ""
        if isinstance(ttp, dict):
            ttp_description = ttp.get("description", "")
            ttp_technique_name = ttp.get("technique_name", "")
            ttp_tactic = ttp.get("tactic", "")

        for tid in technique_ids:
            if tid in seen_techniques:
                continue
            seen_techniques.add(tid)

            if tid in TECHNIQUE_DB:
                tech = TECHNIQUE_DB[tid]
                matches.append({
                    "technique_id": tid,
                    "technique_name": tech["name"],
                    "tactic": tech["tactic"],
                    "confidence": 0.95,
                    "source": "ai_extracted",
                    "description": ttp_description or f"AI identified {tech['name']} technique used in this attack.",
                })
            else:
                # Technique not in our DB — preserve AI-extracted data
                normalized_tactic = _normalize_tactic(ttp_tactic)
                matches.append({
                    "technique_id": tid,
                    "technique_name": ttp_technique_name or f"Technique {tid}",
                    "tactic": normalized_tactic,
                    "confidence": 0.90,
                    "source": "ai_extracted",
                    "description": ttp_description or f"AI identified technique {tid} used in this attack.",
                })

    # Then, keyword-match IoC content against technique database
    all_text_parts = []

    iocs = analysis_data.get("indicators_of_compromise", {})
    for ioc_type, indicators in iocs.items():
        if isinstance(indicators, list):
            all_text_parts.extend(str(i).lower() for i in indicators)

    # Add threat actors and tools
    actors = analysis_data.get("threat_actors", [])
    all_text_parts.extend(str(a).lower() for a in actors)

    tools = analysis_data.get("tools_or_malware", [])
    all_text_parts.extend(str(t).lower() for t in tools)

    combined_text = " ".join(all_text_parts)

    for tid, tech in TECHNIQUE_DB.items():
        if tid in seen_techniques:
            continue

        # Use word-boundary-aware matching to avoid substring false positives
        matched_kws = []
        for kw in tech["keywords"]:
            # For multi-word keywords, simple 'in' check is fine
            # For single-word keywords >= 5 chars, also fine
            # For short keywords < 5 chars, require word boundaries
            if len(kw) < 5:
                # Short keyword — require word boundary matching
                import re as _re
                if _re.search(r'\b' + _re.escape(kw) + r'\b', combined_text):
                    matched_kws.append(kw)
            else:
                if kw in combined_text:
                    matched_kws.append(kw)

        keyword_hits = len(matched_kws)
        # Require at least 2 keyword hits for a match, unless it's a very specific keyword (multi-word)
        min_hits = 1 if any(len(kw.split()) >= 2 for kw in matched_kws) else 2
        if keyword_hits >= min_hits:
            confidence = min(0.85, 0.35 + (keyword_hits * 0.15))
            seen_techniques.add(tid)
            kw_evidence = ", ".join(matched_kws[:5])
            matches.append({
                "technique_id": tid,
                "technique_name": tech["name"],
                "tactic": tech["tactic"],
                "confidence": round(confidence, 2),
                "source": "keyword_match",
                "keyword_hits": keyword_hits,
                "description": f"Detected via keyword indicators: {kw_evidence}",
            })

    # Sort by confidence descending
    matches.sort(key=lambda x: x["confidence"], reverse=True)

    logger.info(f"MITRE ATT&CK mapping: {len(matches)} techniques identified")
    return matches


def get_mitre_tags(techniques: List[Dict]) -> List[str]:
    """Convert technique list to Sigma-compatible MITRE tags."""
    tags = set()
    for tech in techniques:
        tactic = tech.get("tactic", "")
        tid = tech.get("technique_id", "")
        if tactic:
            tags.add(f"attack.{tactic}")
        if tid:
            tags.add(f"attack.{tid.lower()}")
    return sorted(tags)


def get_tactic_summary(techniques: List[Dict]) -> Dict[str, int]:
    """Get a summary of tactics and their technique counts."""
    summary = {}
    for tech in techniques:
        tactic = tech.get("tactic", "unknown")
        summary[tactic] = summary.get(tactic, 0) + 1
    return summary


def get_kill_chain_phase(tactic: str) -> int:
    """Get the kill chain phase number for a tactic (for ordering)."""
    phase_order = {
        "initial_access": 1,
        "execution": 2,
        "persistence": 3,
        "privilege_escalation": 4,
        "defense_evasion": 5,
        "credential_access": 6,
        "discovery": 7,
        "lateral_movement": 8,
        "collection": 9,
        "command_and_control": 10,
        "exfiltration": 11,
        "impact": 12,
    }
    return phase_order.get(tactic, 99)
