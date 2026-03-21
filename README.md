<p align="center">
  <img src="https://img.shields.io/badge/PERSEPTOR-v2.0-6366f1?style=for-the-badge&labelColor=1e1b4b" alt="PERSEPTOR v2.0" />
</p>

<h1 align="center">PERSEPTOR</h1>

<p align="center">
  <strong>AI-Powered Detection Engineering Platform</strong><br/>
  Transform threat intelligence into actionable detection rules — automatically.
</p>

<p align="center">
  <a href="#quickstart"><img src="https://img.shields.io/badge/Get_Started-6366f1?style=for-the-badge" alt="Get Started" /></a>
  <a href="https://github.com/dipsh0v/PERSEPTOR/issues"><img src="https://img.shields.io/badge/Report_Bug-ec4899?style=for-the-badge" alt="Report Bug" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/react-19-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/typescript-4.9-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/flask-2.3+-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License" />
</p>

---

## The Problem

Security teams spend **hours** manually reading threat reports, extracting indicators of compromise, mapping MITRE ATT&CK techniques, and writing detection rules. This process is:

- **Slow** — A single threat report can take 2-4 hours to fully operationalize
- **Error-prone** — Manual extraction misses IoCs and TTPs
- **Inconsistent** — Rule quality varies between analysts
- **Not scalable** — New threats emerge faster than teams can respond

## The Solution

**PERSEPTOR** automates the entire detection engineering pipeline. Paste a threat report URL, and in minutes you get:

| Output | Description |
|--------|-------------|
| **Threat Summary** | Structured intelligence brief with key findings |
| **IoC Extraction** | IPs, domains, URLs, hashes, registry keys, mutexes |
| **TTP Mapping** | Automated MITRE ATT&CK technique identification |
| **Sigma Rules** | Production-ready detection rules (AI-generated + IoC-based) |
| **YARA Rules** | Pattern-based malware detection signatures |
| **SIEM Queries** | Ready-to-deploy queries for Splunk, QRadar, Elastic, Sentinel |
| **Hunting Queries** | Proactive threat hunting queries per SIEM platform |
| **Atomic Tests** | Red Team test scenarios mapped to detections |
| **QA Scoring** | Automated quality validation with confidence scores |

---

## Key Features

### Multi-Provider AI Engine
Switch between AI providers on the fly — no vendor lock-in:

| Provider | Models |
|----------|--------|
| **OpenAI** | GPT-4.1, GPT-4.1 Mini, GPT-4o, O4 Mini (Reasoning), O3 Mini |
| **Anthropic** | Claude Sonnet 4, Claude Opus 4, Claude Haiku 4.5 |
| **Google** | Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0 Flash |

### Global Sigma Match Engine
Cross-reference analysis results against **2,750+ community Sigma rules** from the official SigmaHQ repository. Automatically surface existing detections that match the threat — before you write a single rule.

### Atomic Red Team Integration
Generate executable test scenarios aligned with your Sigma rules. Validate that your detections actually fire against simulated attack techniques.

### Real-Time SSE Streaming
Watch the analysis pipeline execute step-by-step with server-sent events. Every phase — from content extraction to rule generation — streams progress to the UI in real time.

### Production-Grade Security
- **Session encryption** with Fernet (cryptography library)
- **Rate limiting** via token bucket algorithm
- **SSRF prevention** with private IP blocking and DNS resolution checks
- **Input sanitization** and request size validation
- **CORS** with configurable allowed origins

---

## Architecture

