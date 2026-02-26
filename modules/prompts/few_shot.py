"""
PERSEPTOR v2.0 - Few-Shot Examples
Pre-crafted examples for each AI task to improve output quality.
"""


class FewShotExamples:
    """Few-shot examples for prompt engineering."""

    SIGMA_RULE_EXAMPLE = """---
title: Suspicious PowerShell Download and Execute
id: 3b6ab547-8ec2-4991-b284-7bad67e8e2c8
status: experimental
description: Detects PowerShell commands that download and execute content from the internet
references:
    - https://attack.mitre.org/techniques/T1059/001/
author: PERSEPTOR
date: 2024/01/15
tags:
    - attack.execution
    - attack.t1059.001
    - attack.command_and_control
    - attack.t1105
logsource:
    category: process_creation
    product: windows
detection:
    selection_powershell:
        Image|endswith:
            - '\\powershell.exe'
            - '\\pwsh.exe'
    selection_download:
        CommandLine|contains:
            - 'Invoke-WebRequest'
            - 'wget'
            - 'curl'
            - 'Net.WebClient'
            - 'DownloadString'
            - 'DownloadFile'
            - 'Start-BitsTransfer'
    selection_execute:
        CommandLine|contains:
            - 'Invoke-Expression'
            - 'iex'
            - '| IEX'
            - 'Start-Process'
    filter_legitimate:
        ParentImage|endswith:
            - '\\svchost.exe'
            - '\\msiexec.exe'
    condition: selection_powershell and selection_download and selection_execute and not filter_legitimate
fields:
    - CommandLine
    - ParentImage
    - ParentCommandLine
    - User
falsepositives:
    - Legitimate PowerShell scripts that download and execute modules
    - Software deployment tools
level: high"""

    IOC_EXTRACTION_EXAMPLE = """{
  "sigma_title": "APT29 Cozy Bear SolarWinds Supply Chain Attack Indicators",
  "sigma_description": "Detects indicators associated with APT29 SUNBURST backdoor and Teardrop malware",
  "indicators_of_compromise": {
    "ips": ["13.59.205.66", "54.193.127.66"],
    "domains": ["avsvmcloud.com", "freescanonline.com"],
    "urls": ["https://avsvmcloud.com/api/v1/update"],
    "email_addresses": [],
    "file_hashes": ["b91ce2fa41029f6955bff20079468448", "32519b85c0b422e4656de6e6c41878e95fd95026267daab4215ee59c107d6c77"],
    "filenames": ["SolarWinds.Orion.Core.BusinessLayer.dll", "gracious_truth.exe"],
    "registry_keys": ["HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\SolarWindsUpdate"],
    "process_names": ["SolarWinds.BusinessLayerHost.exe"],
    "malicious_commands": ["rundll32.exe C:\\\\Windows\\\\SysWOW64\\\\Rundll32.exe,EntryPoint"]
  },
  "ttps": [
    {"mitre_id": "T1195.002", "technique_name": "Supply Chain Compromise: Compromise Software Supply Chain", "tactic": "Initial Access", "description": "Trojanized SolarWinds Orion update"},
    {"mitre_id": "T1059.001", "technique_name": "PowerShell", "tactic": "Execution", "description": "PowerShell used for post-exploitation commands"},
    {"mitre_id": "T1071.001", "technique_name": "Web Protocols", "tactic": "Command and Control", "description": "HTTPS used for C2 communication"}
  ],
  "suspicious_patterns": ["DGA subdomain pattern under avsvmcloud.com", "Timestomping of malicious DLL"],
  "process_chains": ["solarwinds.businesslayerhost.exe -> rundll32.exe -> cmd.exe"],
  "cves": [],
  "tools_or_malware": ["SUNBURST", "Teardrop", "Raindrop"],
  "threat_actors": ["APT29", "Cozy Bear", "Nobelium"],
  "campaigns": ["SolarWinds Supply Chain Attack"],
  "malicious_execution_chains": ["SolarWinds update -> SUNBURST backdoor -> Teardrop loader -> Cobalt Strike"],
  "image_based_indicators": [],
  "obfuscations_refanged": [],
  "confidence_level": "high",
  "notes": "High-confidence APT29 attribution based on infrastructure overlap and TTP similarity"
}"""

    SIEM_QUERY_EXAMPLE = """{
  "splunk": {
    "description": "Detect suspicious PowerShell download and execute patterns",
    "query": "index=windows sourcetype=WinEventLog:Security EventCode=4688 (NewProcessName=*powershell.exe OR NewProcessName=*pwsh.exe) AND (CommandLine=*Invoke-WebRequest* OR CommandLine=*DownloadString* OR CommandLine=*Net.WebClient*) AND (CommandLine=*Invoke-Expression* OR CommandLine=*IEX*) | stats count by NewProcessName, CommandLine, ParentProcessName, SubjectUserName | where count > 0",
    "notes": "Consider adding tstats for better performance on large datasets. Adjust index and sourcetype for your environment."
  },
  "qradar": {
    "description": "Detect suspicious PowerShell download and execute patterns",
    "query": "SELECT sourceip, username, LOGSOURCENAME(logsourceid) as logsource, UTF8(payload) as cmdline FROM events WHERE devicetype=12 AND LOWER(processname) LIKE '%powershell%' AND (UTF8(payload) LIKE '%Invoke-WebRequest%' OR UTF8(payload) LIKE '%DownloadString%') AND (UTF8(payload) LIKE '%Invoke-Expression%' OR UTF8(payload) LIKE '%IEX%') LAST 24 HOURS",
    "notes": "Adjust LAST clause and add custom properties if available."
  },
  "elastic": {
    "description": "Detect suspicious PowerShell download and execute patterns",
    "query": "process.name:(powershell.exe OR pwsh.exe) AND process.command_line:(*Invoke-WebRequest* OR *DownloadString* OR *Net.WebClient*) AND process.command_line:(*Invoke-Expression* OR *IEX*)",
    "notes": "Index pattern: winlogbeat-* or logs-endpoint*. Consider using EQL for sequence detection."
  },
  "sentinel": {
    "description": "Detect suspicious PowerShell download and execute patterns",
    "query": "SecurityEvent | where EventID == 4688 | where (NewProcessName has 'powershell' or NewProcessName has 'pwsh') | where (CommandLine has 'Invoke-WebRequest' or CommandLine has 'DownloadString' or CommandLine has 'Net.WebClient') | where (CommandLine has 'Invoke-Expression' or CommandLine has 'IEX') | project TimeGenerated, Computer, Account, NewProcessName, CommandLine, ParentProcessName",
    "notes": "Also check DeviceProcessEvents for Defender for Endpoint data."
  }
}"""

    ATOMIC_TEST_EXAMPLE = """[
  {
    "sigma_rule_title": "Suspicious PowerShell Download and Execute",
    "test_name": "PowerShell Download Cradle with Invoke-Expression",
    "description": "Simulates a PowerShell download-and-execute pattern commonly used by threat actors for initial payload delivery. This test creates the exact process creation telemetry that the Sigma rule monitors, using a harmless payload instead of real malware.",
    "mitre_technique": "T1059.001",
    "platforms": ["windows"],
    "privilege_required": "user",
    "prerequisites": ["PowerShell 5.1+ or PowerShell Core", "Sysmon installed with ProcessCreate logging (Event ID 1)", "Windows Security Auditing enabled for Process Creation (Event ID 4688)"],
    "executor": {
      "type": "powershell",
      "steps": [
        "Step 1: Open an elevated PowerShell terminal (Admin not required for this test)",
        "Step 2: Execute the download cradle command below - it downloads a harmless text file and attempts to execute it with Invoke-Expression",
        "Step 3: The command will fail gracefully (text file is not executable) but the process creation event with the download+execute pattern will be logged",
        "Step 4: Verify in Event Viewer or SIEM that the detection fired"
      ],
      "command": "powershell.exe -NoProfile -Command \"$url='https://raw.githubusercontent.com/redcanaryco/atomic-red-team/master/LICENSE.txt'; $data=(New-Object Net.WebClient).DownloadString($url); IEX $data\"",
      "elevation_required": false
    },
    "expected_detection": {
      "log_source": "Windows Security Event Log / Sysmon",
      "event_ids": ["4688", "1"],
      "key_fields": {
        "Image": "C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe",
        "CommandLine": "contains 'Net.WebClient' AND 'DownloadString' AND 'IEX'",
        "ParentImage": "varies (cmd.exe, explorer.exe, etc.)"
      },
      "sigma_condition_match": "Matches selection_powershell (powershell.exe) AND selection_download (Net.WebClient, DownloadString) AND selection_execute (IEX) — all three conditions satisfied"
    },
    "cleanup": {
      "command": "Remove-Item -Path $env:TEMP\\\\atomic-test-* -Force -ErrorAction SilentlyContinue",
      "description": "Removes any temporary files created during the test. The download cradle itself leaves no persistent artifacts."
    },
    "real_world_reference": {
      "threat_actors": ["APT29 (Cozy Bear)", "FIN7", "Lazarus Group"],
      "malware_families": ["SUNBURST", "Emotet PowerShell dropper", "Cobalt Strike PowerShell stager"],
      "mitre_url": "https://attack.mitre.org/techniques/T1059/001/",
      "atomic_red_team_id": "T1059.001-1"
    },
    "safety_notes": "This test downloads a LICENSE.txt file from GitHub - completely harmless. However, some EDR/AV solutions may flag the PowerShell download cradle pattern itself. Whitelist the test in your security tools if needed. No system changes are made."
  }
]"""
