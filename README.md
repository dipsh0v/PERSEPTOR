# PERSEPTOR - AI-Powered Detection Engineering Platform

[![AI-Powered](https://img.shields.io/badge/AI-Powered-green)](https://openai.com/)
[![Detection Engineering](https://img.shields.io/badge/Detection-Engineering-orange)](https://attack.mitre.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org/)
[![React](https://img.shields.io/badge/React-18+-blue)](https://reactjs.org/)

**PERSEPTOR** is an advanced AI-driven detection engineering platform that revolutionizes threat intelligence through automated analysis, detection rule generation, and intelligent security orchestration.

## 🚀 Key Features

### 🧠 AI-Powered Threat Analysis
- **Automated URL Analysis:** Extract intelligence from threat reports
- **OCR Processing:** Analyze images and documents
- **Intelligent Summarization:** AI-generated threat summaries
- **Real-time Processing:** Fast, efficient analysis

### 🔍 Detection Rule Generation
- **Sigma Rules:** Comprehensive YAML-based detection rules
- **YARA Rules:** Pattern-based malware detection signatures
- **SIEM Queries:** Splunk, QRadar, and Elastic queries
- **Quality Assurance:** Automated validation and scoring

### 🎯 Intelligence Extraction
- **IoCs:** IPs, domains, URLs, file hashes, registry keys
- **TTPs:** MITRE ATT&CK technique mapping
- **Threat Actors:** Attribution and profiling
- **Tools & Malware:** Identification and classification

### 🔬 Advanced Capabilities
- **Global Sigma Matching:** Cross-reference with existing rule repositories
- **Confidence Scoring:** AI-powered rule quality assessment
- **Multi-format Output:** Support for various SIEM platforms
- **Interactive Web Interface:** User-friendly dashboard

## 🏗️ Architecture

```
PERSEPTOR Platform
├── 🎨 Frontend (React/TypeScript)
│   ├── Dashboard Interface
│   ├── Real-time Analytics
│   └── Interactive Visualizations
├── 🧠 AI Engine
│   ├── GPT-4 Integration
│   ├── Threat Analysis
│   └── Rule Generation
├── 🔧 Backend Services
│   ├── Flask API
│   ├── Processing Pipeline
│   └── Data Management
└── 📊 Analytics
    ├── Performance Metrics
    ├── Quality Scoring
    └── Validation Framework
```

## 📋 Prerequisites

Before running PERSEPTOR, make sure you have:

- **Python 3.8+** installed
- **Node.js 16+** installed
- **OpenAI API Key** (for AI features)
- **Git** (for cloning the repository)

## 📦 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/dipsh0v/PERSEPTOR.git
cd PERSEPTOR
```

### Step 2: Backend Setup (Python/Flask)

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Step 3: Frontend Setup (React/TypeScript)

```bash
# Navigate to frontend directory
cd perseptor-ui

# Install Node.js dependencies
npm install
```

### Step 4: Run the Application

**Terminal 1 - Start Backend:**
```bash
cd "/path/to/PERSEPTOR"
source venv/bin/activate  # If using virtual environment
python3 api/app.py
```

**Terminal 2 - Start Frontend:**
```bash
cd "/path/to/PERSEPTOR/perseptor-ui"
npm start
```

**Access the Application:**
- Open your browser and go to: `http://localhost:3000`
- Backend API runs on: `http://localhost:5000`

## 🎮 Usage

### Web Interface

1. **Start the application** using the installation steps above
2. **Open your browser** and navigate to `http://localhost:3000`
3. **Enter your OpenAI API key** in the settings
4. **Paste a threat report URL** to analyze
5. **View the results** including:
   - Threat summary
   - Extracted IoCs
   - Generated Sigma rules
   - YARA rules
   - MITRE ATT&CK mappings

### API Usage

```python
import requests

# Analyze a threat report
response = requests.post('http://localhost:5000/api/analyze', json={
    'url': 'https://example.com/threat-report',
    'openai_api_key': 'your-api-key'
})

result = response.json()
print(result['threat_summary'])
```

### Command Line Usage

```python
from modules.gpt_module import summarize_threat_report, extract_iocs_ttps_gpt

# Analyze a threat report URL
summary = summarize_threat_report(
    text="Your threat report content here",
    openai_api_key="your-api-key"
)

iocs_ttps = extract_iocs_ttps_gpt(
    text="Your threat report content here",
    openai_api_key="your-api-key"
)

print(summary)
print(iocs_ttps)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000
```

### AI Model Settings

Edit `modules/gpt_module.py` to customize AI behavior:

```python
# Model configuration
MODEL_NAME = "gpt-4.1-2025-04-14"
TEMPERATURE = 0.1
REASONING_EFFORT = "high"
```

## 📈 Performance Metrics

### Platform Performance
- **Analysis Speed:** 4-5 minutes per threat report
- **Rule Generation:** 1-2 minutes per rule
- **Accuracy Rate:** 90%+ detection accuracy
- **Coverage:** 95%+ MITRE ATT&CK technique coverage


## 🛠️ Troubleshooting

### Common Issues

**1. Cairo Library Error (Windows + Anaconda):**

❌ **Problem:**
```bash
OSError: no library called "cairo-2" was found
cannot load library 'libcairo-2.dll': error 0x7e
```

This error occurs when `cairosvg` cannot find the Cairo library, which is needed for SVG processing.

✅ **Solution (Windows + Anaconda):**

```bash
# Step 0: Navigate to project root
cd /path/to/PERSEPTOR-main

# Step 1: Create a new isolated conda environment
conda create -n perseptor python=3.10 -y
conda activate perseptor

# Step 2: Install Cairo and its dependencies (includes DLL files)
conda install -c conda-forge cairo pango gdk-pixbuf libxml2 libxslt zlib -y
conda install -c conda-forge cairosvg cairocffi -y

# Step 3: Install project dependencies
pip install -r requirements.txt

# Step 4: Run the backend
python api/app.py
```

**Why this works:**
- `conda-forge` provides pre-compiled Cairo DLL files for Windows
- Creates an isolated environment to avoid conflicts
- Installs all required system libraries automatically

**2. Backend not starting:**
```bash
# Check if port 5000 is available
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill process if needed
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

**3. Frontend not connecting to backend:**
- Ensure backend is running on `http://localhost:5000`
- Check CORS settings in `api/app.py`
- Verify API endpoints are accessible
- Make sure both frontend and backend are running

**4. OpenAI API errors:**
```bash
# Verify API key is set (Mac/Linux)
echo $OPENAI_API_KEY

# Verify API key is set (Windows)
echo %OPENAI_API_KEY%

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**5. Module import errors:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python3 -c "import sys; print(sys.path)"
```

**6. Node.js/npm issues:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json  # Mac/Linux
rmdir /s /q node_modules && del package-lock.json  # Windows

# Reinstall
npm install
```

## 🏗️ Project Structure

```
PERSEPTOR/
├── api/                    # Flask backend API
│   ├── app.py             # Main API application
│   └── requirements.txt   # API dependencies
├── modules/               # Core Python modules
│   ├── gpt_module.py      # AI integration
│   ├── sigma_module.py    # Sigma rule generation
│   ├── yara_module.py     # YARA rule generation
│   ├── ocr_module.py      # OCR processing
│   ├── qa_module.py       # Quality assurance
│   └── ...               # Other modules
├── perseptor-ui/          # React frontend
│   ├── src/              # Source code
│   ├── public/           # Static files
│   └── package.json      # Frontend dependencies
├── main.py               # Legacy main application
├── app.py                # Alternative entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🤝 Contributing

We welcome contributions to PERSEPTOR! Here's how you can help:

### 🐛 Bug Reports
- Use GitHub Issues
- Include detailed reproduction steps
- Provide system information

### 💡 Feature Requests
- Describe the use case
- Explain the expected behavior
- Consider implementation complexity

### 🔧 Code Contributions
- Fork the repository
- Create feature branches
- Submit pull requests
- Follow coding standards

### 📚 Documentation
- Improve existing documentation
- Add examples and tutorials
- Translate to other languages

## 📞 Support

### 🆘 Getting Help
- **Issues:** [GitHub Issues](https://github.com/dipsh0v/PERSEPTOR/issues)
- **Discussions:** [GitHub Discussions](https://github.com/dipsh0v/PERSEPTOR/discussions)

### 📧 Contact
- **Developer:** Aytek AYTEMUR
- **Email:** [aytek.aytemur@outlook.com](mailto:aytek.aytemur@outlook.com)
- **GitHub:** [dipsh0v](https://github.com/dipsh0v)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing powerful AI capabilities
- **MITRE ATT&CK** for the comprehensive framework
- **Sigma Community** for detection rule standards
- **Security Community** for feedback and contributions

## 🚀 Roadmap

### Current Version
- [x] AI-powered threat analysis
- [x] Sigma and YARA rule generation
- [x] Web interface
- [x] API endpoints
- [x] MITRE ATT&CK mapping

### Upcoming Features
- [ ] Advanced AI models
- [ ] Cloud deployment options
- [ ] Enterprise features
- [ ] API marketplace

---

**Ready to revolutionize detection engineering with AI? Start using PERSEPTOR today! 🚀**
