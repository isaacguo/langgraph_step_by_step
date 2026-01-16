# API Reference

## Endpoints

### POST /chat
Send a message to the agent.

**Request Body**
```json
{
  "user_id": "string",
  "content": "string",
  "metadata": {}
}
```

**Response**
```json
{
  "request_id": "string",
  "content": "string",
  "safety_score": 1.0,
  "status": "success",
  "error": null
}
```

### GET /health
Check system health.

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### GET /introspection/decisions
Get recent safety decisions.

**Response**
```json
[
  {
    "id": "string",
    "timestamp": "iso-date",
    "result": "string",
    "rationale": "string"
  }
]
```
