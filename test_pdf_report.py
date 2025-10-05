from modules.pdf_report_module import PDFReportGenerator, ReportSection

def test_pdf_report():
    # Create PDF generator instance
    pdf_generator = PDFReportGenerator(output_dir="reports")
    
    # Threat Summary Section
    threat_summary = """Operation FishMedley is a global espionage campaign conducted by the FishMonger APT group, operated by the Chinese contractor I‑SOON. The campaign targeted governments, NGOs, and think tanks in Asia, Europe, and the United States. While no specific CVEs are mentioned, multiple implants and tools are detailed, including ShadowPad, Spyder, SodaMaster, and a custom implant named RPipeCommander. The attackers leveraged common China-aligned threat actor tactics such as DLL side-loading, living-off-the-land utilities (e.g., comsvcs.dll), use of Impacket for lateral movement, credential dumping from LSASS and SAM, and watering-hole techniques.

Severity is assessed as high given the broad targeting and sophisticated TTPs. Notable techniques include abusing PowerShell and BAT scripts for malware deployment, credential theft via password filter DLLs, and the use of custom C&C communications (via raw TCP/UDP and hardcoded endpoints). In addition, the operation repurposed several known implants and tools previously documented by security vendors.

Recommended mitigations include monitoring and alerting on unusual use of privileged access and system utilities, enforcing strict application whitelisting and DLL blocking, enhancing network segmentation, and vigilant detection of lateral movement and credential dumping activities. Organizations in high-risk sectors should review and reinforce their defenses against such advanced persistent threats."""

    # Analysis Data Section
    analysis_data = {
        "sigma_title": "Detection of FishMedley APT Implant Delivery via PowerShell and DLL Side-Loading",
        "description": "Detects suspicious PowerShell and command-line activity indicative of FishMedley operations. The rule looks for signs of payload delivery mechanisms such as the download of ShadowPad loaders, use of DLL side-loading, and suspicious process memory dumping activities consistent with techniques employed by China-aligned threat actors like FishMonger.",
        "confidence": "high",
        "notes": "This analysis is based on an extensive report detailing Operation FishMedley. The campaign targeted diverse sectors across multiple regions using known implants such as ShadowPad, Spyder, and SodaMaster. Indicators include specific file hashes, registry keys, and command lines associated with lateral movement and credential dumping. The activity aligns with the tactics of FishMonger, a China-aligned threat actor operating under multiple aliases, and is supported by a recent DOJ indictment.",
        "iocs": {
            "ips": ["213.59.118.124", "61.238.103.165", "162.33.178.23", "78.141.202.70", "192.46.223.211", "168.100.10.136"],
            "domains": ["api.googleauthenticatoronline.com", "junlper.com"],
            "urls": ["http://<victim's_web_server_IP_address>/Images/menu/log.dll", "http://5.188.230.47/log.dll", "http://45.76.165.227/wECqKe529r.png"],
            "email_addresses": ["threatintel@eset.com"],
            "file_hashes": [
                "D61A4387466A0C999981086C2C994F2A80193CE3",
                "918DDD842787D64B244D353BFC0E14CC037D2D97",
                "F12C8CEC813257890F4856353ABD9F739DEED890",
                "3630F62771360540B66701ABC8F6C868087A6918",
                "3C08C694C222E7346BD8633461C5D19EAE18B661",
                "5401E3EF903AFE981CFC2840D5F0EF2F1D83B0BF",
                "A4F68D0F1C72C3AC9D70919C17DC52692C43599E",
                "D8B631C551845F892EBB5E7D09991F6C9D4FACAD",
                "3F5F6839C7DCB1D164E4813AF2E30E9461AB35C1"
            ],
            "filenames": [
                "log.dll", "task.exe", "DrsSDK.dll", "DeElevator64.dll",
                "safestore64.dll", "libmaxminddb-0.dll", "libvlc.dll",
                "sasetup.dll", "svhost.tmp", "nb.exe", "drop.zip"
            ],
            "registry_keys": ["SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"],
            "process_names": ["powershell.exe", "rundll32.exe", "svchost.exe", "wmplayer.exe", "cmd.exe"],
            "malicious_commands": [
                "quser",
                "wmic os get lastbootuptime",
                "ipconfig /all",
                "tasklist /svc",
                "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -c \"C:\\Windows\\System32\\rundll32 C:\\windows\\system32\\comsvcs.dll, MiniDump 944 c:\\users\\public\\music\\temp.tmp full\"",
                "reg save hklm\\sam C:\\users\\public\\music\\sam.hive",
                "reg save hklm\\system C:\\users\\public\\music\\system.hive",
                "net user",
                "tasklist /v",
                "for /f \"tokens=1,2 delims= \""
            ]
        },
        "ttps": [
            {
                "mitre_id": "T1059.001",
                "technique_name": "PowerShell",
                "description": "Use of PowerShell to download and execute malicious payloads such as the ShadowPad dropper."
            },
            {
                "mitre_id": "T1574.002",
                "technique_name": "DLL Side-Loading",
                "description": "Loading of malicious DLLs (e.g. log.dll) from trusted executables to execute payloads covertly."
            },
            {
                "mitre_id": "T1003.001",
                "technique_name": "LSASS Memory Dumping",
                "description": "Dumping of LSASS memory using utilities like comsvcs.dll to extract credentials."
            }
        ],
        "threat_actors": ["FishMonger", "I‑SOON", "Earth Lusca", "TAG‑22", "Aquatic Panda", "Red Dev 10"],
        "tools_or_malware": ["ShadowPad", "Spyder", "SodaMaster", "RPipeCommander", "BIOPASS RAT", "nbtscan", "dbxcli"]
    }

    # YARA Rules Section
    yara_rules = """rule Suspicious_Ips_Match
{
    meta:
        description = "Detects suspicious ips IoCs"
        author = "Aytek AYTEMUR"
        date = "2025-05-26"
        reference = "Generated from AI-based IoC Analysis"

    strings:
        $ips_0 = "213.59.118.124" ascii fullword
        $ips_1 = "61.238.103.165" ascii fullword
        $ips_2 = "162.33.178.23" ascii fullword
        $ips_3 = "78.141.202.70" ascii fullword
        $ips_4 = "192.46.223.211" ascii fullword
        $ips_5 = "168.100.10.136" ascii fullword

    condition:
        any of them
}

rule Suspicious_Domains_Match
{
    meta:
        description = "Detects suspicious domains IoCs"
        author = "Aytek AYTEMUR"
        date = "2025-05-26"
        reference = "Generated from AI-based IoC Analysis"

    strings:
        $domains_0 = "api.googleauthenticatoronline.com" nocase
        $domains_1 = "junlper.com" nocase

    condition:
        any of them
}"""

    # Sigma Rules Section
    sigma_rules = """title: "Suspicious LSASS Dump via rundll32/comsvcs.dll MiniDump"
id: "placeholder-001"
status: "experimental"
description: >
  This rule detects processes attempting to dump LSASS memory by invoking rundll32.exe with the Windows system library comsvcs.dll (MiniDump).
  This technique is consistent with the lateral movement and credential dumping observed during Operation FishMedley.
references:
  - "https://www.welivesecurity.com/2025/03/25/fishmedley/"
tags:
  - attack.execution
  - attack.credential_access
  - mitre.T1003.001
  - mitre.T1003.002
logsource:
  product: windows
  service: sysmon
detection:
  selection:
    Image|endswith: "rundll32.exe"
    CommandLine|contains: "comsvcs.dll, MiniDump"
  condition: selection
fields:
  - CommandLine
  - ParentImage
  - Image
falsepositives:
  - "Legitimate administrative or diagnostic usage of MiniDump."
level: high"""

    # Global Sigma Matches Section
    sigma_matches = [
        {
            "title": "Rundll32 Execution Without Parameters",
            "ratio": 66.7,
            "keywords": "rundll32, rundll32.exe",
            "description": "Detects suspicious execution of rundll32.exe without command line parameters, which could indicate potential malicious activity.",
            "severity": "high"
        },
        {
            "title": "Potential Persistence Attempt Via Run Keys Using Reg.EXE",
            "ratio": 57.1,
            "keywords": "run, reg, software, currentversion",
            "description": "Identifies attempts to modify Windows Run registry keys using reg.exe, which could be used for persistence.",
            "severity": "medium"
        },
        {
            "title": "Rundll32 Execution Without CommandLine Parameters",
            "ratio": 50.0,
            "keywords": "rundll32, rundll32.exe",
            "description": "Detects instances of rundll32.exe being executed without command line parameters, which may indicate suspicious activity.",
            "severity": "medium"
        }
    ]

    # Create report sections
    sections = [
        ReportSection(
            title="Threat Summary",
            content=[threat_summary]
        ),
        ReportSection(
            title="Analysis Data",
            content=[analysis_data]
        ),
        ReportSection(
            title="Generated YARA Rules",
            content=[yara_rules]
        ),
        ReportSection(
            title="Sigma Rules",
            content=[sigma_rules]
        )
    ]

    # Add each sigma match as a separate section
    for i, match in enumerate(sigma_matches, 1):
        sections.append(
            ReportSection(
                title=f"Global Sigma Match {i}: {match['title']}",
                content=[{
                    "match_ratio": f"{match['ratio']}%",
                    "keywords": match['keywords'],
                    "description": match['description'],
                    "severity": match['severity']
                }]
            )
        )

    # Generate the report
    pdf_generator.generate_report(
        title="Operation FishMedley Analysis Report",
        sections=sections
    )

if __name__ == "__main__":
    test_pdf_report() 