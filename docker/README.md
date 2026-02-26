# PERSEPTOR Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (1.29+)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/dipsh0v/PERSEPTOR.git
   cd PERSEPTOR/docker
   ```

2. **Configure environment variables (Optional)**
   ```bash
   # Copy the environment template
   cp ENV_TEMPLATE .env
   
   # Edit .env to customize ports, paths, and URLs
   nano .env
   ```
   
   All configuration has sensible defaults, so you can skip this step if you want to use:
   - Frontend: Port 3000
   - Backend: Port 5000 (internal only)

3. **Start the containers**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000 (or custom port from .env)
   - Backend API: Internal only - accessed through nginx proxy

## Commands

### Start containers
```bash
docker-compose up
```

### Start containers in background
```bash
docker-compose up -d
```

### Stop containers
```bash
docker-compose down
```

### Rebuild and start containers
```bash
docker-compose up --build
```

### View logs
```bash
docker-compose logs -f
```

### View backend logs only
```bash
docker-compose logs -f backend
```

### View frontend logs only
```bash
docker-compose logs -f frontend
```

### Access container shell
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh
```

## Environment Variables

All configuration is managed through environment variables. You can either:

1. **Create a .env file** (recommended):
   ```bash
   cp ENV_TEMPLATE .env
   # Edit .env with your values
   ```

2. **Use environment variables directly**:
   ```bash
   FRONTEND_PORT=8080 BACKEND_PORT=5000 docker-compose up
   ```

### Available Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_HOST` | `0.0.0.0` | Backend bind address |
| `BACKEND_PORT` | `5000` | Backend internal port |
| `FLASK_ENV` | `development` | Flask environment (development/production) |
| `FRONTEND_PORT` | `3000` | Frontend external port |
| `NGINX_PORT` | `3000` | Nginx internal port |
| `BACKEND_SERVICE` | `backend` | Backend service name in Docker network |
| `SIGMAHQ_BASE_URL` | `https://github.com/SigmaHQ/sigma/blob/master` | SigmaHQ repository URL |
| `TESSERACT_CMD` | `/usr/bin/tesseract` | Tesseract OCR binary path |
| `CHROME_BIN` | `/usr/bin/chromium` | Chrome binary path |
| `CHROMEDRIVER_PATH` | `/usr/bin/chromedriver` | ChromeDriver path |

## Production Deployment

For production environments:

1. **Create .env file**:
   ```bash
   cp ENV_TEMPLATE .env
   ```

2. **Update environment variables**:
   ```bash
   # Edit .env
   FLASK_ENV=production
   FRONTEND_PORT=80  # Or your preferred port
   ```

3. **Start containers**:
   ```bash
   docker-compose up -d --build
   ```

## Troubleshooting

### Port conflicts
If ports 3000 or 5000 are already in use, change them using environment variables:

**Option 1: Using .env file** (recommended):
```bash
# Create or edit .env file
echo "FRONTEND_PORT=8080" >> .env
echo "BACKEND_PORT=5001" >> .env
docker-compose up -d --build
```

**Option 2: Using command line**:
```bash
FRONTEND_PORT=8080 docker-compose up -d
```

### Sigma rules
Sigma rules are automatically loaded from the `Global_Sigma_Rules/` directory within the project. This directory contains 1100+ Sigma rules and is automatically mounted to the Docker container.

### Restart containers
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Clean up and restart
```bash
docker-compose down -v
docker-compose up --build
```

## Architecture

The Docker setup includes:

### Backend Container
- **Base:** Python 3.11-slim
- **Features:**
  - Tesseract OCR support
  - Selenium Chrome driver
  - All Python dependencies
  - Flask API server

### Frontend Container
- **Base:** Node 18 (build) → Nginx Alpine (production)
- **Features:**
  - Multi-stage build for optimized size
  - Production-ready Nginx configuration
  - API proxy to backend

### Network
- Custom bridge network for container isolation
- Automatic DNS resolution between containers

### Volumes
- Hot-reload support for development
- Persistent Sigma rules directory
- Shared modules between containers

## Notes

- Backend includes Tesseract OCR and Selenium Chrome driver
- Frontend runs on Nginx with production build
- Both services have auto-restart capability
- Network isolation using custom bridge network
- API requests are proxied from frontend Nginx to backend

## Security

- Don't commit `.env` file to git in production
- Keep your OpenAI API key secure
- Use Docker secrets for sensitive data in production
- Limit container permissions as needed

## Support

For issues and questions:
- GitHub Issues: https://github.com/dipsh0v/PERSEPTOR/issues
- Documentation: See main README.md
