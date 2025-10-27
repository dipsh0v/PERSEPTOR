# 🎯 DEATHCon 2025 Amsterdam - PERSEPTOR Workshop

## Human & AI: Detection Engineering Collaboration

<div align="center">

![DEATHCon 2025](https://img.shields.io/badge/DEATHCon-2025-red?style=for-the-badge&logo=security&logoColor=white)
![Amsterdam](https://img.shields.io/badge/Amsterdam-Netherlands-orange?style=for-the-badge&logo=location&logoColor=white)
![Detection Engineering](https://img.shields.io/badge/Detection-Engineering-blue?style=for-the-badge&logo=shield&logoColor=white)

**Workshop Leader:** Aytek AYTEMUR  
**Date:** November 8-9, 2025  
**Format:** Hybrid (On-site + Virtual)

</div>

---

## 📖 Workshop Overview

This hands-on workshop explores the intersection of human expertise and AI capabilities in detection engineering. You'll analyze threats manually using your own methodology, then compare your approach with PERSEPTOR's AI-driven analysis to understand the strengths, weaknesses, and collaboration opportunities between human and AI workflows.

**Goal:** Understand how human expertise and AI capabilities can complement each other in modern detection engineering.

---

## 🎯 Workshop Structure

### 📊 Module 1: Threat Report Analysis (60 minutes)
Manual threat intelligence extraction and detection rule creation

### 🔬 Module 2: Detection Rule Creation (30 minutes)
Create Sigma rules from security scenarios using your own methodology

### 🤖 Module 3: AI Comparison (20 minutes)
Run the same tasks through PERSEPTOR and compare approaches

### 💭 Module 4: Reflection (15 minutes)
Analyze differences, strengths, and collaboration opportunities

---

## 📋 Prerequisites

### Required
- ✅ Text Editor (VS Code, Sublime, etc.)
- ✅ Web Browser
- ✅ Timer/Stopwatch (to track your time)
- ✅ OpenAI API Key for PERSEPTOR - [Get it here](https://platform.openai.com/api-keys)

### Knowledge
- Basic cybersecurity concepts
- MITRE ATT&CK framework familiarity
- Understanding of Sigma and YARA formats
- Log analysis experience

---

## 🚀 Getting Started

### Prepare Your Workspace

```bash
mkdir deathcon2025_workshop
cd deathcon2025_workshop
mkdir threat_analysis detection_qa perseptor_comparison notes
```

---

## 📊 MODULE 1: Threat Report Analysis

You will receive a threat intelligence report URL at the workshop start.

### 📝 Step 1: Your Approach (5 minutes)

**Before analyzing the report, write down your methodology:**

```
File: notes/my_approach.md

Reflect on these questions:
1. When analyzing a threat report, what do you look for FIRST?
2. What's your systematic approach to intelligence extraction?
3. What categories of intelligence do you extract?
4. How do you prioritize extraction?
5. What detection opportunities do you identify?
```

This reflection helps you understand your own methodology before comparing with AI.

---

### 📝 Step 2: Intelligence Extraction (45 minutes)

**⏰ START YOUR TIMER**

#### A. IOC Extraction (10 min)

```
File: threat_analysis/iocs.md

Extract and categorize:
- IP Addresses
- Domains
- URLs
- File Hashes (MD5, SHA1, SHA256)
- Email Addresses
- Registry Keys
- File Paths
- Other indicators

Format:
## IP Addresses
- 192.168.1.100 - [Context from report]
- 10.0.0.50 - [Context from report]

## Domains
- malicious-domain.com - [Context from report]
```

---

#### B. TTP Extraction (15 min)

```
File: threat_analysis/ttps.md

Focus on BEHAVIORS, not just indicators:
- Attack techniques used
- Tools and methods
- Execution patterns
- Command-line patterns
- Attack flow

Format:
## Initial Access
- Method: [Description]
- Evidence: [From report]

## Execution
- Technique: [Description]
- Commands: [Patterns]
```

---

#### C. MITRE Mapping (10 min)

```
File: threat_analysis/mitre_mapping.md

Map behaviors to ATT&CK:
- Technique ID (e.g., T1566.001)
- Technique Name
- Tactic
- Detection opportunities

Use: https://attack.mitre.org/
```

---

#### D. Threat Actors & Tools (5 min)

```
File: threat_analysis/actors_tools.md

Document:
- Threat actor names/aliases
- Attribution confidence
- Malware families
- Tools used (custom and commodity)
- Capabilities
```

---

#### E. Detection Rules (20 min)

Create detection rules based on your analysis:

**Sigma Rules:**
```
File: threat_analysis/sigma_rules.yaml

Create 3-5 Sigma rules covering:
- Process execution patterns
- Network activity (if applicable)
- File operations
- Registry modifications

Example structure:
title: PowerShell Base64 Execution - [Threat Campaign]
id: [UUID]
status: experimental
description: Detects base64-encoded PowerShell execution observed in [campaign]
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

**YARA Rules:**
```
File: threat_analysis/yara_rules.yar

Create 2-3 YARA rules for malware detection

Example:
rule Malware_Campaign_Variant {
    meta:
        description = "Detects [malware] from [campaign]"
        author = "[Your Name]"
        date = "2025-11-08"
        reference = "[Report URL]"
        
    strings:
        $s1 = "unique_string" ascii wide
        $s2 = "another_pattern" ascii wide
        $c2 = "malicious-domain.com" ascii wide
        
    condition:
        uint16(0) == 0x5A4D and
        filesize < 5MB and
        2 of ($s*) or $c2
}
```

**⏰ STOP TIMER - Record your time**

---

#### F. SigmaHQ Search (10 min)

```
File: threat_analysis/sigmahq_matches.md

Search https://github.com/SigmaHQ/sigma for:
- Related techniques (e.g., T1059.001)
- Malware families
- Behaviors

Document:
## Found Rules
- Rule: [Title]
- Path: [File path in repo]
- Relevance: [How it applies]
- Coverage: [What it detects]
- Gaps: [What it misses]

## Coverage Assessment
- Existing coverage: [Estimate %]
- Gaps identified: [List]
- New rules needed: [List]
```

---

## 🔬 MODULE 2: Detection Rule Creation

Create Sigma rules for these scenarios. **Time yourself for each!**

### Challenge 1: DNS Tunneling

```
Scenario: Detect possible DNS Tunneling Behavior

Create a Sigma rule that detects:
- Unusually long DNS queries
- Suspicious DNS query patterns
- NXDOMAIN responses with random subdomains

File: detection_qa/dns_tunneling.yaml
```

---

### Challenge 2: PowerShell C2 Download

```
Scenario: Detect file download from C2 server using PowerShell

Create a Sigma rule that detects:
- PowerShell download cmdlets (Invoke-WebRequest, wget, curl)
- Common obfuscation attempts
- Suspicious download patterns

File: detection_qa/powershell_download.yaml
```

---

### Challenge 3: Credential Dumping

```
Scenario: Detect credential dumping via LSASS access

Create a Sigma rule that detects:
- Unauthorized LSASS memory access
- Common credential dumping tools
- Suspicious process handles

File: detection_qa/credential_dumping.yaml
```

---

### Challenge 4: Scheduled Task Persistence

```
Scenario: Detect malicious scheduled task creation

Create a Sigma rule that detects:
- Suspicious schtasks.exe usage
- Tasks from unusual locations
- Tasks with suspicious actions

File: detection_qa/scheduled_task.yaml
```

---

### Challenge 5: WMI Lateral Movement

```
Scenario: Detect lateral movement via WMI

Create a Sigma rule that detects:
- Remote WMI execution
- WMI process creation on remote hosts
- Suspicious WMI activity patterns

File: detection_qa/wmi_lateral_movement.yaml
```

**⏰ Record total time and time per rule**

---

## 🤖 MODULE 3: AI Comparison with PERSEPTOR

### Part 1: Threat Report Analysis

**⏰ START TIMER**

1. Access PERSEPTOR: `http://localhost:3000`
2. Enter your OpenAI API key
3. Input the same threat report URL
4. Click "Analyze"
5. Wait for completion

**⏰ STOP TIMER - Note PERSEPTOR's time**

### Part 2: Detection QA

Access the **QA** page and run each challenge:

```
1. "Create a Sigma rule to detect possible DNS Tunneling Behavior"
2. "Create a Sigma rule to detect possible file download from C2 server by using PowerShell"
3. "Create a Sigma rule to detect credential dumping attempts targeting LSASS process"
4. "Create a Sigma rule to detect malicious scheduled task creation for persistence"
5. "Create a Sigma rule to detect lateral movement using Windows Management Instrumentation"
```

**⏰ Note PERSEPTOR's time for each**

---

## 📊 Comparison Framework

```
File: perseptor_comparison/analysis.md
```

### 1. Time Comparison

```markdown
## Time Analysis

| Task | My Time | PERSEPTOR Time | Observations |
|------|---------|----------------|--------------|
| Threat Report Analysis | X min | X min | [Notes] |
| Detection QA (5 rules) | X min | X sec | [Notes] |
| **Total** | **X min** | **X min** | [Notes] |
```

---

### 2. Quality Comparison

```markdown
## IOC Extraction

**My Results:**
- Total IOCs: X
- Categories: [List]

**PERSEPTOR Results:**
- Total IOCs: X
- Categories: [List]

**Comparison:**
- PERSEPTOR found that I missed: [List]
- I found that PERSEPTOR missed: [List]
- Context understanding: [Analysis]

---

## TTP Extraction

**My Results:**
- Total TTPs: X
- [Key behaviors identified]

**PERSEPTOR Results:**
- Total TTPs: X
- [Key behaviors identified]

**Comparison:**
- Behavioral understanding: [Analysis]
- Attack flow comprehension: [Analysis]

---

## MITRE Mapping

**My Results:**
- Techniques: [List with IDs]

**PERSEPTOR Results:**
- Techniques: [List with IDs]

**Comparison:**
- Accuracy: [Analysis]
- Coverage: [Analysis]

---

## Detection Rules

### Sigma Rule Comparison

**Example: DNS Tunneling**

My Approach:
```yaml
[Your rule]
```

PERSEPTOR's Approach:
```yaml
[AI rule]
```

**Analysis:**
- Detection coverage: [Comparison]
- False positive risk: [Comparison]
- Technical quality: [Comparison]
- Approach differences: [Analysis]

[Repeat for each rule]
```

---

### 3. SigmaHQ Coverage

```markdown
## SigmaHQ Repository Search

**My Research:**
- Rules found: X
- Time: X min
- Coverage: [Assessment]

**PERSEPTOR's Matches:**
- Rules found: X
- Time: Automatic
- Coverage: [Assessment]

**Comparison:**
- Thoroughness: [Analysis]
- Accuracy: [Analysis]
```

---

## 💭 MODULE 4: Reflection & Discussion

```
File: notes/reflection.md
```

### A. Time & Efficiency

```markdown
## Speed Analysis

- PERSEPTOR was X times faster
- Time matters for: [Use cases]
- Speed-quality trade-offs: [Observations]
```

---

### B. Strengths & Weaknesses

```markdown
## What Humans Excel At

1. [Strength] - Example: [From workshop]
2. [Strength] - Example: [From workshop]
3. [Strength] - Example: [From workshop]

## What AI Excels At

1. [Strength] - Example: [From workshop]
2. [Strength] - Example: [From workshop]
3. [Strength] - Example: [From workshop]

## Human Limitations

1. [Limitation] - Impact: [Analysis]
2. [Limitation] - Impact: [Analysis]

## AI Limitations

1. [Limitation] - Impact: [Analysis]
2. [Limitation] - Impact: [Analysis]
```

---

### C. What Each Missed

```markdown
## Intelligence I Missed

1. [Item] - Why: [Reason] - Severity: [Impact]
2. [Item] - Why: [Reason] - Severity: [Impact]

## Intelligence PERSEPTOR Missed

1. [Item] - Why: [Reason] - Severity: [Impact]
2. [Item] - Why: [Reason] - Severity: [Impact]

## Detection Logic Gaps

**In my rules:** [Analysis]
**In AI rules:** [Analysis]
```

---

### D. Trust & Validation

```markdown
## Would I Use These Rules in Production?

**My Own Rules:**
- Trust level: X/10
- What needs validation: [List]
- What needs improvement: [List]

**AI-Generated Rules:**
- Trust level: X/10
- What needs validation: [List]
- What needs improvement: [List]

## Validation Requirements

For AI rules, I would always validate:
1. [Aspect]
2. [Aspect]
3. [Aspect]
```

---

### E. Collaboration Model

```markdown
## How Should Human & AI Work Together?

**Proposed Workflow:**

1. [Step] - Performed by: Human/AI - Reason: [Why]
2. [Step] - Performed by: Human/AI - Reason: [Why]
3. [Step] - Performed by: Human/AI - Reason: [Why]

**Best Division of Labor:**

| Task | Best Performed By | Reason |
|------|------------------|--------|
| Initial triage | Human/AI | [Reason] |
| IOC extraction | Human/AI | [Reason] |
| Behavioral analysis | Human/AI | [Reason] |
| Rule generation | Human/AI | [Reason] |
| Validation | Human/AI | [Reason] |
| Context understanding | Human/AI | [Reason] |

**Collaboration Benefits:**
- [Benefit]
- [Benefit]
```

---

### F. Key Insights

```markdown
## What I Learned

**About my own methodology:**
- [Insight]
- [Insight]

**About AI capabilities:**
- [Insight]
- [Insight]

**About detection engineering:**
- [Insight]
- [Insight]

## How I'll Change My Approach

**Will start using AI for:**
1. [Use case] - Because: [Reason]
2. [Use case] - Because: [Reason]

**Will keep doing manually:**
1. [Task] - Because: [Reason]
2. [Task] - Because: [Reason]

**Will always validate:**
- [What AI produces]
```

---

### G. Future Perspective

```markdown
## The Future of Detection Engineering

**In 1 year:**
- [Prediction about AI role]
- [Prediction about human role]

**In 5 years:**
- [Prediction]

**Will AI replace detection engineers?**
My view: [Yes/No/Partially] - Because: [Detailed reasoning based on workshop]

**Skills humans will need:**
1. [Skill]
2. [Skill]
3. [Skill]
```

---

## 📚 Essential Resources

### MITRE ATT&CK
- Website: https://attack.mitre.org/
- Navigator: https://mitre-attack.github.io/attack-navigator/

### Sigma
- Repository: https://github.com/SigmaHQ/sigma
- Creation Guide: https://github.com/SigmaHQ/sigma/wiki/Rule-Creation-Guide
- Specification: https://github.com/SigmaHQ/sigma-specification

### YARA
- Documentation: https://yara.readthedocs.io/
- Rules Repository: https://github.com/Yara-Rules/rules

---

## 📧 Contact & Community

**Workshop Leader:**
- Aytek AYTEMUR
- Email: aytek.aytemur@outlook.com
- GitHub: [dipsh0v](https://github.com/dipsh0v)
- PERSEPTOR: https://github.com/dipsh0v/PERSEPTOR

**Share Your Experience:**
- #DEATHCon2025
- #PERSEPTOR
- #DetectionEngineering

---

## ⚠️ Important Notes

### Ethics & Privacy
- Use for educational purposes only
- Don't analyze classified/proprietary reports without authorization
- Respect data handling policies

### API Usage
- Monitor OpenAI API costs
- Set usage limits
- Keep API keys secure

---

<div align="center">

## 🎯 Workshop Goals

**This workshop is about learning, not competing.**

Understand the unique strengths of human expertise and AI capabilities.  
Discover how they can work together to improve detection engineering.  
Share knowledge and insights with the community.

---

*DEATHCon 2025 Amsterdam - Detection Engineering and Threat Hunting Conference*  
*November 8-9, 2025 - The Netherlands*

</div>
