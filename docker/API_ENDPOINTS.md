# PERSEPTOR API Endpoints

## Base URL
- Development: `http://localhost:3000/api` (via nginx proxy)
- Direct backend: `http://localhost:5000/api` (manual setup only)

## Authentication
Session-based authentication with Fernet encryption. Sessions are created automatically and managed via `X-Session-Token` header. API keys for AI providers are configured via the Settings UI or environment variables.

---

## Analysis Endpoints

### POST /api/analyze
Analyze a threat report URL and generate intelligence (JSON response).

**Request Body:**
```json
{
  "url": "https://example.com/threat-report",
  "openai_api_key": "sk-..."
}
```

### POST /api/analyze/stream
Analyze a threat report URL with real-time SSE streaming.

**Request Body:**
```json
{
  "url": "https://example.com/threat-report"
}
```

**SSE Events:**
```
data: {"type": "stage", "stage": "content_extraction", "progress": 10, "message": "Fetching page content..."}
data: {"type": "stage", "stage": "ai_analysis", "progress": 30, "message": "Analyzing threats..."}
data: {"type": "result", "data": {...}}
data: {"type": "complete"}
```

### POST /api/analyze/pdf/stream
Analyze a PDF document with real-time SSE streaming.

**Request:** Multipart form data with PDF file.

---

## Rule Generation

### POST /api/generate_rule
Generate a custom Sigma rule using AI.

**Request Body:**
```json
{
  "prompt": "Create a Sigma rule to detect..."
}
```

**Response:** Rule object with confidence score, MITRE mappings, test cases, and recommendations.

---

## Rules Management

### GET /api/rules
Get all created Sigma rules.

### DELETE /api/rules/:rule_id
Delete a specific rule.

### GET /api/rules/:rule_id/download
Download a rule as a YAML file.

---

## Reports Management

### GET /api/reports
Get all analyzed threat reports (sorted by timestamp, newest first).

### DELETE /api/reports/:report_id
Delete a specific report.

---

## Session Management

### POST /api/session
Create an encrypted session.

### DELETE /api/session
Terminate the current session.

### GET /api/session/usage
Get token usage statistics for the current session.

---

## System

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "app_name": "PERSEPTOR",
  "version": "2.0.0",
  "default_provider": "openai",
  "default_model": "gpt-4.1-2025-04-14",
  "available_providers": ["openai", "anthropic", "google"],
  "sigma_rules_loaded": 2750,
  "debug": true,
  "timestamp": "2026-03-21T15:27:10.740107"
}
```

### GET /api/models
List available AI models grouped by provider.

---

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (missing parameters, invalid input) |
| 401 | Unauthorized (session expired) |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |

## Security Features

- **Rate Limiting:** Token bucket algorithm (configurable, default 60 req/min)
- **Session Encryption:** Fernet-based encrypted sessions
- **SSRF Prevention:** Private IP blocking and DNS resolution checks
- **Input Sanitization:** Request size validation and input cleaning
- **CORS:** Configurable allowed origins

## Testing

```bash
# Health check
curl http://localhost:3000/api/health

# Get all reports
curl http://localhost:3000/api/reports

# Get all rules
curl http://localhost:3000/api/rules

# List available models
curl http://localhost:3000/api/models
```