```
PERSEPTOR v2.0
│
├── perseptor-ui/                    # Frontend (React 19 + TypeScript + MUI 7)
│   ├── pages/
│   │   ├── Dashboard                # URL/PDF input → full analysis pipeline
│   │   ├── Reports                  # Historical analysis results
│   │   ├── CreatedRules             # Generated Sigma/YARA rules library
│   │   ├── QA                       # Quality scoring dashboard
│   │   ├── Settings                 # Provider/model/API key configuration
│   │   └── AboutPerseptor           # Platform info
│   ├── components/
│   │   ├── MitreNavigator           # ATT&CK technique heatmap
│   │   ├── ConfidenceGauge          # Visual QA score gauge
│   │   ├── ProgressTracker          # SSE pipeline progress
│   │   └── AnalysisProgressOverlay  # Full-screen analysis overlay
│   └── store/                       # Redux Toolkit state management
│
├── api/
│   └── app.py                       # Flask API (13 endpoints, SSE streaming)
│
├── modules/
│   ├── ai_engine.py                 # Multi-provider AI orchestration
│   ├── content_fetcher.py           # URL fetch, OCR, Playwright rendering
│   ├── sigma_generator.py           # Sigma rule generation engine
│   ├── yara_generator.py            # YARA rule generation engine
│   ├── siem_query_generator.py      # Splunk/QRadar/Elastic/Sentinel query builder
│   ├── sigma_matcher.py             # Global Sigma Match (2,750+ rules)
│   ├── quality_analyzer.py          # QA scoring and validation framework
│   ├── pdf_reporter.py              # PDF report generation
│   ├── mitre_mapping.py             # MITRE ATT&CK technique mapper
│   ├── security.py                  # SSRF prevention, API key validation
│   ├── session_manager.py           # Fernet-encrypted session management
│   ├── middleware.py                # Rate limiting, request validation
│   ├── config.py                    # Central configuration (dataclasses)
│   ├── ai/                          # Provider abstraction layer
│   │   ├── openai_provider.py       # OpenAI implementation
│   │   ├── anthropic_provider.py    # Anthropic implementation
│   │   ├── google_provider.py       # Google Gemini implementation
│   │   ├── provider_factory.py      # Factory pattern for providers
│   │   └── retry_handler.py         # Exponential backoff retry logic
│   ├── database/                    # SQLite with WAL mode
│   │   ├── models.py                # ORM models
│   │   └── repository.py            # Data access layer
│   ├── pipeline/                    # Processing pipeline
│   │   ├── cache.py                 # Result caching
│   │   └── output_validator.py      # Output format validation
│   └── prompts/                     # Prompt engineering
│       ├── templates.py             # Structured prompt templates
│       └── few_shot.py              # Few-shot learning examples
│
├── Global_Sigma_Rules/              # 2,750+ community Sigma rules (SigmaHQ)
│
└── docker/                          # Container orchestration
    ├── docker-compose.yml
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    └── nginx.conf.template
```

---

## Analysis Pipeline

```
 URL / PDF Input
    │
    ▼
┌─────────────────────────────┐
│  1. CONTENT EXTRACTION      │  Playwright headless browser + OCR
│     Fetch page → parse HTML │  Images → EasyOCR → text
│     Extract text + tables   │  PDF documents → PyPDF2
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  2. AI ANALYSIS             │  Multi-provider (OpenAI/Anthropic/Google)
│     Threat summarization    │  Structured JSON output
│     IoC extraction          │  TTP identification
│     MITRE ATT&CK mapping   │  Confidence scoring
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  3. DETECTION GENERATION    │  IoC-based + behavior-based rules
│     Sigma rules (YAML)      │  Per-IoC and per-TTP generation
│     YARA rules              │  Pattern matching signatures
│     SIEM queries            │  Splunk │ QRadar │ Elastic │ Sentinel
│     Hunting queries         │  Proactive threat hunting
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  4. ENRICHMENT              │  Cross-reference with 2,750+ rules
│     Global Sigma Match      │  Existing detection surfacing
│     Atomic Red Team tests   │  Attack simulation scenarios
│     QA scoring              │  Automated quality validation
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  5. OUTPUT                  │  Real-time SSE streaming to UI
│     Dashboard visualization │  PDF report generation
│     Rule library storage    │  SQLite persistence (WAL mode)
└─────────────────────────────┘
```

---

## Quickstart

### Option A: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/dipsh0v/PERSEPTOR.git
cd PERSEPTOR

# 2. Configure environment
cp .env.example .env
# Edit .env and add at least one AI provider API key:
#   OPENAI_API_KEY=sk-...
#   or ANTHROPIC_API_KEY=sk-ant-...
#   or GOOGLE_API_KEY=AI...

# 3. Build and start containers
cd docker
docker compose up -d --build

