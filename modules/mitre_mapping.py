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
    "T1566.002": {"name": "Spearphishing Link", "tactic": "initial_access", "keywords": ["link", "url", "click"]},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "initial_access", "keywords": ["exploit", "vulnerability", "cve", "rce"]},
    "T1133": {"name": "External Remote Services", "tactic": "initial_access", "keywords": ["vpn", "rdp", "remote desktop", "citrix"]},
    "T1195": {"name": "Supply Chain Compromise", "tactic": "initial_access", "keywords": ["supply chain", "trojanized", "update", "package"]},

    # Execution
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "execution", "keywords": ["script", "interpreter"]},
    "T1059.001": {"name": "PowerShell", "tactic": "execution", "keywords": ["powershell", "ps1", "invoke-expression", "iex", "-encodedcommand", "-enc"]},
    "T1059.003": {"name": "Windows Command Shell", "tactic": "execution", "keywords": ["cmd.exe", "cmd /c", "command prompt", "batch"]},
    "T1059.005": {"name": "Visual Basic", "tactic": "execution", "keywords": ["vbscript", "vbs", "wscript", "cscript", "macro"]},
    "T1059.007": {"name": "JavaScript", "tactic": "execution", "keywords": ["javascript", "jscript", "js", "node"]},
    "T1204": {"name": "User Execution", "tactic": "execution", "keywords": ["user execution", "double click", "open", "run"]},
    "T1047": {"name": "Windows Management Instrumentation", "tactic": "execution", "keywords": ["wmi", "wmic", "wmiprvse"]},
    "T1053": {"name": "Scheduled Task/Job", "tactic": "execution", "keywords": ["schtasks", "scheduled task", "cron", "at.exe"]},

    # Persistence
    "T1547.001": {"name": "Registry Run Keys / Startup Folder", "tactic": "persistence", "keywords": ["run key", "startup", "hkcu\\software\\microsoft\\windows\\currentversion\\run", "autorun"]},
    "T1543.003": {"name": "Windows Service", "tactic": "persistence", "keywords": ["service", "sc.exe", "new-service"]},
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
    "T1055": {"name": "Process Injection", "tactic": "defense_evasion", "keywords": ["inject", "process injection", "dll injection", "hollowing", "createremotethread"]},
    "T1218": {"name": "System Binary Proxy Execution", "tactic": "defense_evasion", "keywords": ["mshta", "rundll32", "regsvr32", "certutil", "lolbin"]},

    # Credential Access
    "T1003": {"name": "OS Credential Dumping", "tactic": "credential_access", "keywords": ["credential dump", "lsass", "mimikatz", "procdump", "ntds"]},
    "T1003.001": {"name": "LSASS Memory", "tactic": "credential_access", "keywords": ["lsass", "mimikatz", "sekurlsa"]},
    "T1110": {"name": "Brute Force", "tactic": "credential_access", "keywords": ["brute force", "password spray", "credential stuffing"]},
    "T1552": {"name": "Unsecured Credentials", "tactic": "credential_access", "keywords": ["plaintext password", "credentials in files", "password file"]},

    # Discovery
    "T1082": {"name": "System Information Discovery", "tactic": "discovery", "keywords": ["systeminfo", "hostname", "ver", "system information"]},
    "T1083": {"name": "File and Directory Discovery", "tactic": "discovery", "keywords": ["dir", "find", "ls", "file listing"]},
    "T1087": {"name": "Account Discovery", "tactic": "discovery", "keywords": ["net user", "net group", "whoami", "account discovery"]},
    "T1057": {"name": "Process Discovery", "tactic": "discovery", "keywords": ["tasklist", "ps", "get-process", "process list"]},
    "T1049": {"name": "System Network Connections Discovery", "tactic": "discovery", "keywords": ["netstat", "ss", "network connections"]},

    # Lateral Movement
    "T1021.001": {"name": "Remote Desktop Protocol", "tactic": "lateral_movement", "keywords": ["rdp", "mstsc", "remote desktop", "3389"]},
    "T1021.002": {"name": "SMB/Windows Admin Shares", "tactic": "lateral_movement", "keywords": ["smb", "admin$", "c$", "ipc$", "net use"]},
    "T1570": {"name": "Lateral Tool Transfer", "tactic": "lateral_movement", "keywords": ["copy", "transfer", "move laterally", "psexec"]},

    # Collection
    "T1005": {"name": "Data from Local System", "tactic": "collection", "keywords": ["collect data", "local files", "sensitive data"]},
    "T1113": {"name": "Screen Capture", "tactic": "collection", "keywords": ["screenshot", "screen capture", "screen grab"]},
    "T1056.001": {"name": "Keylogging", "tactic": "collection", "keywords": ["keylogger", "keylogging", "keystroke"]},

    # Command and Control
    "T1071": {"name": "Application Layer Protocol", "tactic": "command_and_control", "keywords": ["http", "https", "dns", "c2", "command and control"]},
    "T1071.001": {"name": "Web Protocols", "tactic": "command_and_control", "keywords": ["http beacon", "https callback", "web c2"]},
    "T1071.004": {"name": "DNS", "tactic": "command_and_control", "keywords": ["dns tunnel", "dns c2", "dns exfiltration"]},
    "T1105": {"name": "Ingress Tool Transfer", "tactic": "command_and_control", "keywords": ["download", "wget", "curl", "certutil", "bitsadmin"]},
    "T1572": {"name": "Protocol Tunneling", "tactic": "command_and_control", "keywords": ["tunnel", "ssh tunnel", "vpn tunnel", "socks"]},
    "T1573": {"name": "Encrypted Channel", "tactic": "command_and_control", "keywords": ["encrypted", "ssl", "tls", "encrypted c2"]},

    # Exfiltration
    "T1041": {"name": "Exfiltration Over C2 Channel", "tactic": "exfiltration", "keywords": ["exfiltrate", "data theft", "steal data"]},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "exfiltration", "keywords": ["ftp exfil", "dns exfil", "icmp exfil"]},
    "T1567": {"name": "Exfiltration Over Web Service", "tactic": "exfiltration", "keywords": ["cloud storage", "dropbox", "google drive", "mega"]},

    # Impact
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "impact", "keywords": ["ransomware", "encrypt", "ransom", "locked files"]},
    "T1490": {"name": "Inhibit System Recovery", "tactic": "impact", "keywords": ["vssadmin", "shadow copy", "bcdedit", "wbadmin"]},
    "T1489": {"name": "Service Stop", "tactic": "impact", "keywords": ["stop service", "net stop", "sc stop", "taskkill"]},
}


def map_iocs_to_mitre(analysis_data: dict) -> List[Dict]:
    """
    Map IoCs and TTPs from analysis data to MITRE ATT&CK techniques.

    Returns a list of matched techniques with confidence scores.
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

        # Get description from AI-extracted TTP
        ttp_description = ""
        if isinstance(ttp, dict):
            ttp_description = ttp.get("description", "")

        for tid in technique_ids:
            if tid in TECHNIQUE_DB and tid not in seen_techniques:
                seen_techniques.add(tid)
                tech = TECHNIQUE_DB[tid]
                matches.append({
                    "technique_id": tid,
                    "technique_name": tech["name"],
                    "tactic": tech["tactic"],
                    "confidence": 0.95,
                    "source": "ai_extracted",
                    "description": ttp_description or f"AI identified {tech['name']} technique used in this attack.",
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

        matched_kws = [kw for kw in tech["keywords"] if kw in combined_text]
        keyword_hits = len(matched_kws)
        if keyword_hits > 0:
            confidence = min(0.9, 0.3 + (keyword_hits * 0.15))
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
