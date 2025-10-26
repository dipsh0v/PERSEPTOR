# 🎯 DEATHCon 2025 Amsterdam - PERSEPTOR Workshop

## Human vs AI: The Ultimate Detection Engineering Challenge

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

Welcome to the most challenging Detection Engineering workshop at DEATHCon 2025! This hands-on experience will test your skills as a threat analyst and detection engineer against PERSEPTOR, an AI-powered threat intelligence platform.

**The Question:** Can human expertise still outperform AI in threat analysis and detection rule creation?

**Your Mission:** Complete a comprehensive threat analysis workflow manually, then compare your results with PERSEPTOR's AI-driven analysis.

---

## 🎯 Workshop Structure

This workshop is divided into **TWO main cases** that progressively challenge your detection engineering skills:

### 📊 Case 1: Threat Report Analysis & Detection Engineering
**Duration:** 60-90 minutes  
**Objective:** Manual threat intelligence extraction and detection rule creation

### 🔬 Case 2: Detection Rule Q&A Challenge
**Duration:** 30-45 minutes  
**Objective:** Create Sigma detection rules from specific security scenarios

### 🤖 AI Comparison Phase
**Duration:** 30 minutes  
**Objective:** Compare your work with PERSEPTOR's AI-generated results

### 💭 Reflection & Discussion
**Duration:** 20 minutes  
**Objective:** Analyze AI vs Human strengths, weaknesses, and collaboration opportunities

---

## 📋 Prerequisites

Before starting this workshop, ensure you have:

