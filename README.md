<!-- Banner / Logo Placeholder -->

<p align="center">
  <img src="[IMAGE: PERSEPTOR banner / logo]" alt="PERSEPTOR" width="780"/>
</p>

<h1 align="center">PERSEPTOR 🎯</h1>

<p align="center"><b>AI‑Powered Detection Engineering Platform</b></p>
<p align="center">Turn raw threat intelligence into production‑ready detections in minutes — with human‑in‑the‑loop QA.</p>

<p align="center">
  <a href="#quick-start"><img alt="docker" src="https://img.shields.io/badge/run%20with-docker-blue"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/License-Apache--2.0-green"></a>
  <img alt="status" src="https://img.shields.io/badge/status-active-success">
  <img alt="stars" src="https://img.shields.io/github/stars/dipsh0v/PERSEPTOR?style=social">
  <img alt="issues" src="https://img.shields.io/github/issues/dipsh0v/PERSEPTOR">
  <img alt="prs" src="https://img.shields.io/github/issues-pr/dipsh0v/PERSEPTOR">
</p>

<p align="center">
  <a href="#overview"><b>Overview</b></a> ·
  <a href="#key-features"><b>Features</b></a> ·
  <a href="#quick-start"><b>Quick Start</b></a> ·
  <a href="#architecture"><b>Architecture</b></a> ·
  <a href="#docs"><b>Docs</b></a> ·
  <a href="#roadmap"><b>Roadmap</b></a> ·
  <a href="#community"><b>Community</b></a>
</p>

<p align="center">
  <a href="#quick-start"><b>🚀 Try in 60 seconds</b></a> ·
  <a href="https://github.com/dipsh0v/PERSEPTOR/stargazers"><b>⭐ Star to support</b></a>
</p>

---

## Overview

**PERSEPTOR** transforms real‑world threat intel into **ATT&CK‑mapped** detections you can deploy. It automates behavioral extraction, Sigma/YARA generation, SIEM query conversion, and rule QA — then keeps humans in the loop for tuning and validation.

**Built for** SOC, Detection Engineering, Threat Intel, and IR teams who want repeatable pipelines over ad‑hoc heroics.

**What it solves**

* Threat reports are unstructured and slow to convert into signals.
* Rules ship without QA or context, causing false positives.
* Coverage is hard to measure and communicate.

**How it helps**

* AI‑assisted analysis → consistent patterns & IoCs
* One‑click rule generation (Sigma/YARA) + SIEM queries
* Confidence scoring, test cases, and validation workflows

> *“From intel to instrumented detection — fast, explainable, and production‑ready.”*

---

## ✨ Key Features {#key-features}

### 🤖 AI‑Powered Analysis

* Extract **TTPs**, **IoCs**, and behaviors from reports, blogs, and PDFs (OCR included)
* Normalize to **MITRE ATT&CK** tactics/techniques
* Summarize & stage **investigation notes**

### 🛡️ Detection Engineering

* Generate **Sigma** and **YARA** with rationale & test cases
* Convert to **SIEM queries** (Splunk, Elastic, Sentinel, QRadar)
* Rule **QA**: confidence score, explainers, common FP patterns

### 🔍 Threat Intelligence

* Enrich entities (domains, hashes, IPs, tools)
* De‑duplicate & tag context (family, cluster, campaign)
* Planned: analyst feedback → **FP reduction via ML**

### 📊 Analytics & Reporting

* Auto‑built **report** with sources, ATT&CK mapping, and artifacts
* Export artifacts (planned: PDF/HTML)
* “Analyzed Reports” history & re‑run capability

### 🧩 Integrations (initial)

* **OCR** for images/figures embedded in reports
* Local file & URL ingestion
* Dockerized services for easy deployment

---

## 🎬 Quick Start {#quick-start}

> **Goal:** up and running in ~60 seconds with Docker.

```bash
# 1) Clone
git clone https://github.com/dipsh0v/PERSEPTOR.git && cd PERSEPTOR

# 2) Configure (minimal)
cp .env.example .env
# Edit .env with your OpenAI key (see SECURITY notes).
# UI also supports entering a key at runtime.

# 3) Launch
docker compose up -d --build

# 4) Open UI
# Default: http://localhost:3000
```

**Success indicator:** Frontend responds on `:3000`, API on `:5000`. Run a sample analysis from the UI (paste a public threat report URL) and generate a Sigma rule.

<details>
<summary>Manual / Dev Setup (advanced)</summary>

* **Backend (Flask/Gunicorn)**

  ```bash
  cd api && python3 -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  export OPENAI_API_KEY=sk-...  # or set via .env
  gunicorn -b 0.0.0.0:5000 -w 1 app:app
  ```
* **Frontend (React)**

  ```bash
  cd perseptor-ui
  npm install
  npm run dev  # http://localhost:3000
  ```

</details>

---

## 📸 Screenshots / Demo

* [IMAGE: Dashboard — URL/file analysis → patterns/IoCs]
* [IMAGE: Generated Sigma with confidence & test cases]
* [IMAGE: ATT&CK mapping view]
* [IMAGE: Report summary card]

> *Video demo placeholder*: `[VIDEO: 90s overview]`

---

## 🏗️ Architecture {#architecture}

