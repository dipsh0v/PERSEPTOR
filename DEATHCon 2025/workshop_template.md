# 🎯 DEATHCon 2025 Workshop Challenge Template

## 📋 Threat Analysis Worksheet

**Participant Name:** _________________________  
**Date:** _________________________  
**Workshop Session:** _________________________  

---

## 📊 Phase 1: Manual Threat Analysis

### 🔗 Threat Report Information
- **URL:** _________________________
- **Title:** _________________________
- **Date Published:** _________________________
- **Source:** _________________________

### 📝 Executive Summary
```
[Write a comprehensive summary of the threat here]
```

### 🎯 Key TTPs (Tactics, Techniques, Procedures)
| TTP | Description | Impact |
|-----|-------------|---------|
| | | |
| | | |
| | | |

### 🗺️ MITRE ATT&CK Techniques
| Technique ID | Technique Name | Description | Detection Opportunity |
|--------------|----------------|-------------|----------------------|
| | | | |
| | | | |
| | | | |

### 🔍 IOCs (Indicators of Compromise)

#### IP Addresses
```
[List IP addresses here]
```

#### Domains/URLs
```
[List domains and URLs here]
```

#### File Hashes
```
[List file hashes here]
```

#### Registry Keys
```
[List registry keys here]
```

### 👤 Threat Actors
| Actor Name | Type | Description | Attribution Confidence |
|------------|------|-------------|----------------------|
| | | | |
| | | | |

### 🛠️ Tools & Malware
| Name | Type | Description | Capabilities |
|------|------|-------------|--------------|
| | | | |
| | | | |

---

## 📜 Phase 2: Detection Rules Generation

### 🎯 Sigma Rules

#### Rule 1: [Rule Name]
```yaml
title: [Rule Title]
id: [Generated UUID]
status: experimental
description: [Rule Description]
author: [Your Name]
date: [Date]
modified: [Date]
level: medium
tags:
    - attack.technique_id
    - attack.tactic
detection:
    selection:
        [Detection Logic]
    condition: selection
falsepositives:
    - [False Positive Scenarios]
level: medium
```

#### Rule 2: [Rule Name]
```yaml
title: [Rule Title]
id: [Generated UUID]
status: experimental
description: [Rule Description]
author: [Your Name]
date: [Date]
modified: [Date]
level: medium
tags:
    - attack.technique_id
    - attack.tactic
detection:
    selection:
        [Detection Logic]
    condition: selection
falsepositives:
    - [False Positive Scenarios]
level: medium
```

### 🎯 YARA Rules

#### Rule 1: [Rule Name]
```yaml
rule [RuleName] {
    meta:
        description = "[Rule Description]"
        author = "[Your Name]"
        date = "[Date]"
        reference = "[Reference URL]"
        hash = "[File Hash]"
    strings:
        $s1 = "[String Pattern 1]"
        $s2 = "[String Pattern 2]"
    condition:
        any of them
}
```

---

## 🔍 Phase 3: SigmaHQ Integration

### 📚 Existing Rule Analysis
| SigmaHQ Rule | Relevance | Coverage | Notes |
|--------------|-----------|----------|-------|
| | | | |
| | | | |

### 🎯 Rule Mapping
```
[Document how existing SigmaHQ rules map to your threat analysis]
```

### 📈 Coverage Gaps
```
[Identify areas where existing rules don't cover the threat]
```

---

## 🤖 Phase 4: AI Comparison

### 🔗 PERSEPTOR Analysis Results
- **Analysis URL:** _________________________
- **Processing Time:** _________________________
- **Confidence Score:** _________________________

### 📊 Comparison Matrix

| Aspect | Human Analysis | AI Analysis | Winner |
|--------|----------------|-------------|---------|
| **Completeness** | /10 | /10 | |
| **Accuracy** | /10 | /10 | |
| **Speed** | /10 | /10 | |
| **Rule Quality** | /10 | /10 | |
| **Innovation** | /10 | /10 | |

### 🎯 Key Differences
```
[Document major differences between human and AI analysis]
```

### 💡 Insights & Lessons Learned
```
[What did you learn from this comparison?]
```

---

## 🏆 Final Assessment

### 📊 Self-Evaluation
- **Overall Performance:** /10
- **Areas of Strength:** _________________________
- **Areas for Improvement:** _________________________
- **Most Challenging Aspect:** _________________________

### 🎯 Workshop Goals Achievement
- [ ] Completed manual threat analysis
- [ ] Generated detection rules
- [ ] Analyzed SigmaHQ rules
- [ ] Compared with AI results
- [ ] Documented insights

### 🚀 Next Steps
```
[What will you do differently in future threat analysis?]
```

---

## 📝 Additional Notes
```
[Any additional observations, questions, or insights]
```

---

**Workshop Completed:** ✅  
**Time Taken:** _________________________  
**Final Score:** _________________________  

---

*This template is part of DEATHCon 2025 - Human vs AI Detection Engineering Challenge*