# 4. Open in browser
# http://localhost:3000
```

> **Note:** First build takes a few minutes (installs Playwright browser + npm dependencies).
> Subsequent starts are fast since Docker caches the layers.

<details>
<summary><strong>Verify containers are running</strong></summary>

```bash
docker compose ps
# Should show:
#   perseptor-backend    running (healthy)
#   perseptor-frontend   running

# Check backend health
curl http://localhost:3000/api/health

# View logs
docker compose logs -f backend
docker compose logs -f frontend
```
</details>

### Option B: Manual Setup

**Prerequisites:** Python 3.9+ and Node.js 18+

```bash
# 1. Clone the repository
git clone https://github.com/dipsh0v/PERSEPTOR.git
cd PERSEPTOR

# 2. Configure environment
cp .env.example .env
# Edit .env and add at least one AI provider API key

# 3. Backend setup
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium     # Required for dynamic page rendering

# 4. Start backend (Terminal 1)
python3 api/app.py              # Starts on http://localhost:5000

# 5. Frontend setup (Terminal 2)
cd perseptor-ui
npm install
npm start                       # Starts on http://localhost:3000
```

> **Windows + Anaconda users:** If you encounter a Cairo library error (`OSError: no library called "cairo-2"`), use conda:
> ```bash
> conda create -n perseptor python=3.11 -y && conda activate perseptor
> conda install -c conda-forge cairo pango gdk-pixbuf cairosvg cairocffi -y
> pip install -r requirements.txt
> playwright install chromium
> ```

### First Run

1. Open `http://localhost:3000`
2. Go to **Settings** → enter your AI provider API key (OpenAI, Anthropic, or Google)
3. Select your preferred model
4. Go to **Threat Analysis** → paste a threat report URL or upload a PDF
5. Watch the real-time analysis pipeline execute

---

## Configuration

All configuration is managed through environment variables or a `.env` file in the project root:

```bash
# AI Provider (choose one or more)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...

# Default provider: "openai" | "anthropic" | "google"
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-4.1-2025-04-14

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
FLASK_ENV=development

# Security
SECRET_KEY=your-secret-key-here
SESSION_EXPIRY_HOURS=24
RATE_LIMIT_PER_MINUTE=60
CORS_ORIGINS=http://localhost:3000

# Database
DATABASE_PATH=data/perseptor.db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text
```

> **Note:** API keys can also be configured via the **Settings** page in the UI. Keys set in the UI are stored in your browser and sent per-request — they are never stored on the server.

> **Docker users:** The `.env` file is automatically loaded by `docker compose`. Environment variables in `.env` are passed through to the backend container.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Full analysis pipeline (JSON response) |
| `POST` | `/api/analyze/stream` | Full analysis pipeline (SSE streaming) |
| `POST` | `/api/analyze/pdf/stream` | PDF analysis pipeline (SSE streaming) |
| `POST` | `/api/generate_rule` | Generate individual detection rules |
| `GET` | `/api/rules` | List all generated rules |
| `DELETE` | `/api/rules/:id` | Delete a specific rule |
| `GET` | `/api/rules/:id/download` | Download rule file |
| `GET` | `/api/reports` | List all analysis reports |
| `DELETE` | `/api/reports/:id` | Delete a specific report |
| `POST` | `/api/session` | Create encrypted session |
| `DELETE` | `/api/session` | Terminate session |
| `GET` | `/api/session/usage` | Get token usage statistics |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/models` | List available AI models by provider |

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | Flask 2.3+ |
| AI Providers | OpenAI, Anthropic, Google Generative AI |
| Content Extraction | Playwright, BeautifulSoup4, EasyOCR |
| Rule Processing | pySigma, PyYAML |
| PDF Generation | ReportLab, Matplotlib |
| NLP | NLTK |
| Database | SQLite (WAL mode) |
| Session Security | Cryptography (Fernet) |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 19 |
| Language | TypeScript 4.9 |
| UI Library | MUI (Material UI) 7 |
| State Management | Redux Toolkit 2.2 |
| HTTP Client | Axios |
| Charts | Recharts |
| Routing | React Router 7 |
| Notifications | Notistack |

---

## Project Structure

```
PERSEPTOR/
├── api/                         # Backend API
│   └── app.py                   # Flask application (13+ REST + SSE endpoints)
├── modules/                     # Core processing modules
│   ├── ai/                      # AI provider abstraction (3 providers)
│   ├── database/                # Data persistence layer
│   ├── pipeline/                # Processing pipeline & caching
│   └── prompts/                 # Prompt templates & few-shot examples
├── perseptor-ui/                # Frontend application
│   └── src/
│       ├── components/          # Reusable UI components
│       ├── pages/               # Route-level page components
│       ├── store/               # Redux store & slices
│       └── services/            # API client layer
├── Global_Sigma_Rules/          # 2,750+ community detection rules
├── docker/                      # Docker configuration
│   ├── docker-compose.yml       # Container orchestration
│   ├── Dockerfile.backend       # Python backend image
│   ├── Dockerfile.frontend      # React build + Nginx image
│   └── nginx.conf.template      # Nginx reverse proxy config
├── scripts/
│   └── update_sigma_rules.py    # Sigma rules update script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── LICENSE                      # MIT License
```

---

## Remote / SSH Server Deployment

PERSEPTOR works seamlessly on remote servers, cloud instances, and VPN setups:

```bash
# On your server
cd PERSEPTOR
cp .env.example .env
# Edit .env with your API keys

