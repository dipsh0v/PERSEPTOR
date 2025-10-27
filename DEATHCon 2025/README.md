# 🎯 DEATHCon 2025 - PERSEPTOR Workshop

## Human & AI: Detection Engineering Collaboration

<div align="center">

![DEATHCon 2025](https://img.shields.io/badge/DEATHCon-2025-red?style=for-the-badge&logo=security&logoColor=white)
![Detection Engineering](https://img.shields.io/badge/Detection-Engineering-blue?style=for-the-badge&logo=shield&logoColor=white)

**Workshop Leader:** Aytek AYTEMUR  
**Format:** Hybrid (On-site + Virtual)

</div>

---

## 📖 Workshop Overview

This hands-on workshop explores how human expertise and AI capabilities complement each other in detection engineering. You'll analyze threats manually, then compare your approach with PERSEPTOR's AI-driven analysis.

**Goal:** Understand how human expertise and AI can work together in modern detection engineering.

---

## 🎯 Workshop Structure

1. **Module 1: Threat Report Analysis** (110 minutes)
2. **Module 2: Detection Rule Creation** (30 minutes)  
3. **Module 3: PERSEPTOR Comparison** (20 minutes)
4. **Module 4: Reflection** (15 minutes)

---

## 📋 Prerequisites

- Text Editor (VS Code, Sublime, etc.)
- Web Browser
- Timer/Stopwatch
- OpenAI API Key - [Get it here](https://platform.openai.com/api-keys)

**Knowledge:** Basic cybersecurity (detection engineering, threat intelligence), MITRE ATT&CK, Sigma/YARA formats

---

## 📊 MODULE 1: Threat Report Analysis (110 min)

You will receive a public threat report URL at the workshop start.

### Step 1: Initial Reflection (≈5 min)

```
File: notes/my_approach.md

Before analyzing, document:
1. What do you look for FIRST in a threat report?
2. What's your systematic approach?
3. What intelligence categories do you extract?
4. How do you identify detection opportunities?
```

---

### Step 2: IOC Extraction (≈20 min)

**⏰ START TIMER**

```
File: threat_analysis/iocs.md

Extract and categorize:
- IP Addresses
- Domains & URLs
- File Hashes (MD5, SHA1, SHA256)
- Email Addresses
- Registry Keys
- File Paths
- Other indicators

Example format:
## IP Addresses
- 192.168.1.100 - C2 server (paragraph 3)

## Domains
- malicious-domain.com - Primary C2 domain
```

**⏰ STOP TIMER**

---

### Step 3: TTP Extraction (≈30 min)

**⏰ START TIMER**

```
File: threat_analysis/ttps.md

Focus on BEHAVIORS:
- Attack techniques
- Execution patterns
- Command-line patterns
- Tools and methods

Example format:
## Initial Access
- Spear-phishing with malicious attachment
- Evidence: [Quote from report]

## Execution
- PowerShell with base64 encoding
- Pattern: powershell.exe -enc [base64]
```

**⏰ STOP TIMER**

---

### Step 4: MITRE Mapping (≈10 min)

```
File: threat_analysis/mitre_mapping.md

Map behaviors to ATT&CK techniques:

T1566.001 - Phishing: Spearphishing Attachment
- Tactic: Initial Access
- Evidence: [From report]
- Detection: Email analysis, sandbox

T1059.001 - PowerShell
- Tactic: Execution
- Evidence: [From report]
- Detection: Script block logging (Event ID 4104)
```

Use: https://attack.mitre.org/

---

### Step 5: Threat Actors & Tools (≈10 min)

```
File: threat_analysis/actors_tools.md

## Threat Actors
- Name/Alias: [Name]
- Confidence: High/Medium/Low
- Motivation: [Type]
- Targets: [Sectors]

## Malware & Tools
- Emotet - Banking Trojan/Loader
- Mimikatz - Credential dumping
- [etc.]
```

---

### Step 6: Detection Rules (≈35 min)

**⏰ START TIMER**

**Sigma Rules (≈25 min):**

```
File: threat_analysis/sigma_rules.yaml

Create 3-5 Sigma rules

Template:
title: PowerShell Base64 Execution - [Campaign Name]
id: [UUID]
status: experimental
description: Detects base64 PowerShell execution from [campaign]
references:
    - [Report URL]
author: [Your Name]
date: 2025/11/08
tags:
    - attack.execution
    - attack.t1059.001
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains:
            - ' -enc '
            - ' -EncodedCommand '
    condition: selection
falsepositives:
    - Legitimate admin scripts
level: high
```

**YARA Rules (≈10 min):**

```
File: threat_analysis/yara_rules.yar

Create 2-3 YARA rules

Template:
rule Malware_Campaign_Variant {
    meta:
        description = "Detects [malware]"
        author = "[Your Name]"
        date = "2025-11-08"
        
    strings:
        $s1 = "unique_string" ascii wide
        $c2 = "malicious-domain.com" ascii wide
        
    condition:
        uint16(0) == 0x5A4D and
        2 of them
}
```

**⏰ STOP TIMER**

---

### Step 7: SigmaHQ Search (≈25 min)

**⏰ START TIMER**

```
File: threat_analysis/sigmahq_matches.md

Search https://github.com/SigmaHQ/sigma

Look for:
- Related techniques (T1059.001, etc.)
- Malware families mentioned
- Similar attack behaviors

Document:
## Rule: [Title]
- Path: rules/windows/process_creation/...
- Relevance: High/Medium/Low
- What it covers: [Description]
- What it misses: [Gaps]

## Coverage Summary
- Existing rules found: X
- Coverage estimate: ~X%
- Gaps: [What's not covered]
- New rules needed: [List]
```

**⏰ STOP TIMER**

---

## 🔬 MODULE 2: Detection Rule Creation (≈30 min)

Create Sigma rules for these scenarios. **Time each challenge.**

**⏰ START TIMER (total for all 5)**

### Challenge 1: DNS Tunneling (≈6 min)
```
File: detection_qa/dns_tunneling.yaml

Scenario: Detect DNS tunneling behavior
- Long DNS queries
- Suspicious patterns
- NXDOMAIN with random subdomains
```

### Challenge 2: PowerShell Download (≈6 min)
```
File: detection_qa/powershell_download.yaml

Scenario: Detect C2 file download via PowerShell
- Invoke-WebRequest, wget, curl
- Obfuscation attempts
```

### Challenge 3: Credential Dumping (≈6 min)
```
File: detection_qa/credential_dumping.yaml

Scenario: Detect LSASS credential dumping
- LSASS memory access
- Credential dumping tools
```

### Challenge 4: Scheduled Task (≈6 min)
```
File: detection_qa/scheduled_task.yaml

Scenario: Detect malicious scheduled task
- Suspicious schtasks.exe usage
- Unusual locations
```

### Challenge 5: WMI Lateral Movement (≈6 min)
```
File: detection_qa/wmi_lateral_movement.yaml

Scenario: Detect WMI lateral movement
- Remote WMI execution
- WMI process creation
```

**⏰ STOP TIMER - Record total time**

---

## 🤖 MODULE 3: PERSEPTOR Comparison (≈20 min)

### Part 1: Threat Report Analysis (≈10 min)

**⏰ START TIMER**

1. Access PERSEPTOR: `http://localhost:3000`
2. Enter OpenAI API key
3. Input the same threat report URL
4. Click "Analyze" and wait

**⏰ STOP TIMER - Note PERSEPTOR's time**

---

### Part 2: Detection QA (≈10 min)

Go to **QA** page and run each challenge:

```
1. "Create a Sigma rule to detect possible DNS Tunneling Behavior"
2. "Create a Sigma rule to detect possible file download from C2 server by using PowerShell"
3. "Create a Sigma rule to detect credential dumping attempts targeting LSASS process"
4. "Create a Sigma rule to detect malicious scheduled task creation for persistence"
5. "Create a Sigma rule to detect lateral movement using Windows Management Instrumentation"
```

**⏰ Note time for each**

---

## 📊 COMPARISON & ANALYSIS

```
File: perseptor_comparison/analysis.md
```

### 1. Time Comparison

```markdown
| Task | My Time | PERSEPTOR Time |
|------|---------|----------------|
| IOC Extraction | X min | X min |
| TTP Extraction | X min | X min |
| MITRE Mapping | X min | X min |
| Actors & Tools | X min | X min |
| Sigma Rules | X min | X min |
| YARA Rules | X min | X min |
| SigmaHQ Search | X min | X min |
| Detection QA | X min | X min |
| **Total** | **X min** | **X min** |

Observations: [Your notes]
```

---

### 2. Quality Comparison

```markdown
## IOCs
My results: X IOCs across Y categories
PERSEPTOR's results: X IOCs across Y categories

PERSEPTOR found that I missed: [List]
I found that PERSEPTOR missed: [List]

---

## TTPs
My approach: [Brief description]
PERSEPTOR's approach: [Brief description]

Behavioral understanding: [Comparison notes]

---

## MITRE Mapping
My techniques: [List IDs]
PERSEPTOR's techniques: [List IDs]

Accuracy: [Notes]

---

## Detection Rules

### Example: DNS Tunneling

My rule:
```yaml
[Your rule]
```

PERSEPTOR's rule:
```yaml
[PERSEPTOR's rule]
```

Comparison:
- Coverage: [Notes]
- False positives: [Notes]
- Approach: [Key differences]

[Repeat for other significant rules]
```

---

### 3. SigmaHQ Research

```markdown
My research: X rules in Y minutes
PERSEPTOR's matches: X rules (automatic)

Comparison: [Which was more thorough/accurate]
```

---

## 💭 MODULE 4: Reflection (≈15 min)

```
File: notes/reflection.md
```

### Key Questions to Answer

```markdown
## 1. Speed vs Quality
- Was PERSEPTOR faster? By how much?
- Did speed affect quality?
- When does speed matter? When doesn't it?

## 2. Human Strengths
What did I do better than PERSEPTOR?
1. [Strength + example]
2. [Strength + example]
3. [Strength + example]

## 3. AI Strengths
What did PERSEPTOR do better than me?
1. [Strength + example]
2. [Strength + example]
3. [Strength + example]

## 4. What Each Missed
Intelligence/patterns I missed: [List]
Intelligence/patterns PERSEPTOR missed: [List]

Why did these gaps occur? [Analysis]

## 5. Trust & Validation
Would I use my rules in production? [Yes/No + why]
Would I use PERSEPTOR's rules without review? [Yes/No + why]

What validation is needed for:
- My rules: [List]
- PERSEPTOR's rules: [List]

## 6. Collaboration Model
How should human and AI work together?

| Task | Who Should Do It | Why |
|------|-----------------|-----|
| Initial triage | Human/AI/Both | [Reason] |
| IOC extraction | Human/AI/Both | [Reason] |
| Behavioral analysis | Human/AI/Both | [Reason] |
| Rule creation | Human/AI/Both | [Reason] |
| Validation | Human/AI/Both | [Reason] |

## 7. Future Outlook
Will AI replace detection engineers? [Your view + reasoning]

Skills humans will need in AI era:
1. [Skill]
2. [Skill]
3. [Skill]

How will you change your workflow? [Action items]
```

---

## 📚 Resources

**MITRE ATT&CK:** https://attack.mitre.org/  
**Sigma Repository:** https://github.com/SigmaHQ/sigma  
**Sigma Guide:** https://github.com/SigmaHQ/sigma/wiki/Rule-Creation-Guide  
**YARA Docs:** https://yara.readthedocs.io/  
**PERSEPTOR:** https://github.com/dipsh0v/PERSEPTOR

---

## 📧 Contact

**Aytek AYTEMUR**  
Email: aytek.aytemur@outlook.com  
GitHub: [dipsh0v](https://github.com/dipsh0v)

**Share:** #DEATHCon2025 #PERSEPTOR #DetectionEngineering

---

## ⚠️ Important Notes

- Educational purposes only
- Respect data handling policies
- Monitor API costs
- Keep API keys secure

---

<div align="center">

## 🎯 Remember

**This workshop is about learning, not competing.**

Discover how human expertise and AI capabilities can work together  
to improve detection engineering.

**DEATHCon 2025 - Detection Engineering and Threat Hunting Conference**

</div>
