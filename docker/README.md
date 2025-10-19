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

2. **Start the containers**
   ```bash
   docker-compose up -d --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

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

## Production Deployment

For production environments:

1. Update environment variables for production
2. Change `FLASK_ENV` to `production` in `docker-compose.yml`
3. Start containers:
   ```bash
   docker-compose up -d
   ```

## Troubleshooting

### Port conflicts
If ports 3000 or 5000 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "8080:3000"  # Alternative port for frontend
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