### Required Tools
- ✅ **Text Editor** (VS Code, Sublime Text, Notepad++, etc.)
- ✅ **Web Browser** (Chrome, Firefox, Safari)
- ✅ **Note-taking Tool** (Physical notebook or digital)
- ✅ **Timer/Stopwatch** (to track your time)
- ✅ **OpenAI API Key** (for AI comparison phase) - [Get it here](https://platform.openai.com/api-keys)

### Required Knowledge
- ✅ Basic understanding of cybersecurity concepts
- ✅ Familiarity with threat intelligence terminology
- ✅ Knowledge of MITRE ATT&CK framework
- ✅ Understanding of Sigma and YARA rule formats
- ✅ Experience with log analysis and SIEM concepts

### Optional but Helpful
- 📚 Access to MITRE ATT&CK Navigator
- 📚 SigmaHQ repository bookmarked
- 📚 YARA documentation reference
- 📚 Previous experience with threat hunting

---

## 🚀 Getting Started

### Step 1: Prepare Your Workspace

Create a dedicated workspace for this workshop:

```bash
# Create workshop directory
mkdir deathcon2025_workshop
cd deathcon2025_workshop

# Create subdirectories
mkdir case1_threat_analysis
mkdir case2_detection_qa
mkdir perseptor_comparison
mkdir reflection
```

### Step 2: Download Workshop Materials

- **Workshop README** (this file)
- **Reference Links** (provided below)
- **Timer/Stopwatch ready**

### Step 3: Mental Preparation

Before starting:
1. **Clear your mind** - Focus entirely on the challenge
2. **Eliminate distractions** - Close unnecessary applications
3. **Prepare note-taking tools** - Have them ready
4. **Review MITRE ATT&CK** - Quick refresh if needed

---

## 📊 CASE 1: Threat Report Analysis & Detection Engineering

### 🎯 Objective

You will be given a real-world threat intelligence report URL. Your goal is to extract all relevant intelligence and create detection rules **manually** before seeing how PERSEPTOR performs the same task.

### 📝 Phase 1.1: Initial Reflection (5 minutes)

**Before you start analyzing the threat report, ask yourself:**

> *"When I'm asked to analyze a threat report or intelligence article, what should I look for first? What's my systematic approach? What intelligence should I extract?"*

**Write down your answer in your workspace:**

```
File: case1_threat_analysis/my_approach.md

Questions to answer:
1. What are the FIRST things I look for in a threat report?
2. What intelligence categories do I need to extract?
3. What's my priority order for extraction?
4. What detection opportunities should I identify?
5. How do I validate the intelligence I extract?
```

**Take 5 minutes** to document your personal approach. This reflection will be valuable later when comparing with AI.

---

### 📝 Phase 1.2: Systematic Intelligence Extraction (45-60 minutes)

**⏰ START YOUR TIMER NOW!**

You will extract intelligence in the following systematic order:

#### 1️⃣ IOC Extraction (10 minutes)

Extract **Indicators of Compromise** from the threat report:

```
File: case1_threat_analysis/iocs.md

Categories to extract:
- IP Addresses (both IPv4 and IPv6)
- Domain Names
- URLs
- File Hashes (MD5, SHA1, SHA256)
- Email Addresses
- Registry Keys
- File Paths
- Mutex Names
- Named Pipes
- User Agents
- SSL Certificate Hashes
```

**Quality Criteria:**
- ✅ Extract ALL IOCs mentioned in the report
- ✅ Categorize them properly
- ✅ Note the context where each IOC appears
- ✅ Mark confidence level (High/Medium/Low) for each IOC

**Example Format:**
```markdown
## IP Addresses
- 192.168.1.100 (High Confidence) - C2 server mentioned in paragraph 3
- 10.0.0.50 (Medium Confidence) - Suspected staging server

## Domains
- malicious-domain.com (High Confidence) - Primary C2 domain
- backup-server.net (Medium Confidence) - Backup C2 infrastructure

## File Hashes (SHA256)
- abc123def456... (High Confidence) - Main malware payload
```

---

#### 2️⃣ TTP (Behavioral) Extraction (15 minutes)

Extract **Tactics, Techniques, and Procedures** - the behavioral patterns of the threat:

```
File: case1_threat_analysis/ttps.md

What to extract:
- HOW the attack was conducted (techniques)
- WHAT tools/methods were used (procedures)
- WHY certain approaches were taken (tactics)
- Attack kill chain stages
- Behavioral patterns
- Unique methodologies
```

**Quality Criteria:**
- ✅ Focus on BEHAVIOR, not just indicators
- ✅ Identify the attack kill chain
- ✅ Note unique or innovative techniques
- ✅ Extract command-line patterns
- ✅ Document execution flows

**Example Format:**
```markdown
## Initial Access
- Technique: Spear-phishing with malicious attachment
- Description: [Detailed description from report]
- Evidence: [Quote or reference from report]

## Execution
- Technique: PowerShell script execution
- Command Pattern: powershell.exe -enc [base64]
- Description: [Behavioral description]

## Persistence
- Technique: Registry Run key modification
- Path: HKCU\Software\Microsoft\Windows\CurrentVersion\Run
- Description: [How persistence is achieved]
```

---

#### 3️⃣ MITRE ATT&CK Mapping (10 minutes)

Map the extracted TTPs to **MITRE ATT&CK techniques**:

```
File: case1_threat_analysis/mitre_mapping.md

For each TTP, identify:
- MITRE Technique ID (e.g., T1566.001)
- Technique Name
- Tactic Category
- Sub-technique (if applicable)
- Detection opportunities
```

**Resources:**
- MITRE ATT&CK Website: https://attack.mitre.org/
- ATT&CK Navigator: https://mitre-attack.github.io/attack-navigator/

**Example Format:**
```markdown
## Technique Mapping

### T1566.001 - Phishing: Spearphishing Attachment
- **Tactic:** Initial Access
- **Evidence from Report:** [Quote]
- **Detection Opportunity:** Email attachment analysis, sandbox detonation
- **Data Sources:** Email gateway logs, endpoint detection

### T1059.001 - Command and Scripting Interpreter: PowerShell
- **Tactic:** Execution
- **Evidence from Report:** [Quote]
- **Detection Opportunity:** PowerShell script block logging
- **Data Sources:** PowerShell logs (Event ID 4104), process creation logs
```

---

#### 4️⃣ Threat Actor Attribution (5 minutes)

Identify and document **threat actor** information:

```
File: case1_threat_analysis/threat_actors.md

Extract:
- Threat actor name(s) or aliases
- Attribution confidence level
- Known characteristics
- Historical activities
- Motivations and objectives
- Geographical associations
- Target industries/sectors
```

**Example Format:**
```markdown
## Primary Threat Actor: APT99 (Example)

**Attribution Confidence:** High / Medium / Low
**Aliases:** [List alternative names]
**First Observed:** [Date]
**Motivation:** Espionage / Financial / Destructive
**Target Sectors:** Finance, Healthcare, Government
**Geographical Origin:** [If mentioned]
**Known Characteristics:**
- Preference for PowerShell-based attacks
- Use of custom RAT malware
- Targets executives and high-value personnel
```

---

#### 5️⃣ Tools & Malware Identification (5 minutes)

Document all **tools and malware** mentioned:

```
File: case1_threat_analysis/tools_malware.md

Extract:
- Malware family names
- Tool names (both custom and commodity)
- Versions or variants
- Capabilities and features
- Delivery mechanisms
- Communication protocols
```

**Example Format:**
```markdown
## Malware

### Emotet (Example)
- **Type:** Banking Trojan / Loader
- **Capabilities:** 
  - Credential theft
  - Module downloading
  - Lateral movement
  - Email harvesting
- **Delivery:** Malicious Office documents
- **C2 Protocol:** HTTPS

## Tools

### Mimikatz
- **Type:** Credential dumping tool
- **Usage in Attack:** Extract credentials from LSASS
- **Detection:** Process creation, LSASS access
```

---

### 📝 Phase 1.3: Detection Rule Creation (20-30 minutes)

Now create **detection rules** based on your intelligence extraction:

#### 🔹 Sigma Rule Creation

```
File: case1_threat_analysis/sigma_rules.yaml

Create 3-5 Sigma rules based on the threat report
```

**Sigma Rule Requirements:**
- ✅ Follow proper Sigma YAML format
- ✅ Include all required fields (title, description, logsource, detection, etc.)
- ✅ Add MITRE ATT&CK tags
- ✅ Include severity level
- ✅ Write clear detection logic
- ✅ Consider false positive scenarios

**Example Template:**
```yaml
title: Suspicious PowerShell Base64 Execution - [Your Threat Name]
id: [Generate UUID]
status: experimental
description: Detects PowerShell execution with base64-encoded commands as observed in [threat name] campaign
references:
    - [URL to threat report]
author: [Your Name]
tags:
    - attack.execution
    - attack.t1059.001
    - attack.defense_evasion
    - attack.t1027
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains:
            - ' -enc '
            - ' -EncodedCommand '
            - ' -ec '
    condition: selection
falsepositives:
    - Legitimate scripts using base64 encoding
    - System administration tasks
level: high
```

**Create Multiple Rules:**
- At least 1 rule for **process execution**
- At least 1 rule for **network activity** (if applicable)
- At least 1 rule for **persistence mechanism** (if applicable)
- At least 1 rule for **file operations** (if applicable)

---

#### 🔹 YARA Rule Creation

```
File: case1_threat_analysis/yara_rules.yar

Create 2-3 YARA rules based on malware indicators
```

**YARA Rule Requirements:**
- ✅ Proper YARA syntax
- ✅ Clear rule name
- ✅ Metadata section (author, date, description)
- ✅ Strings section with relevant patterns
- ✅ Condition logic
- ✅ Comments explaining detection logic

**Example Template:**
```yara
rule Malware_ThreatName_Variant1 {
    meta:
        description = "Detects [malware name] based on [threat report]"
        author = "[Your Name]"
        date = "2025-11-08"
        reference = "[URL to threat report]"
        hash1 = "[SHA256 if available]"
        severity = "high"
        
    strings:
        // Unique strings from the malware
        $s1 = "unique_string_1" ascii wide
        $s2 = "unique_string_2" ascii wide
        
        // Code patterns
        $hex1 = { 4D 5A 90 00 03 00 00 00 }  // MZ header example
        
        // Registry or file paths
        $path1 = "Software\\Microsoft\\Windows\\CurrentVersion\\Run" ascii wide
        
        // C2 patterns
        $c2_1 = "malicious-domain.com" ascii wide
        
    condition:
        uint16(0) == 0x5A4D and  // PE file
        filesize < 5MB and
        (2 of ($s*)) or
        (1 of ($hex*) and 1 of ($c2*))
}
```

**⏰ STOP YOUR TIMER**

**Document your time:**
```
Total time spent on Case 1: ____ minutes

Breakdown:
- IOC Extraction: ____ minutes
- TTP Extraction: ____ minutes
- MITRE Mapping: ____ minutes
- Threat Actors: ____ minutes
- Tools/Malware: ____ minutes
- Sigma Rules: ____ minutes
- YARA Rules: ____ minutes
```

---

### 📝 Phase 1.4: SigmaHQ Repository Search (15 minutes)

Search the **SigmaHQ repository** for existing detection rules that could detect this threat:

```
File: case1_threat_analysis/sigmahq_matches.md
```

**Steps:**
1. Visit https://github.com/SigmaHQ/sigma
2. Search for rules related to:
   - Techniques you identified (e.g., "T1059.001")
   - Malware families mentioned
   - Specific behaviors (e.g., "powershell base64")
   - Attack patterns

**Document Your Findings:**
```markdown
## SigmaHQ Rule Matches

### Rule 1: [Rule Title]
- **File Path:** rules/windows/process_creation/...
- **Relevance:** High / Medium / Low
- **Coverage:** What aspects of the threat it detects
- **Gaps:** What it misses from the threat report
- **URL:** [Direct link to rule]

### Rule 2: [Rule Title]
...

## Coverage Analysis
- **Total Rules Found:** X rules
- **High Relevance:** X rules
- **Coverage Percentage:** Approximately X% of the threat
- **Gaps Identified:** [List what existing rules don't cover]

## Recommendations
- Rules that should be created (not in SigmaHQ)
- Rules that need modification
- Combined detection strategies
```

---

## 🔬 CASE 2: Detection Rule Q&A Challenge

### 🎯 Objective

Create high-quality Sigma detection rules based on specific security scenarios. This tests your ability to translate security requirements into detection logic.

**⏰ Time Limit:** 30-45 minutes total (5-8 minutes per rule)

---

### 📝 Detection Challenges

Create Sigma rules for each of the following scenarios. **Start your timer for each challenge!**

#### Challenge 1: DNS Tunneling Detection

```
Scenario: Detect possible DNS Tunneling Behavior

Requirements:
- Detect unusually long DNS queries
- Identify high-frequency DNS requests to single domain
- Detect suspicious DNS query patterns (random subdomains)
- Focus on NXDOMAIN responses with suspicious patterns

File: case2_detection_qa/challenge1_dns_tunneling.yaml
```

**Expected Elements:**
- Detection of DNS queries with suspicious characteristics
- Volume-based detection (if possible)
- Pattern-based detection (randomness in subdomains)
- Proper log source configuration
- Clear false positive considerations

---

#### Challenge 2: PowerShell C2 File Download

```
Scenario: Detect file download from C2 server using PowerShell

Requirements:
- Detect PowerShell downloading files from web
- Identify common download commands (Invoke-WebRequest, wget, curl)
- Catch obfuscation attempts
- Focus on command-line patterns

File: case2_detection_qa/challenge2_ps_download.yaml
```

**Expected Elements:**
- PowerShell download cmdlet detection
- Alternative syntax variations
- Obfuscation bypass techniques
- Network indicators if available

---

#### Challenge 3: Credential Dumping via LSASS

```
Scenario: Detect credential dumping attempts targeting LSASS process

Requirements:
- Detect unauthorized access to LSASS memory
- Identify common credential dumping tools
- Catch both tool-based and manual approaches
- Cover multiple techniques (Mimikatz, ProcDump, etc.)

File: case2_detection_qa/challenge3_credential_dumping.yaml
```

**Expected Elements:**
- LSASS process access detection
- Tool signature detection
- Suspicious handle operations
- DLL injection attempts

---

#### Challenge 4: Suspicious Scheduled Task Creation

```
Scenario: Detect malicious scheduled task creation for persistence

Requirements:
- Detect schtasks.exe with suspicious parameters
- Identify tasks running from unusual locations
- Catch tasks with suspicious actions (PowerShell, cmd, etc.)
- Focus on persistence mechanisms

File: case2_detection_qa/challenge4_scheduled_task.yaml
```

**Expected Elements:**
- Schtasks command-line analysis
- Suspicious execution paths
- Unusual schedule patterns
- Privilege escalation indicators

---

#### Challenge 5: Lateral Movement via WMI

```
Scenario: Detect lateral movement using Windows Management Instrumentation

Requirements:
- Detect remote WMI execution
- Identify WMI process creation on remote hosts
- Catch common lateral movement patterns
- Focus on network-based WMI activity

File: case2_detection_qa/challenge5_wmi_lateral_movement.yaml
```

**Expected Elements:**
- WMI remote execution detection
- Network connection patterns
- Process creation via WMI
- Remote administration tools

---

### 📊 Self-Assessment Checklist

For each rule you created, verify:

```
Rule Quality Checklist:
□ Proper YAML format
□ All required fields present (title, description, logsource, detection, etc.)
□ Clear and descriptive title
□ Detailed description
□ Appropriate log source specified
□ Detection logic is sound
□ Condition statement is logical
□ MITRE ATT&CK tags included
□ Severity level appropriate
□ False positives considered
□ Author and date included
□ Status field set (experimental/stable/test)
```

**⏰ STOP YOUR TIMER**

**Document your time:**
```
Total time for Case 2: ____ minutes

Per Challenge:
- Challenge 1 (DNS Tunneling): ____ minutes
- Challenge 2 (PS Download): ____ minutes
- Challenge 3 (Credential Dumping): ____ minutes
- Challenge 4 (Scheduled Task): ____ minutes
- Challenge 5 (WMI Lateral): ____ minutes
```

---

## 🤖 AI COMPARISON PHASE: Human vs PERSEPTOR

Now it's time to see how PERSEPTOR performs on the same tasks!

### Prerequisites

1. ✅ PERSEPTOR is installed and running
   - Backend running on `http://localhost:5000`
   - Frontend running on `http://localhost:3000`
2. ✅ OpenAI API key ready
3. ✅ Both Case 1 and Case 2 completed

---

### 🔍 Part 1: Threat Report Analysis Comparison

**⏰ START TIMER**

#### Step 1: Access PERSEPTOR Dashboard

1. Open your browser and navigate to `http://localhost:3000`
2. Enter your OpenAI API key
3. Navigate to the **Dashboard** page

#### Step 2: Analyze the Same Threat Report

1. **Input the threat report URL** (the same one you analyzed manually)
2. **Click "Analyze"**
3. **Wait for PERSEPTOR to complete the analysis**
4. **Note the time taken** by PERSEPTOR

**⏰ STOP TIMER**

```
File: perseptor_comparison/case1_timing.md

My Manual Analysis Time: ____ minutes
PERSEPTOR Analysis Time: ____ minutes
Time Difference: ____ minutes
Speed Ratio: PERSEPTOR was X times faster/slower
```

#### Step 3: Compare Results

Create a detailed comparison document:

```
File: perseptor_comparison/case1_detailed_comparison.md
```

**Comparison Template:**

```markdown
# Case 1: Threat Report Analysis - Comparison

## 1. IOC Extraction

### My Results
- Total IOCs extracted: X
- IP Addresses: X
- Domains: X
- File Hashes: X
- [etc.]

### PERSEPTOR Results
- Total IOCs extracted: X
- IP Addresses: X
- Domains: X
- File Hashes: X
- [etc.]

### Analysis
**PERSEPTOR caught that I missed:**
- [List IOCs]

**I caught that PERSEPTOR missed:**
- [List IOCs]

**Accuracy Assessment:**
- My accuracy: X%
- PERSEPTOR accuracy: X%
- Context understanding: Human/AI winner and why

---

## 2. TTP (Behavioral) Extraction

### My Results
- Total TTPs identified: X
- [List your TTPs]

### PERSEPTOR Results
- Total TTPs identified: X
- [List PERSEPTOR's TTPs]

### Analysis
**Behavioral understanding:**
- Who captured more nuanced behaviors? [Analysis]
- Who understood attack flow better? [Analysis]
- Quality of descriptions: [Comparison]

**PERSEPTOR advantages:**
- [List]

**My advantages:**
- [List]

---

## 3. MITRE ATT&CK Mapping

### My Results
- Total techniques mapped: X
- Technique IDs: [List]

### PERSEPTOR Results
- Total techniques mapped: X
- Technique IDs: [List]

### Analysis
**Accuracy:**
- Correct mappings: Mine X, PERSEPTOR X
- Incorrect mappings: Mine X, PERSEPTOR X

**Insights:**
- [Analysis of mapping quality]

---

## 4. Threat Actor Attribution

### My Results
[Your attribution analysis]

### PERSEPTOR Results
[PERSEPTOR's attribution]

### Analysis
**Attribution quality:**
- Confidence levels
- Evidence quality
- Context understanding

---

## 5. Tools & Malware

### My Results
- Tools identified: X
- Malware families: X

### PERSEPTOR Results
- Tools identified: X
- Malware families: X

### Analysis
**Completeness and accuracy comparison**

---

## 6. Sigma Rule Comparison

### Rule-by-Rule Comparison

#### My Rule 1 vs PERSEPTOR Rule 1
**My Rule:**
```yaml
[Your rule]
```

**PERSEPTOR's Rule:**
```yaml
[PERSEPTOR's rule]
```

**Analysis:**
- **Detection Coverage:** Mine vs AI
- **False Positive Risk:** Mine vs AI
- **Completeness:** Mine vs AI
- **Technical Quality:** Mine vs AI
- **Winner:** Human/AI/Tie and why

[Repeat for each rule]

### Overall Sigma Assessment
- **Total Rules:** Mine X, PERSEPTOR X
- **Quality Rating:** [Comparison]
- **Coverage:** [Comparison]
- **Innovation:** [Who had more creative approaches?]

---

## 7. YARA Rule Comparison

### Rule-by-Rule Comparison

#### My YARA Rule 1 vs PERSEPTOR YARA Rule 1
**My Rule:**
```yara
[Your rule]
```

**PERSEPTOR's Rule:**
```yara
[PERSEPTOR's rule]
```

**Analysis:**
- **String Selection:** Quality comparison
- **Detection Logic:** Effectiveness
- **False Positive Risk:** Assessment
- **Technical Quality:** Comparison
- **Winner:** Human/AI/Tie and why

[Repeat for each rule]

---

## 8. SigmaHQ Match Comparison

### My SigmaHQ Research
- Rules found: X
- Time spent: X minutes
- Coverage identified: X%

### PERSEPTOR's SigmaHQ Matches
- Rules found: X
- Time spent: Automatic
- Coverage identified: X%

### Analysis
**Research thoroughness:**
- Did PERSEPTOR find rules I missed?
- Did I find rules PERSEPTOR missed?
- Quality of matching algorithm vs manual research

---

## 9. Overall Case 1 Winner

### Scoring

| Category | Human Score (1-10) | AI Score (1-10) | Winner | Notes |
|----------|-------------------|-----------------|--------|-------|
| IOC Extraction | X | X | Human/AI | [Reason] |
| TTP Extraction | X | X | Human/AI | [Reason] |
| MITRE Mapping | X | X | Human/AI | [Reason] |
| Threat Actors | X | X | Human/AI | [Reason] |
| Tools/Malware | X | X | Human/AI | [Reason] |
| Sigma Rules | X | X | Human/AI | [Reason] |
| YARA Rules | X | X | Human/AI | [Reason] |
| SigmaHQ Matching | X | X | Human/AI | [Reason] |
| Speed | X | X | Human/AI | [Reason] |
| Creativity | X | X | Human/AI | [Reason] |

**Total Score:**
- Human: X/100
- AI: X/100

**Overall Winner:** Human / AI / Tie

**Key Insights:**
- [What did you learn?]
```

---

### 🔍 Part 2: Detection QA Comparison

**⏰ START TIMER**

#### Step 1: Access PERSEPTOR QA Module

1. Navigate to the **QA** page in PERSEPTOR
2. Ensure your OpenAI API key is configured

#### Step 2: Run the Same Challenges

For each of the 5 challenges from Case 2, input the exact same prompt into PERSEPTOR:

**Challenge 1:**
```
Prompt: "Create a Sigma rule to detect possible DNS Tunneling Behavior"
```

**Challenge 2:**
```
Prompt: "Create a Sigma rule to detect possible file download from C2 server by using PowerShell"
```

**Challenge 3:**
```
Prompt: "Create a Sigma rule to detect credential dumping attempts targeting LSASS process"
```

**Challenge 4:**
```
Prompt: "Create a Sigma rule to detect malicious scheduled task creation for persistence"
```

**Challenge 5:**
```
Prompt: "Create a Sigma rule to detect lateral movement using Windows Management Instrumentation"
```

**⏰ Note PERSEPTOR's time for each challenge**

**⏰ STOP TIMER**

#### Step 3: Compare Detection Rules

```
File: perseptor_comparison/case2_detailed_comparison.md
```

**Comparison Template:**

```markdown
# Case 2: Detection QA - Comparison

## Time Comparison

| Challenge | My Time | PERSEPTOR Time | Difference |
|-----------|---------|----------------|------------|
| DNS Tunneling | X min | X sec | [Analysis] |
| PS Download | X min | X sec | [Analysis] |
| Credential Dump | X min | X sec | [Analysis] |
| Scheduled Task | X min | X sec | [Analysis] |
| WMI Lateral | X min | X sec | [Analysis] |
| **TOTAL** | **X min** | **X sec** | **X faster/slower** |

---

## Challenge 1: DNS Tunneling

### My Rule
```yaml
[Your rule]
```

**My Approach:**
- Detection logic reasoning
- Why I chose specific fields
- False positive considerations

### PERSEPTOR's Rule
```yaml
[PERSEPTOR's rule]
```

**PERSEPTOR's Approach:**
- What detection logic did it use?
- What fields did it select?
- What considerations did it include?

### Detailed Comparison

| Aspect | My Rule | PERSEPTOR Rule | Winner | Reason |
|--------|---------|----------------|--------|--------|
| **Detection Coverage** | [Description] | [Description] | Human/AI | [Why] |
| **Log Source Selection** | [My choice] | [AI choice] | Human/AI | [Why] |
| **Detection Logic** | [My logic] | [AI logic] | Human/AI | [Why] |
| **Field Selection** | [My fields] | [AI fields] | Human/AI | [Why] |
| **False Positive Handling** | [My approach] | [AI approach] | Human/AI | [Why] |
| **MITRE Mapping** | [My mapping] | [AI mapping] | Human/AI | [Why] |
| **Completeness** | X/10 | X/10 | Human/AI | [Why] |
| **Practicality** | X/10 | X/10 | Human/AI | [Why] |
| **Innovation** | X/10 | X/10 | Human/AI | [Why] |

**Key Differences:**
1. [Difference 1]
2. [Difference 2]
3. [Difference 3]

**What I learned from PERSEPTOR's approach:**
- [Insight 1]
- [Insight 2]

**What PERSEPTOR could learn from my approach:**
- [Insight 1]
- [Insight 2]

**Confidence Scores:**
- My confidence in my rule: X/10
- PERSEPTOR's confidence score: X/10
- PERSEPTOR's explanation: [If provided]

---

[Repeat the same detailed comparison for Challenges 2-5]

---

## Overall Case 2 Assessment

### Quantitative Comparison

| Metric | Human | AI | Winner |
|--------|-------|-------|--------|
| Total Time | X min | X sec | Human/AI |
| Avg Time per Rule | X min | X sec | Human/AI |
| Total Quality Score | X/50 | X/50 | Human/AI |
| Avg Quality per Rule | X/10 | X/10 | Human/AI |
| Detection Coverage | X% | X% | Human/AI |
| False Positive Risk | Low/Med/High | Low/Med/High | Human/AI |

### Qualitative Comparison

**Human Strengths:**
- [List strengths demonstrated]

**AI Strengths:**
- [List strengths demonstrated]

**Human Weaknesses:**
- [List weaknesses demonstrated]

**AI Weaknesses:**
- [List weaknesses demonstrated]

### Overall Winner: Human / AI / Tie

**Reasoning:**
[Detailed explanation of why this winner was determined]

---

## Combined Learning Insights

**What AI did better:**
1. [Insight]
2. [Insight]
3. [Insight]

**What I did better:**
1. [Insight]
2. [Insight]
3. [Insight]

**Collaboration Opportunities:**
- How human + AI could work together
- Where AI augments human capabilities
- Where human oversight is essential
```

---

## 💭 REFLECTION & DISCUSSION: AI vs Human Detection Engineering

This is the most important part of the workshop. Take time for deep reflection.

```
File: reflection/ai_vs_human_analysis.md
```

### 📊 Comprehensive Analysis Template

```markdown
# AI vs Human Detection Engineering: Deep Analysis

## Executive Summary

**Overall Workshop Experience:**
[2-3 paragraphs summarizing your experience]

**Key Finding:**
[Your main takeaway in 1-2 sentences]

---

## 1. Speed & Efficiency Analysis

### Time Comparison Summary

| Task Category | Human Time | AI Time | Speed Difference |
|--------------|-----------|---------|------------------|
| Threat Report Analysis | X min | X sec/min | AI X% faster |
| Detection Rule Creation | X min | X sec/min | AI X% faster |
| **Total Workshop Time** | **X min** | **X min** | **AI X% faster** |

### Observations

**Where speed matters:**
- [Analysis]

**Where speed doesn't matter:**
- [Analysis]

**Trade-offs:**
- [Analysis]

---

## 2. Quality & Accuracy Analysis

### IOC & TTP Extraction Quality

**Accuracy Metrics:**
- Human IOC accuracy: X%
- AI IOC accuracy: X%
- Human TTP accuracy: X%
- AI TTP accuracy: X%

**Quality Assessment:**

| Aspect | Human | AI | Analysis |
|--------|-------|-----|----------|
| Completeness | X/10 | X/10 | [Who was more thorough?] |
| Accuracy | X/10 | X/10 | [Who made fewer mistakes?] |
| Context Understanding | X/10 | X/10 | [Who understood nuances better?] |
| Relevance Filtering | X/10 | X/10 | [Who separated signal from noise better?] |

**Key Findings:**
- [Insight]

---

## 3. Detection Rule Quality Analysis

### Sigma Rule Quality Comparison

**Technical Quality:**
- Human syntax correctness: X%
- AI syntax correctness: X%

**Detection Effectiveness:**

| Rule | Human Coverage % | AI Coverage % | False Positive Risk (H/M/L) Human | False Positive Risk (H/M/L) AI |
|------|------------------|---------------|-----------------------------------|--------------------------------|
| Case 1 - Rule 1 | X% | X% | H/M/L | H/M/L |
| Case 1 - Rule 2 | X% | X% | H/M/L | H/M/L |
| Case 2 - Challenge 1 | X% | X% | H/M/L | H/M/L |
| Case 2 - Challenge 2 | X% | X% | H/M/L | H/M/L |
| [etc.] | | | | |

**Overall Assessment:**
- [Analysis]

---

## 4. Creativity & Innovation Analysis

### Novel Approaches

**Human Creative Elements:**
1. [Unique approach I used]
2. [Creative detection logic I invented]
3. [Innovative correlation I identified]

**AI Creative Elements:**
1. [Unique approach AI used]
2. [Creative detection logic AI generated]
3. [Innovative correlation AI identified]

**Creativity Winner:** Human / AI / Tie

**Reasoning:**
- [Detailed analysis]

---

## 5. Context Understanding & Domain Knowledge

### Threat Context

**Human Performance:**
- Understanding of threat landscape: X/10
- Ability to contextualize IOCs: X/10
- Recognition of TTPs: X/10
- Attribution reasoning: X/10

**AI Performance:**
- Understanding of threat landscape: X/10
- Ability to contextualize IOCs: X/10
- Recognition of TTPs: X/10
- Attribution reasoning: X/10

**Analysis:**

**Where human domain knowledge excelled:**
- [Specific examples]

**Where AI knowledge base excelled:**
- [Specific examples]

**Knowledge gaps in AI:**
- [What AI clearly didn't understand or missed]

**Knowledge gaps in human (me):**
- [What I didn't know that AI did]

---

## 6. PROS: Human Detection Engineering

### Strengths Demonstrated

1. **[Strength 1]**
   - Evidence: [Example from workshop]
   - Why it matters: [Analysis]
   - AI limitation in this area: [Comparison]

2. **[Strength 2]**
   - Evidence: [Example from workshop]
   - Why it matters: [Analysis]
   - AI limitation in this area: [Comparison]

3. **[Strength 3]**
   - Evidence: [Example from workshop]
   - Why it matters: [Analysis]
   - AI limitation in this area: [Comparison]

[Add more as needed]

### Human Advantages Summary

**What humans do better:**
- [List]

**Why these advantages exist:**
- [Analysis]

**Will these advantages persist?**
- [Future prediction]

---

## 7. CONS: Human Detection Engineering

### Weaknesses Demonstrated

1. **[Weakness 1]**
   - Evidence: [Example from workshop]
   - Impact: [How this affected results]
   - How AI overcame this: [Comparison]

2. **[Weakness 2]**
   - Evidence: [Example from workshop]
   - Impact: [How this affected results]
   - How AI overcame this: [Comparison]

3. **[Weakness 3]**
   - Evidence: [Example from workshop]
   - Impact: [How this affected results]
   - How AI overcame this: [Comparison]

[Add more as needed]

### Human Limitations Summary

**What humans struggle with:**
- [List]

**Why these limitations exist:**
- [Analysis]

**Can these be overcome?**
- [Analysis]

---

## 8. PROS: AI Detection Engineering (PERSEPTOR)

### Strengths Demonstrated

1. **[Strength 1]**
   - Evidence: [Example from workshop]
   - Why it matters: [Analysis]
   - Human limitation in this area: [Comparison]

2. **[Strength 2]**
   - Evidence: [Example from workshop]
   - Why it matters: [Analysis]
   - Human limitation in this area: [Comparison]

3. **[Strength 3]**
   - Evidence: [Example from workshop]
   - Why it matters: [Analysis]
   - Human limitation in this area: [Comparison]

[Add more as needed]

### AI Advantages Summary

**What AI does better:**
- [List]

**Why these advantages exist:**
- [Analysis]

**Implications for the field:**
- [Analysis]

---

## 9. CONS: AI Detection Engineering (PERSEPTOR)

### Weaknesses Demonstrated

1. **[Weakness 1]**
   - Evidence: [Example from workshop]
   - Impact: [How this affected results]
   - Why AI struggled: [Analysis]
   - Human advantage here: [Comparison]

2. **[Weakness 2]**
   - Evidence: [Example from workshop]
   - Impact: [How this affected results]
   - Why AI struggled: [Analysis]
   - Human advantage here: [Comparison]

3. **[Weakness 3]**
   - Evidence: [Example from workshop]
   - Impact: [How this affected results]
   - Why AI struggled: [Analysis]
   - Human advantage here: [Comparison]

[Add more as needed]

### AI Limitations Summary

**What AI struggles with:**
- [List]

**Why these limitations exist:**
- [Analysis]

**Can AI overcome these?**
- [Prediction and analysis]

---

## 10. What Did Each Miss?

### Critical Gaps in AI Analysis

**IOCs/TTPs AI Missed:**
1. [Item] - Why: [Reason] - Impact: [Severity]
2. [Item] - Why: [Reason] - Impact: [Severity]
3. [Item] - Why: [Reason] - Impact: [Severity]

**Detection Logic AI Missed:**
1. [Item] - Why: [Reason] - Impact: [Severity]
2. [Item] - Why: [Reason] - Impact: [Severity]

**Context AI Missed:**
1. [Item] - Why: [Reason] - Impact: [Severity]
2. [Item] - Why: [Reason] - Impact: [Severity]

**Analysis of AI Gaps:**
- [Why did AI miss these?]
- [What does this reveal about AI limitations?]

---

### Critical Gaps in Human Analysis (My Gaps)

**IOCs/TTPs I Missed:**
1. [Item] - Why: [Reason] - Impact: [Severity]
2. [Item] - Why: [Reason] - Impact: [Severity]
3. [Item] - Why: [Reason] - Impact: [Severity]

**Detection Logic I Missed:**
1. [Item] - Why: [Reason] - Impact: [Severity]
2. [Item] - Why: [Reason] - Impact: [Severity]

**Context I Missed:**
1. [Item] - Why: [Reason] - Impact: [Severity]
2. [Item] - Why: [Reason] - Impact: [Severity]

**Analysis of My Gaps:**
- [Why did I miss these?]
- [What does this reveal about human limitations?]
- [How can I improve?]

---

## 11. False Positives & False Negatives

### False Positive Analysis

**My Rules - False Positive Risk:**

| Rule | Risk Level | Why | How to Mitigate |
|------|-----------|-----|-----------------|
| [Rule 1] | H/M/L | [Reason] | [Mitigation] |
| [Rule 2] | H/M/L | [Reason] | [Mitigation] |
| [etc.] | | | |

**AI Rules - False Positive Risk:**

| Rule | Risk Level | Why | How to Mitigate |
|------|-----------|-----|-----------------|
| [Rule 1] | H/M/L | [Reason] | [Mitigation] |
| [Rule 2] | H/M/L | [Reason] | [Mitigation] |
| [etc.] | | | |

**Comparison:**
- Who designed rules with lower FP risk? [Analysis]
- Who considered edge cases better? [Analysis]
- Who balanced detection vs noise better? [Analysis]

---

### False Negative Analysis

**Potential False Negatives - My Rules:**
1. [Scenario] - Why my rule would miss it
2. [Scenario] - Why my rule would miss it

**Potential False Negatives - AI Rules:**
1. [Scenario] - Why AI rule would miss it
2. [Scenario] - Why AI rule would miss it

**Comparison:**
- Who had better coverage? [Analysis]
- Who considered evasion techniques better? [Analysis]

---

## 12. Trust & Validation

### Would I Trust These Rules in Production?

**My Own Rules:**

| Rule | Trust Level (1-10) | Why | What needs improvement |
|------|-------------------|-----|----------------------|
| [Rule 1] | X | [Reason] | [Improvements] |
| [Rule 2] | X | [Reason] | [Improvements] |
| [etc.] | | | |

**AI Generated Rules:**

| Rule | Trust Level (1-10) | Why | What needs improvement |
|------|-------------------|-----|----------------------|
| [Rule 1] | X | [Reason] | [Improvements] |
| [Rule 2] | X | [Reason] | [Improvements] |
| [etc.] | | | |

**Analysis:**
- Do I trust my own rules more than AI? Why?
- Would I use AI rules without modification? Why/why not?
- What validation would I require for AI rules?
- What validation would I require for human rules?

---

## 13. Human-AI Collaboration Model

### How Should They Work Together?

**Proposed Collaboration Workflow:**

```
Step 1: [Who does what]
Step 2: [Who does what]
Step 3: [Who does what]
...
```

**Role Division:**

| Task | Best Performed By | Reason | How the Other Assists |
|------|------------------|--------|---------------------|
| Initial report triage | Human/AI | [Reason] | [How other helps] |
| IOC extraction | Human/AI | [Reason] | [How other helps] |
| TTP analysis | Human/AI | [Reason] | [How other helps] |
| MITRE mapping | Human/AI | [Reason] | [How other helps] |
| Rule generation | Human/AI | [Reason] | [How other helps] |
| Rule validation | Human/AI | [Reason] | [How other helps] |
| Context understanding | Human/AI | [Reason] | [How other helps] |
| Quality assurance | Human/AI | [Reason] | [How other helps] |

**Collaboration Benefits:**
1. [Benefit]
2. [Benefit]
3. [Benefit]

**Collaboration Challenges:**
1. [Challenge]
2. [Challenge]
3. [Challenge]

---

## 14. Future of Detection Engineering

### Predictions

**In 1 year:**
- [Prediction about AI capabilities]
- [Prediction about human role]
- [Prediction about the field]

**In 5 years:**
- [Prediction about AI capabilities]
- [Prediction about human role]
- [Prediction about the field]

**In 10 years:**
- [Prediction about AI capabilities]
- [Prediction about human role]
- [Prediction about the field]

### Will AI Replace Human Detection Engineers?

**My Answer:** Yes / No / Partially

**Reasoning:**
[Detailed explanation based on workshop experience]

**What will change:**
- [Change 1]
- [Change 2]
- [Change 3]

**What will stay the same:**
- [Constant 1]
- [Constant 2]
- [Constant 3]

**What skills will humans need:**
- [Skill 1]
- [Skill 2]
- [Skill 3]

---

## 15. Personal Development Plan

### What I Learned

**Technical Learnings:**
1. [Learning]
2. [Learning]
3. [Learning]

**Process Learnings:**
1. [Learning]
2. [Learning]
3. [Learning]

**Strategic Learnings:**
1. [Learning]
2. [Learning]
3. [Learning]

### How I'll Improve

**Immediate Actions (Next Week):**
- [ ] [Action]
- [ ] [Action]
- [ ] [Action]

**Short-term Goals (Next Month):**
- [ ] [Goal]
- [ ] [Goal]
- [ ] [Goal]

**Long-term Goals (Next Year):**
- [ ] [Goal]
- [ ] [Goal]
- [ ] [Goal]

### How I'll Use AI in My Work

**Will Use AI For:**
1. [Use case] - Because [reason]
2. [Use case] - Because [reason]
3. [Use case] - Because [reason]

**Won't Use AI For:**
1. [Use case] - Because [reason]
2. [Use case] - Because [reason]
3. [Use case] - Because [reason]

**Will Always Human-Validate:**
1. [What AI does]
2. [What AI does]
3. [What AI does]

---

## 16. Final Verdict

### Workshop Scoreboard

**Final Scores:**

| Category | Weight | Human Score | AI Score | Weighted Human | Weighted AI |
|----------|--------|-------------|----------|----------------|-------------|
| IOC Extraction | 10% | X/10 | X/10 | X | X |
| TTP Extraction | 10% | X/10 | X/10 | X | X |
| MITRE Mapping | 10% | X/10 | X/10 | X | X |
| Threat Actors | 5% | X/10 | X/10 | X | X |
| Tools/Malware | 5% | X/10 | X/10 | X | X |
| Sigma Rules | 20% | X/10 | X/10 | X | X |
| YARA Rules | 10% | X/10 | X/10 | X | X |
| SigmaHQ Research | 5% | X/10 | X/10 | X | X |
| Detection QA | 15% | X/10 | X/10 | X | X |
| Creativity | 5% | X/10 | X/10 | X | X |
| Speed | 5% | X/10 | X/10 | X | X |
| **TOTAL** | **100%** | | | **X/10** | **X/10** |

### THE WINNER: **Human** / **AI** / **Tie**

### Why:
[Comprehensive explanation of the winner]

---

## 17. Message to the Security Community

**To fellow detection engineers:**

[Your message about AI in detection engineering based on this workshop experience]

**To security leaders:**

[Your recommendations about AI adoption in detection engineering]

**To AI developers:**

[What you'd like to see improved in AI detection engineering tools]

---

## 18. Would I Do It Again?

**Manual Analysis:** Yes / No - Because: [Reason]

**Using PERSEPTOR:** Yes / No - Because: [Reason]

**Combined Approach:** Yes / No - Because: [Reason]

**Recommendation to Others:**
[Your recommendation]

---

## 19. Unexpected Findings

**Surprises:**

1. **[Surprise 1]**
   - What I expected: [Expectation]
   - What actually happened: [Reality]
   - Why this matters: [Analysis]

2. **[Surprise 2]**
   - What I expected: [Expectation]
   - What actually happened: [Reality]
   - Why this matters: [Analysis]

3. **[Surprise 3]**
   - What I expected: [Expectation]
   - What actually happened: [Reality]
   - Why this matters: [Analysis]

---

## 20. Final Thoughts

[Free-form reflection on the entire workshop experience. Write about anything that didn't fit in the structured sections above. This is your space for deep thoughts, philosophical considerations, concerns, excitement, or anything else about AI vs Human in cybersecurity.]

---

**Workshop Completed:** [Date and Time]  
**Total Time Invested:** [X hours]  
**Worth It:** Yes / No - Because: [Reason]

**#DEATHCon2025 #HumanVsAI #DetectionEngineering #PERSEPTOR**
```

---

## 📚 Essential Resources

### 🔗 MITRE ATT&CK Resources
- **MITRE ATT&CK Website:** https://attack.mitre.org/
- **ATT&CK Navigator:** https://mitre-attack.github.io/attack-navigator/
- **ATT&CK Techniques List:** https://attack.mitre.org/techniques/enterprise/

### 🔗 Sigma Resources
- **SigmaHQ Repository:** https://github.com/SigmaHQ/sigma
- **Sigma Rule Creation Guide:** https://github.com/SigmaHQ/sigma/wiki/Rule-Creation-Guide
- **Sigma Specification:** https://github.com/SigmaHQ/sigma-specification
- **Sigma Converter Tools:** https://github.com/SigmaHQ/sigma/tree/master/tools

### 🔗 YARA Resources
- **YARA Documentation:** https://yara.readthedocs.io/
- **YARA Rules Repository:** https://github.com/Yara-Rules/rules
- **Writing YARA Rules:** https://yara.readthedocs.io/en/stable/writingrules.html

### 🔗 Detection Engineering Resources
- **Florian Roth's Sigma Best Practices:** https://github.com/Neo23x0/Talks
- **Detection Engineering Guide:** https://www.socinvestigation.com/
- **Threat Hunting Resources:** https://github.com/threat-hunting

### 🔗 Threat Intelligence Sources
- **MISP Project:** https://www.misp-project.org/
- **AlienVault OTX:** https://otx.alienvault.com/
- **Threat Intelligence Feeds:** Various (workshop specific)

---

## 🏆 Workshop Completion Certificate

After completing all phases:

```
===============================================
    DEATHCON 2025 AMSTERDAM
    Workshop Completion Certificate
===============================================

This certifies that:

[YOUR NAME]

Successfully completed the 
"Human vs AI: Detection Engineering Challenge"

Workshop Components Completed:
✅ Case 1: Threat Report Analysis
✅ Case 2: Detection Rule Q&A Challenge
✅ AI Comparison with PERSEPTOR
✅ Reflection & Analysis

Total Time Invested: ____ hours
Workshop Date: November 8-9, 2025

Final Score: Human ____ vs AI ____

Signature: ___________________
Aytek AYTEMUR - Workshop Leader

#DEATHCon2025 #DetectionEngineering
===============================================
```

---

## 📧 Contact & Community

### Workshop Leader
- **Name:** Aytek AYTEMUR
- **Email:** aytek.aytemur@outlook.com
- **GitHub:** [dipsh0v](https://github.com/dipsh0v)
- **PERSEPTOR Repository:** https://github.com/dipsh0v/PERSEPTOR

### Community
- **Workshop Discord:** [Join discussion]
- **DEATHCon Community:** [Community links]
- **LinkedIn:** Share your results with #DEATHCon2025

### Share Your Results!

After completing the workshop:
1. **Share your final verdict** (Human vs AI winner)
2. **Post key insights** on social media
3. **Contribute to discussion** about AI in security
4. **Connect with other participants**

**Hashtags:**
- #DEATHCon2025
- #PERSEPTOR
- #DetectionEngineering
- #HumanVsAI
- #ThreatIntelligence
- #CyberSecurity

---

## 🙏 Acknowledgments

This workshop and PERSEPTOR platform are made possible by:

- **OpenAI** - For powerful AI capabilities that power PERSEPTOR
- **MITRE Corporation** - For the ATT&CK framework
- **SigmaHQ Community** - For Sigma detection rule standards
- **YARA Community** - For pattern matching standards
- **DEATHCon Organizers** - For hosting this amazing conference
- **All Participants** - For taking on this challenge

---

## ⚠️ Important Notes

### Data Privacy
- All analysis performed in this workshop is for educational purposes
- Do not analyze proprietary or classified threat reports without authorization
- Ensure compliance with your organization's data handling policies

### API Usage
- Monitor your OpenAI API usage and costs
- Set appropriate usage limits
- Use your own API keys, don't share them

### Ethical Considerations
- Use detection engineering knowledge responsibly
- Do not create rules for malicious purposes
- Share knowledge to improve community security

---

## 🎯 Success Metrics

You've successfully completed the workshop if you:

- ✅ **Completed Case 1:** Full threat report analysis with all components
- ✅ **Completed Case 2:** Created 5 Sigma rules for detection scenarios
- ✅ **Ran PERSEPTOR:** Compared AI results with your manual analysis
- ✅ **Deep Reflection:** Completed comprehensive AI vs Human analysis
- ✅ **Documented Everything:** Created all required files and comparisons
- ✅ **Learned Something:** Gained new insights about detection engineering and AI

---

<div align="center">

## 🐉 Ready for the Challenge?

**This is not just a workshop—it's a journey to understand the future of detection engineering.**

**May your analysis be thorough, your rules be precise, and your insights be profound.**

![DEATHCon 2025](https://img.shields.io/badge/Challenge-Accepted-green?style=for-the-badge&logo=checkmark&logoColor=white)

**Let the Human vs AI battle begin! 🏆**

---

*DEATHCon 2025 Amsterdam - Detection Engineering and Threat Hunting Conference*  
*November 8-9, 2025 - The Netherlands*

</div>