cd docker && docker compose up -d --build

# Access from your local machine
# http://YOUR_SERVER_IP:3000
```

**Notes:**
- Only port `3000` needs to be open in your firewall (the backend is internal to Docker)
- CORS is pre-configured for both local and remote access
- Works with Tailscale, WireGuard, and other VPN solutions
- No additional configuration needed — just access via your server's IP

---

## Troubleshooting

<details>
<summary><strong>Backend won't start</strong></summary>

```bash
# Check if port 5000 is in use
lsof -i :5000           # macOS/Linux
netstat -ano | findstr :5000   # Windows

# Kill the blocking process
kill -9 <PID>            # macOS/Linux
taskkill /PID <PID> /F   # Windows
```
</details>

<details>
<summary><strong>Frontend can't connect to backend</strong></summary>

- Verify backend is running: `curl http://localhost:5000/api/health`
- Docker: `docker compose ps` to check container status
- Docker logs: `docker compose logs backend`
- Make sure `.env` file exists (copy from `.env.example`)
</details>

<details>
<summary><strong>AI provider errors</strong></summary>

- Verify your API key in the Settings page (or in `.env`)
- Check provider status pages for outages
- Try switching to a different provider/model
- Check backend logs: `docker compose logs backend` or set `LOG_LEVEL=DEBUG`
</details>

<details>
<summary><strong>Playwright / browser errors</strong></summary>

```bash
# Install Playwright browser (manual setup only)
playwright install chromium

# Docker handles this automatically during build
```
</details>

<details>
<summary><strong>Module import errors</strong></summary>

```bash
pip install -r requirements.txt
python3 -c "import sys; print(sys.path)"
```
</details>

<details>
<summary><strong>npm/Node.js issues</strong></summary>

```bash
cd perseptor-ui
rm -rf node_modules package-lock.json
npm install
```
</details>

<details>
<summary><strong>Docker build fails</strong></summary>

```bash
# Clean rebuild
docker compose down
docker compose build --no-cache
docker compose up -d

# Check disk space
docker system df
docker system prune  # Clean unused images/containers
```
</details>

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Reporting Bugs

Use [GitHub Issues](https://github.com/dipsh0v/PERSEPTOR/issues) with:
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, Node version)

---

## Contact

**Aytek AYTEMUR**

- GitHub: [@dipsh0v](https://github.com/dipsh0v)
- Email: [aytek.aytemur@outlook.com](mailto:aytek.aytemur@outlook.com)

---

## License

Distributed under the [MIT License](LICENSE).

---

## Acknowledgments

- [MITRE ATT&CK](https://attack.mitre.org/) — Threat classification framework
- [SigmaHQ](https://github.com/SigmaHQ/sigma) — Community detection rules
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) — Attack simulation framework

---

<p align="center">
  <strong>PERSEPTOR</strong> — Detection Engineering, Automated.
</p>
