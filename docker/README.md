# PERSEPTOR Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2+

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/dipsh0v/PERSEPTOR.git
   cd PERSEPTOR
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add at least one AI provider API key:
   #   OPENAI_API_KEY=sk-...
   #   or ANTHROPIC_API_KEY=sk-ant-...
   #   or GOOGLE_API_KEY=AI...
   ```

3. **Build and start containers**
   ```bash
   cd docker
   docker compose up -d --build
   ```

4. **Access the application**
   - Open http://localhost:3000 in your browser
   - Go to **Settings** to configure your AI provider and model
   - Go to **Threat Analysis** to start analyzing

## Commands

```bash
# Start containers
docker compose up -d

# Start with rebuild
docker compose up -d --build

# Stop containers
docker compose down

# View all logs
docker compose logs -f

# View backend logs only
docker compose logs -f backend

# View frontend logs only
docker compose logs -f frontend

# Check container status
docker compose ps

# Restart a service
docker compose restart backend
docker compose restart frontend

# Access container shell
docker compose exec backend bash
docker compose exec frontend sh

# Clean rebuild (fresh start)
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## Environment Variables

All configuration is managed through the `.env` file in the project root. Copy `.env.example` to get started:

```bash
cp .env.example .env
```

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key |
| `ANTHROPIC_API_KEY` | *(empty)* | Anthropic API key |
| `GOOGLE_API_KEY` | *(empty)* | Google AI API key |
| `DEFAULT_AI_PROVIDER` | `openai` | Default AI provider |
| `DEFAULT_MODEL` | `gpt-4.1-2025-04-14` | Default AI model |
| `FLASK_ENV` | `development` | Flask environment |
| `SECRET_KEY` | `change-me-in-production` | Session encryption key |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit |
| `SESSION_EXPIRY_HOURS` | `24` | Session timeout |
| `NGINX_PORT` | `3000` | Frontend port (exposed) |

> **Note:** API keys can also be configured via the **Settings** page in the UI. Keys set in the UI are stored in your browser and never on the server.

## Architecture

### Backend Container
- **Base:** Python 3.11-slim
- **Features:**
  - Playwright headless browser for dynamic page rendering
  - EasyOCR for image text extraction
  - Multi-provider AI engine (OpenAI, Anthropic, Google)
  - Flask API server with SSE streaming
  - SQLite database with WAL mode
  - Healthcheck enabled (auto-restarts on failure)
- **Internal port:** 5000 (not exposed externally)

### Frontend Container
- **Base:** Node 18 (build stage) -> Nginx Alpine (production)
- **Features:**
  - Multi-stage build for optimized image size
  - Nginx reverse proxy to backend API
  - SSE streaming support (proxy_buffering off)
  - Gzip compression for static assets

### Network
- Custom bridge network for container isolation
- Backend is only accessible within the Docker network
- Frontend nginx proxies /api/* requests to backend

### Volumes
- `modules/` and `api/` are bind-mounted for live development
- `Global_Sigma_Rules/` mounted read-only (2,750+ detection rules)
- Named volume `perseptor-data` persists the SQLite database

## Troubleshooting

### Port conflicts
```bash
# Change the frontend port via environment variable
NGINX_PORT=8080 docker compose up -d

# Or set in .env file
# NGINX_PORT=8080
```

### Backend health check
```bash
# Check health via nginx
curl http://localhost:3000/api/health

# Check container health status
docker compose ps
```

### SSE streaming issues
The nginx config includes dedicated SSE locations with `proxy_buffering off` for the analysis streaming endpoints. If streaming does not work:
```bash
# Verify nginx config has SSE blocks
docker compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Sigma rules
2,750+ community Sigma rules from SigmaHQ are automatically loaded from `Global_Sigma_Rules/` and mounted read-only into the backend container.

## Security

- Never commit `.env` to git (it is in `.gitignore`)
- Change `SECRET_KEY` in production
- AI API keys can be set via `.env` or the Settings UI
- Backend port 5000 is not exposed externally
- Rate limiting is enabled by default (60 req/min)

## Support

For issues and questions:
- GitHub Issues: https://github.com/dipsh0v/PERSEPTOR/issues
- Documentation: See main README.md
