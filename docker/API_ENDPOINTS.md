# PERSEPTOR API Endpoints

## Base URL
- Development: `http://localhost:3000/api` (via nginx proxy)
- Production: Configure via environment variables

## Authentication
Currently no authentication required. For production, consider implementing:
- API Keys
- JWT tokens
- OAuth 2.0

---

## Analysis Endpoints

### POST /api/analyze
Analyze a threat report URL and generate intelligence.

**Request Body:**
```json
{
  "url": "https://example.com/threat-report",
  "openai_api_key": "sk-..."
}
```

**Response:**
```json
{
  "threat_summary": "...",
  "analysis_data": {
    "indicators_of_compromise": {
      "ip_addresses": ["1.2.3.4"],
      "domains": ["malicious.com"],
      "file_hashes": ["abc123..."]
    },
    "ttps": [
      {
        "mitre_id": "T1566",
        "technique_name": "Phishing",
        "description": "..."
      }
    ],
    "threat_actors": ["APT28"],
    "tools_or_malware": ["Emotet"]
  },
  "yara_rules": [...],
  "generated_sigma_rules": "...",
  "siem_queries": {
    "splunk": {...},
    "qradar": {...},
    "elastic": {...},
    "sentinel": {...}
  },
  "sigma_matches": [...]
}
```

**Notes:**
- Report is automatically saved to backend storage
- Returns 500 on error with error details

---

## Sigma Rule Generation Endpoints

### POST /api/generate_rule
Generate a custom Sigma rule using AI.

**Request Body:**
```json
{
  "prompt": "Create a Sigma rule to detect...",
  "openai_api_key": "sk-..."
}
```

**Response:**
```json
{
  "rule": {
    "title": "...",
    "description": "...",
    "detection": {...},
    "level": "high",
    ...
  },
  "explanation": "...",
  "test_cases": [...],
  "mitre_techniques": [...],
  "recommendations": [...],
  "references": [...],
  "confidence_score": 0.85,
  "component_scores": {...}
}
```

**Notes:**
- Rule is automatically saved to backend storage
- Calculates confidence score
- Returns MITRE ATT&CK mappings

---

## Sigma Rules Management

### GET /api/rules
Get all created Sigma rules.

**Response:**
```json
{
  "rules": [
    {
      "id": "uuid",
      "title": "Rule Title",
      "description": "...",
      "author": "PERSEPTOR",
      "date": "2025/10/22",
      "product": "sigma",
      "confidence_score": 0.85,
      "mitre_techniques": [...],
      "rule_content": {...},
      "created_at": "2025-10-22T12:00:00Z"
    }
  ],
  "count": 10
}
```

### DELETE /api/rules/:rule_id
Delete a specific Sigma rule.

**Parameters:**
- `rule_id`: UUID of the rule to delete

**Response:**
```json
{
  "message": "Rule deleted successfully"
}
```

**Error Response:**
```json
{
  "error": "Rule not found"
}
```

### GET /api/rules/:rule_id/download
Download a Sigma rule as YAML file.

**Parameters:**
- `rule_id`: UUID of the rule to download

**Response:**
- Content-Type: `text/yaml`
- Content-Disposition: `attachment; filename="rule_title.yaml"`

---

## Reports Management

### GET /api/reports
Get all analyzed threat reports.

**Response:**
```json
{
  "reports": [
    {
      "id": "uuid",
      "url": "https://example.com/threat-report",
      "timestamp": "2025-10-22T12:00:00Z",
      "threat_summary": "...",
      "analysis_data": {...},
      "yara_rules": [...],
      "generated_sigma_rules": "...",
      "siem_queries": {...},
      "sigma_matches": [...]
    }
  ],
  "count": 5
}
```

**Notes:**
- Reports are sorted by timestamp (newest first)
- Includes all analysis results

### DELETE /api/reports/:report_id
Delete a specific report.

**Parameters:**
- `report_id`: UUID of the report to delete

**Response:**
```json
{
  "message": "Report deleted successfully"
}
```

**Error Response:**
```json
{
  "error": "Report not found"
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (missing parameters, invalid input)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error

Error responses include a JSON body:
```json
{
  "error": "Error message description"
}
```

Some endpoints also include traceback in development mode:
```json
{
  "error": "Error message",
  "traceback": "Full Python traceback..."
}
```

---

## Storage

**Current Implementation:**
- In-memory storage (Python lists)
- Data is lost on server restart
- Not suitable for production

**Production Recommendations:**
1. **PostgreSQL/MySQL**: Relational database for structured data
2. **MongoDB**: NoSQL for flexible document storage
3. **Redis**: For caching and session management
4. **Object Storage (S3, MinIO)**: For large YARA/Sigma rule files

---

## Rate Limiting

**Current Status:** No rate limiting implemented

**Production Recommendations:**
- Implement rate limiting per IP address
- Consider user-based limits with authentication
- Use Redis for distributed rate limiting

Suggested limits:
- `/api/analyze`: 10 requests per hour per IP
- `/api/generate_rule`: 20 requests per hour per IP
- `/api/reports`: 100 requests per hour per IP
- `/api/rules`: 100 requests per hour per IP

---

## CORS Configuration

**Current Configuration:**
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

**Production Recommendations:**
- Restrict origins to specific domains
- Use environment variables for allowed origins
- Enable credentials if using authentication

Example:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            os.environ.get("FRONTEND_URL", "http://localhost:3000")
        ],
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## Health Check

**Recommended Addition:**

### GET /api/health
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-22T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "openai": "available"
  }
}
```

---

## Websockets (Future Enhancement)

For real-time updates during long-running analysis:

### WS /api/analyze/stream
Stream analysis progress in real-time.

**Messages:**
```json
{
  "type": "progress",
  "stage": "ocr_processing",
  "progress": 25,
  "message": "Processing images..."
}
```

---

## Environment Variables

API behavior can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_HOST` | `0.0.0.0` | Host to bind |
| `BACKEND_PORT` | `5000` | Port to listen on |
| `FLASK_ENV` | `development` | Flask environment |
| `SIGMAHQ_BASE_URL` | `https://github.com/SigmaHQ/sigma/blob/master` | SigmaHQ repo URL |

---

## Testing

Use the included test script:
```bash
cd /home/dipsh0v/PERSEPTOR/docker
./test_env_vars.sh
```

Manual API testing:
```bash
# Health check (if implemented)
curl http://localhost:3000/api/health

# Get all reports
curl http://localhost:3000/api/reports

# Get all rules
curl http://localhost:3000/api/rules

# Analyze URL (requires OpenAI key)
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/threat-report",
    "openai_api_key": "sk-..."
  }'
```

---

## Future Enhancements

1. **Authentication & Authorization**
   - User accounts
   - API keys
   - Role-based access control

2. **Persistent Storage**
   - Database integration
   - File storage for large artifacts

3. **Export Formats**
   - MISP format export
   - STIX/TAXII support
   - CSV/Excel export

4. **Webhooks**
   - Notify on analysis completion
   - Integration with SIEM systems

5. **Batch Processing**
   - Analyze multiple URLs
   - Scheduled scans

6. **Advanced Analytics**
   - Trend analysis
   - IOC deduplication
   - Threat actor correlation

