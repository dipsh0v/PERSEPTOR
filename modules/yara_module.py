import re
import uuid
from datetime import datetime

# === Utility Functions ===
def safe_string(string: str) -> str:
    """ Escape special characters for YARA syntax """
    return string.replace('"', '\\"')

# === Main YARA Rule Generation Function ===
def generate_yara_rules(analysis_data: dict) -> str:
    """
    Generates YARA rules using IoCs extracted from JSON data.
    """
    yara_rules = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    # IoC Mapping to YARA Structures
    ioc_map = {
        "ips": "ascii fullword",
        "domains": "nocase",
        "urls": "ascii wide",
        "email_addresses": "nocase", 
        "file_hashes": "ascii fullword",
        "filenames": "nocase",
        "registry_keys": "nocase",
        "process_names": "nocase",
        "malicious_commands": "ascii wide nocase"
    }

    for ioc_type, yara_modifier in ioc_map.items():
        iocs = analysis_data.get("indicators_of_compromise", {}).get(ioc_type, [])
        if iocs:
            yara_strings = [f"${ioc_type}_{index} = \"{safe_string(ioc)}\" {yara_modifier}" for index, ioc in enumerate(iocs)]

            yara_rule = f"""
rule Suspicious_{ioc_type.capitalize()}_Match
{{
    meta:
        description = "Detects suspicious {ioc_type} IoCs"
        author = "Aytek AYTEMUR"
        date = "{current_date}"
        reference = "Generated from AI-based IoC Analysis"

    strings:
        {chr(10).join(yara_strings)}

    condition:
        any of them
}}
"""
            yara_rules.append(yara_rule.strip())

    malicious_cmds = analysis_data.get("indicators_of_compromise", {}).get("malicious_commands", [])
    if malicious_cmds:
        cmd_strings = [f"${'cmd_' + str(index)} = \"{safe_string(cmd)}\"" for index, cmd in enumerate(malicious_cmds)]

        yara_rule = f"""
rule Suspicious_Command_Detection
{{
    meta:
        description = "Detects malicious command usage"
        author = "Aytek AYTEMUR"
        date = "{current_date}"
        reference = "Generated from AI-based IoC Analysis"

    strings:
        {chr(10).join(cmd_strings)}

    condition:
        any of them
}}
"""
        yara_rules.append(yara_rule.strip())

    return "\n\n".join(yara_rules)

# === Example Usage ===
if __name__ == "__main__":
    # Sample data mimicking JSON output structure
    sample_analysis_data = {
        "indicators_of_compromise": {
            "ips": ["192.168.1.1", "10.0.0.5"],
            "domains": ["example.com", "malicious[.]site"],
            "urls": ["hxxp://badurl[.]com"],
            "email_addresses": ["attacker@badmail.com"],
            "file_hashes": ["3c1b5d2f26e57a..."],
            "filenames": ["winupdate.exe", "malware.exe"],
            "registry_keys": ["HKEY_LOCAL_MACHINE\\Software\\SuspiciousApp"],
            "process_names": ["cmd.exe", "powershell.exe"],
            "malicious_commands": ["rm -rf /important/data", "wget hxxp://malicious[.]com"]
        }
    }

    yara_output = generate_yara_rules(sample_analysis_data)
    print(yara_output)
