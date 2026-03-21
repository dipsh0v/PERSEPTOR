# PERSEPTOR Configuration Checklist

## Environment Variable Configuration

### Docker Compose (docker-compose.yml)
- [x] Backend environment variables with defaults
- [x] AI API keys passthrough from .env
- [x] `env_file` with `required: false` for optional .env
- [x] Backend healthcheck enabled
- [x] Frontend depends on backend healthy state
- [x] Backend only uses `expose` (not accessible externally)
- [x] Named volume for persistent SQLite data

### Backend Dockerfile (Dockerfile.backend)
- [x] PYTHONUNBUFFERED=1 for log streaming
- [x] BACKEND_HOST and BACKEND_PORT environment variables
- [x] Playwright chromium installed
- [x] Data and logs directories created

### Frontend Dockerfile (Dockerfile.frontend)
- [x] Multi-stage build (Node build + Nginx serve)
- [x] nginx.conf.template with envsubst
- [x] docker-entrypoint.sh for dynamic config
- [x] NGINX_PORT, BACKEND_SERVICE, BACKEND_PORT variables

### Nginx Configuration
- [x] SSE streaming endpoint with proxy_buffering off
- [x] PDF upload streaming endpoint with proxy_buffering off
- [x] General API proxy with 10-minute timeout
- [x] Gzip compression enabled
- [x] client_max_body_size 50m for PDF uploads
- [x] Dynamic variables via envsubst

### Backend Code (api/app.py)
- [x] Reads config from environment via modules/config.py
- [x] CORS origins configurable
- [x] Accept-Encoding: gzip, deflate (no Brotli)
- [x] Structured JSON logging

### Modules Configuration (modules/config.py)
- [x] AI provider keys from environment
- [x] Database path configurable
- [x] Cache settings configurable
- [x] Security settings (CORS, rate limit, session expiry)
- [x] Logging configuration

## Test Steps

### Step 1: Start containers
```bash
cd docker
docker compose up -d --build
```

### Step 2: Verify health
```bash
curl http://localhost:3000/api/health
docker compose ps
```

### Step 3: Check nginx config
```bash
docker compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Step 4: Verify backend environment
```bash
docker compose exec backend printenv | grep -E "OPENAI|ANTHROPIC|GOOGLE|DEFAULT|FLASK|DATABASE"
```

### Step 5: Network connectivity
```bash
# Should work (via nginx)
curl http://localhost:3000/api/health

# Should fail (backend not exposed)
curl http://localhost:5000/api/health 2>&1 | head -1
```