```mermaid
graph TD
  A[Input
  • URL / PDF / HTML
  • Files / Images (OCR)
  ] --> B[Ingestion & Parsing]
  B --> C[AI Analysis
  • TTP/IoC extraction
  • ATT&CK mapping]
  C --> D[Detection Engine
  • Sigma / YARA
  • SIEM queries]
  D --> E[QA & Scoring
  • Confidence
  • Test cases]
  E --> F[Report Builder
  • Summary
  • Artifacts]
  F --> G[(Store)]
  G --> H[UI: History & Export]
```

**Tech Stack**: GPT‑4, Python/Flask, React, Docker, Tesseract OCR

---

## 📚 Documentation {#docs}

### Installation

* **Prerequisites**: Docker ≥ 24, Docker Compose, Node 18+, Python 3.11+
* **Config**: `.env` (see `.env.example`) or UI‑provided API key
* **Security**: Prefer using a **project‑scoped** API key; avoid committing keys

### Configuration

| Variable         | Description                                    |
| ---------------- | ---------------------------------------------- |
| `OPENAI_API_KEY` | OpenAI API key (sk‑… or project key)           |
| `API_PORT`       | Backend port (default `5000`)                  |
| `UI_PORT`        | Frontend port (default `3000`)                 |
| `ALLOW_UI_KEYS`  | Allow setting API key from UI (default `true`) |

### Usage — Basic Workflow

1. Provide a threat report URL or upload a file.
2. PERSEPTOR extracts TTPs/IoCs and suggests ATT&CK mapping.
3. Generate **Sigma/YARA** + SIEM queries.
4. Review confidence, test cases, and potential FP notes.
5. Save/report; iterate with edits.

### API Reference (Preview)

```http
POST /api/analyze
POST /api/generate_rule
GET  /api/reports
```

> Full OpenAPI spec coming soon.

---

## 🎯 Use Cases

**SOC Operations**

* Rapid rule prototyping for emerging threats
* Confidence‑scored detections for triage

**Threat Intelligence**

* Normalized, actionable outputs from narrative intel
* Batch processing of long‑form reports

**Incident Response**

* Quick hypothesis → rule generation for scoping
* Report bundles for stakeholders

**Red / Purple Team**

* Procedure → detection linkage to drive exercises
* ATT&CK‑mapped coverage tracking (planned)

---

## 🚀 Performance & Benchmarks *(initial)*

* Typical single‑report analysis: *seconds to a few minutes* depending on inputs.
* OCR adds overhead proportional to image count.
* Rule QA returns a scalar **confidence score** with component breakdowns.

(Community contributions with reproducible benchmarks welcome.)

---

## 🗺️ Roadmap {#roadmap}

**Near‑term**

* PDF/HTML export of reports
* “Mark as FP” on IoCs → learning loop
* OpenAPI docs + SDK examples

**Mid‑term**

* Coverage dashboard (SigmaHQ cross‑match)
* Multi‑model provider support
* Pluggable enrichment (VT, URLhaus, etc.)

**Long‑term**

* Rule lifecycle management (promote, deprecate)
* Team workspaces & RBAC
* Data‑driven FP reduction models

> Track progress in **Issues** and **Project Board**.

---

## 🤝 Contributing

We welcome issues, PRs, and discussions. See:

* `CONTRIBUTING.md` — how to file issues/PRs, coding standards
* `CODE_OF_CONDUCT.md` — be kind

**Ways to contribute**

* Bug reports & test cases
* New parsers/enrichers
* Additional SIEM mappings
* Benchmarks & docs

> Contributors will be recognized in **ACKNOWLEDGMENTS**.

---

## 💬 Community & Support {#community}

* GitHub **Issues** → bugs/feature requests
* GitHub **Discussions** → ideas/roadmap
* Security: see `SECURITY.md` for vulnerability reporting
*

> For organizations exploring collaboration, please open a discussion.

---

## 🏆 Acknowledgments

* Open‑source projects that make this possible: Python, Flask, React, Tesseract, SigmaHQ, YARA
* The detection engineering community for patterns, reviews, and feedback

---

## 📄 License & Citation

This project is licensed under **Apache‑2.0** — see `LICENSE`.

**Suggested citation**

```
Aytek Aytemur. PERSEPTOR: AI‑Powered Detection Engineering Platform. 2025. https://github.com/dipsh0v/PERSEPTOR
```

---

## ⭐ Show Your Support

If PERSEPTOR helps you ship better detections faster, please **star** the repo and share it with your team.

<p align="center">
  <a href="https://github.com/dipsh0v/PERSEPTOR/stargazers">⭐ Star on GitHub</a>
</p>

---

### Quality Checklist (for maintainers)

* [ ] First 5 seconds: value is clear
* [ ] True "Quick Start" (copy‑paste)
* [ ] Scannable sections & hierarchy
* [ ] Practical depth without overload
* [ ] Works for newcomers & experts
* [ ] Clear CTAs
* [ ] Copy‑paste‑ready examples
* [ ] Easy navigation
* [ ] Friendly community tone

---

### Notes for Maintainers (README hygiene)

* Keep screenshots up‑to‑date with UI
* Avoid leaking secrets in examples
* Prefer relative links within repo
* Ensure alt text on images
* Keep Mermaid diagrams simple and current
