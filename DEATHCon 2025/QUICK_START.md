# 🚀 DEATHCon 2025 Workshop - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. **Prerequisites Check**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check Node.js version  
node --version     # Should be 16+

# Check Git
git --version
```

### 2. **Get Your OpenAI API Key**
- Go to [OpenAI Platform](https://platform.openai.com/api-keys)
- Create a new API key
- Copy and save it securely

### 3. **Setup Workshop Environment**
```bash
# Navigate to workshop directory
cd "DEATHCon 2025"

# Run setup script
python3 setup_workshop.py

# Follow the prompts and complete setup
```

### 4. **Start PERSEPTOR (Optional)**
```bash
# Terminal 1 - Backend
cd ../
python3 api/app.py

# Terminal 2 - Frontend  
cd perseptor-ui
npm start
```

### 5. **You're Ready! 🎉**
- Open your workspace: `DEATHCon 2025/workspace/`
- Use the template: `my_workshop_template.md`
- Join the live stream when workshop starts

---

## 📋 Workshop Checklist

### ✅ Before Workshop
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] OpenAI API key ready
- [ ] Workshop setup completed
- [ ] Template downloaded
- [ ] Internet connection stable

### ✅ During Workshop
- [ ] **Phase 1 (30 min):** Manual threat analysis
- [ ] **Phase 2 (15 min):** SigmaHQ rule search
- [ ] **Phase 3 (15 min):** AI comparison with PERSEPTOR
- [ ] **Submit results** before time expires

### ✅ After Workshop
- [ ] Review your results
- [ ] Compare with AI analysis
- [ ] Submit final report
- [ ] Join discussion and networking

---

## 🎯 Workshop Phases Overview

### 🔍 Phase 1: Manual Analysis (30 minutes)
**Goal:** Extract intelligence from threat report

**Deliverables:**
- Threat summary
- TTPs and MITRE techniques
- IOCs (IPs, domains, hashes)
- Threat actors and tools
- Sigma and YARA rules

### 🔍 Phase 2: SigmaHQ Integration (15 minutes)
**Goal:** Find existing detection rules

**Deliverables:**
- List of relevant SigmaHQ rules
- Rule mapping and coverage analysis
- Gap identification

### 🤖 Phase 3: AI Comparison (15 minutes)
**Goal:** Compare with PERSEPTOR AI

**Deliverables:**
- AI analysis results
- Side-by-side comparison
- Insights and lessons learned

---

## 🛠️ Essential Tools

### 📝 Text Editor
- **VS Code** (Recommended)
- **Sublime Text**
- **Vim/Nano**

### 🌐 Web Browser
- **Chrome** (Recommended)
- **Firefox**
- **Safari**

### 🔗 Essential Websites
- [MITRE ATT&CK](https://attack.mitre.org/)
- [SigmaHQ Repository](https://github.com/SigmaHQ/sigma)
- [YARA Rules](https://github.com/Yara-Rules/rules)
- [PERSEPTOR](http://localhost:3000) (if running locally)

---

## 📊 Scoring System

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Completeness** | 25% | How thoroughly you covered all aspects |
| **Accuracy** | 25% | Correctness of extracted intelligence |
| **Rule Quality** | 20% | Effectiveness of generated detection rules |
| **Innovation** | 15% | Creative approaches and insights |
| **Speed** | 15% | How quickly you completed the analysis |

---

## 🆘 Troubleshooting

### ❌ Setup Issues
```bash
# If Python version is too old
brew install python3  # macOS
sudo apt install python3.8  # Ubuntu

# If Node.js is missing
brew install node  # macOS
sudo apt install nodejs npm  # Ubuntu
```

### ❌ PERSEPTOR Issues
```bash
# If backend won't start
cd ../
pip install -r requirements.txt
python3 api/app.py

# If frontend won't start
cd perseptor-ui
npm install
npm start
```

### ❌ API Key Issues
- Verify key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)
- Check you have sufficient credits
- Ensure key has proper permissions

---

## 🎉 Success Tips

### 💡 Analysis Tips
- **Read thoroughly:** Don't rush the initial reading
- **Take notes:** Document everything as you go
- **Be systematic:** Follow the template structure
- **Think creatively:** Look for unique insights

### 🎯 Rule Writing Tips
- **Be specific:** Avoid overly broad rules
- **Consider false positives:** Think about legitimate use cases
- **Use proper syntax:** Follow Sigma/YARA standards
- **Test your logic:** Validate rule structure

### 🤖 AI Comparison Tips
- **Be objective:** Compare fairly and honestly
- **Look for patterns:** Identify where each excels
- **Learn from differences:** Use insights for improvement
- **Document everything:** Record your observations

---

## 📞 Support

### 🆘 Getting Help
- **Discord:** `#deathcon-workshop` channel
- **Email:** [AAytemur1864@outlook.com](mailto:AAytemur1864@outlook.com)
- **GitHub:** [dipsh0v/PERSEPTOR](https://github.com/dipsh0v/PERSEPTOR)

### 🌐 Community
- **LinkedIn:** [DEATHCon 2025](https://linkedin.com/company/deathcon)
- **Twitter:** [@DEATHCon2025](https://twitter.com/DEATHCon2025)

---

## 🏆 Awards & Recognition

### 🥇 Competition Categories
- **Overall Champion:** Best combined score
- **Accuracy Master:** Most accurate analysis
- **Speed Demon:** Fastest completion
- **Innovation Award:** Most creative approach
- **AI Collaboration:** Best human-AI teamwork

### 🎖️ Recognition
- Digital certificates for all participants
- Special DEATHCon 2025 workshop badges
- LinkedIn endorsements and recommendations
- Networking opportunities with industry experts

---

<div align="center">

## 🐉 Ready to Compete?

**The ultimate Human vs AI challenge awaits!**

![DEATHCon Dragon](https://img.shields.io/badge/DEATHCon-Dragon-red?style=for-the-badge&logo=dragon&logoColor=white)

**May the best analyst win! 🏆**

</div>

---

*This quick start guide is part of DEATHCon 2025 - Detection Engineering and Threat Hunting Conference*
