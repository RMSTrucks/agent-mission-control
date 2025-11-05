# Mission Control Backend

FastAPI backend for Agent Pipeline Management System.

## Features

- **Agent Management**: Compile, test, and manage AI agents
- **Testing**: Run BDD tests on SuperSpec files
- **Optimization**: Start and monitor GEPA optimization workflows
- **System Monitoring**: Health checks and performance metrics
- **SuperOptiX Integration**: Full integration with SuperOptiX CLI

## Setup

### Prerequisites

```bash
# Install dependencies from project root
pip install -r requirements.txt

# Install SuperOptiX
pip install superoptix
```

### Configuration

Create a `.env` file in the project root (optional):

```env
# API Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/database.db

# SuperOptiX
SUPEROPTIX_PATH=/path/to/super.exe

# External APIs (optional)
VAPI_API_KEY=your_vapi_key
CLOSE_API_KEY=your_close_key
OPENAI_API_KEY=your_openai_key
```

### Running the Backend

```bash
# From the backend directory
uvicorn main:app --reload

# Or from project root
cd backend && uvicorn main:app --reload

# With custom port
uvicorn main:app --reload --port 8080
```

The API will start on `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & System

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/system/status` - System status
- `GET /api/system/metrics` - Performance metrics

### Agents

- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get agent details
- `POST /api/agents` - Create new agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `POST /api/agents/{id}/compile` - Compile agent to SuperSpec
- `GET /api/agents/{id}/status` - Get agent status

### Testing

- `POST /api/tests/run` - Run BDD tests
- `POST /api/tests/evaluate/{agent_id}` - Evaluate agent
- `GET /api/tests/evaluate/{agent_id}/history` - Evaluation history
- `GET /api/tests/evaluate/{agent_id}/latest` - Latest evaluation

### Optimization

- `POST /api/optimize/{agent_id}` - Start optimization
- `GET /api/optimize/{agent_id}/status` - Get optimization status
- `GET /api/optimize/{agent_id}/history` - Optimization history
- `GET /api/optimize/{agent_id}/results` - Optimization results
- `POST /api/optimize/{agent_id}/deploy` - Deploy optimized version
- `POST /api/optimize/{agent_id}/rollback` - Rollback to baseline

## Request/Response Examples

### Compile Agent

**Request:**
```bash
curl -X POST "http://localhost:8000/api/agents/remus/compile"
```

**Response:**
```json
{
  "success": true,
  "agent_name": "remus",
  "output_path": "./remus.yaml",
  "message": "Compilation successful",
  "errors": null
}
```

### Start Optimization

**Request:**
```bash
curl -X POST "http://localhost:8000/api/optimize/remus" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "remus",
    "optimizer": "gepa",
    "iterations": 10,
    "params": {
      "auto_level": "medium"
    }
  }'
```

**Response:**
```json
{
  "job_id": "opt_remus_a1b2c3d4",
  "agent_id": "remus",
  "status": "pending",
  "optimizer": "gepa",
  "iterations": 10,
  "current_iteration": 0,
  "logs": ["Optimization started in background"]
}
```

### Get Optimization Status

**Request:**
```bash
curl "http://localhost:8000/api/optimize/remus/status"
```

**Response:**
```json
{
  "job_id": "opt_remus_a1b2c3d4",
  "agent_id": "remus",
  "status": "running",
  "optimizer": "gepa",
  "iterations": 10,
  "current_iteration": 5,
  "best_score": 85.5,
  "elapsed_seconds": 180.5,
  "iteration_history": [75.0, 78.5, 82.0, 84.0, 85.5]
}
```

## Architecture

```
backend/
├── main.py              # FastAPI app entry point
├── core/                # Core configuration
│   ├── __init__.py
│   └── config.py       # Settings management
├── api/                 # API endpoints
│   ├── __init__.py
│   ├── agents.py       # Agent management
│   ├── tests.py        # Testing & evaluation
│   └── optimize.py     # Optimization workflows
├── models/             # Pydantic models
│   ├── __init__.py
│   ├── requests.py     # Request schemas
│   └── responses.py    # Response schemas
└── database/           # Database setup (TODO)
    ├── __init__.py
    └── db.py
```

## Integration with SuperOptiX

The backend uses the SuperOptiX client wrapper from `integrations/superoptix_client.py`:

```python
from integrations.superoptix_client import SuperOptiXClient

client = SuperOptiXClient()

# Compile agent
result = client.compile_agent("my_agent")

# Run tests
result = client.run_tests("agent.yaml")

# Optimize
result = client.optimize("agent.yaml", iterations=10)
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "HTTPException",
  "message": "Agent not found: invalid_agent",
  "detail": "Additional error details",
  "timestamp": "2024-11-05T12:00:00"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `202` - Accepted (async operation started)
- `204` - No Content (successful deletion)
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `501` - Not Implemented
- `503` - Service Unavailable

## Background Tasks

Long-running operations (optimization) use FastAPI's `BackgroundTasks`:

- Optimization jobs run in background
- Status tracked in memory (TODO: move to database)
- Progress available via status endpoints

## Database

**Current**: In-memory storage for optimization jobs

**TODO**:
- SQLite for development
- PostgreSQL for production
- Store agents, evaluations, optimizations, executions

## Future Enhancements

### Phase 2
- Database integration (SQLite/PostgreSQL)
- Celery for distributed task queue
- WebSocket support for real-time updates
- Memory system integration endpoints
- VAPI deployment integration
- Close CRM integration

### Phase 3
- Authentication & authorization
- Rate limiting
- API versioning
- Caching (Redis)
- Comprehensive logging
- Metrics & monitoring

## Testing

```bash
# Run tests (once implemented)
pytest tests/test_api.py

# Run with coverage
pytest --cov=backend tests/
```

## Troubleshooting

**SuperOptiX Not Available**
- Install: `pip install superoptix`
- Check: `super --version`
- Set path in `.env`: `SUPEROPTIX_PATH=/path/to/super.exe`

**Port Already in Use**
- Change port: `uvicorn main:app --reload --port 8080`
- Or update `PORT` in `.env`

**CORS Errors**
- Add frontend URL to `cors_origins` in `config.py`
- Or set in `.env`: `CORS_ORIGINS=["http://localhost:8501"]`

## Development

### Adding New Endpoints

1. Create/modify router in `api/` directory
2. Add request/response models in `models/`
3. Register router in `main.py`
4. Update this README

### Code Style

- Follow PEP 8
- Use type hints
- Document with docstrings
- ASCII markers only (no emojis in backend code)

---

**Version**: 0.1.0
**Framework**: FastAPI 0.104+
**Python**: 3.10+
**Status**: Phase 2 - Backend Development Complete
