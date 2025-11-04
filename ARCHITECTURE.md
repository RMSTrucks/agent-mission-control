# Agent Pipeline Management System - Technical Architecture

**Project**: Claude 3.0 Mission Control
**Date**: November 4, 2025
**Status**: Design Complete

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE LAYER                        │
│              (Streamlit → React + TailwindCSS)                   │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐          │
│  │   Home   │ │  Agents  │ │ Optimize │ │  Memory   │          │
│  │Dashboard │ │Management│ │ Workflow │ │  System   │          │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST + WebSocket
┌───────────────────────────┴─────────────────────────────────────┐
│                     BACKEND API LAYER                            │
│                    (FastAPI + Python)                            │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Agents    │  │  Evaluate   │  │  Optimize   │             │
│  │   Routes    │  │   Routes    │  │   Routes    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Execute    │  │   Memory    │  │   System    │             │
│  │   Routes    │  │   Routes    │  │   Routes    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Python API Calls
┌───────────────────────────┴─────────────────────────────────────┐
│                  INTEGRATION LAYER                               │
│                    (Python Clients)                              │
│                                                                   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│ │ SuperOptiX  │ │    VAPI     │ │    Close    │ │  Memory   │ │
│ │   Client    │ │   Client    │ │   Client    │ │  Manager  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ External APIs / MCP
┌───────────────────────────┴─────────────────────────────────────┐
│                   EXTERNAL SYSTEMS                               │
│                                                                   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│ │ SuperOptiX  │ │VAPI Phone   │ │Close CRM    │ │ Memory    │ │
│ │   Engine    │ │Bots (Live)  │ │(29K+ leads) │ │  MCPs     │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: User Interface

### Technology
- **Phase 1 (MVP)**: Streamlit
  - Rapid development and iteration
  - Python-native (same language as backend)
  - Built-in components and widgets
  - Auto-reloading on code changes
  - Easy to see via Screenpipe

- **Phase 2 (Production)**: React + Next.js (if needed)
  - More polished UI
  - Better performance
  - Custom components
  - Advanced visualizations

### Pages/Views

**Home Dashboard**
- System status overview
- Quick actions panel
- Recent activity feed
- Agent health indicators
- Memory/knowledge stats

**Agents Page**
- List all agents (REMUS, GENESIS, SCOUT, etc.)
- Agent status cards (live, dev, optimizing, etc.)
- Quick actions: View, Edit, Optimize, Deploy
- Performance metrics per agent

**Optimize Workflow Page**
- Select agent to optimize
- Configure optimizer (GEPA, MIPRO, etc.)
- Set parameters (auto level, metrics, etc.)
- Run optimization
- Real-time progress display
- Results comparison (baseline vs optimized)
- Deploy button

**Execute Page**
- Select agent
- Enter inputs
- Execute agent with real data
- Display outputs
- Show execution logs

**Memory System Page**
- Temporal Memory view (facts, preferences, context)
- Hybrid Intelligence view (conversation search)
- Sync buttons for each system
- Search across both systems
- Configure context loading

**Monitoring Page**
- Performance metrics over time
- Cost tracking (tokens, API calls)
- Error logs
- System health dashboard

### UI Components
- Agent status cards
- Progress indicators
- Action buttons with loading states
- Real-time log viewers
- Comparison charts
- Configuration forms

---

## Layer 2: Backend API

### Technology
- **FastAPI**: Modern Python async framework
- **Uvicorn**: ASGI server
- **Celery**: Async task queue for long-running operations
- **Redis**: Message broker + caching
- **SQLAlchemy**: ORM for database
- **WebSockets**: Real-time updates to frontend

### API Routes

#### Agents (`/api/agents`)
```python
GET    /api/agents              # List all agents
GET    /api/agents/:id          # Get agent details
POST   /api/agents              # Create new agent
PUT    /api/agents/:id          # Update agent
DELETE /api/agents/:id          # Delete agent
POST   /api/agents/:id/compile  # Compile SuperSpec to pipeline
GET    /api/agents/:id/status   # Get agent status
```

#### Evaluation (`/api/evaluate`)
```python
POST   /api/evaluate/:agent_id                # Run evaluation
GET    /api/evaluate/:agent_id/history        # Evaluation history
GET    /api/evaluate/:agent_id/latest         # Latest results
POST   /api/evaluate/:agent_id/baseline       # Set baseline
```

#### Optimization (`/api/optimize`)
```python
POST   /api/optimize/:agent_id                # Start optimization
GET    /api/optimize/:agent_id/status         # Check progress
GET    /api/optimize/:agent_id/history        # Optimization history
POST   /api/optimize/:agent_id/deploy         # Deploy optimized version
POST   /api/optimize/:agent_id/rollback       # Rollback to baseline
```

#### Execution (`/api/execute`)
```python
POST   /api/execute/:agent_id                 # Execute agent
GET    /api/execute/:agent_id/history         # Execution history
GET    /api/execute/:agent_id/logs            # Execution logs
```

#### Memory (`/api/memory`)
```python
GET    /api/memory/temporal                   # Get temporal memory
GET    /api/memory/hybrid                     # Get hybrid intelligence
POST   /api/memory/sync                       # Sync from sources
POST   /api/memory/search                     # Search across systems
GET    /api/memory/context/:agent_id          # Get agent context
PUT    /api/memory/context/:agent_id          # Update agent context
```

#### System (`/api/system`)
```python
GET    /api/system/status                     # Overall system health
GET    /api/system/metrics                    # Performance metrics
GET    /api/system/logs                       # System logs
POST   /api/system/sync-all                   # Sync all systems
```

### WebSocket Endpoints
```python
WS     /ws/optimize/:agent_id                 # Real-time optimization progress
WS     /ws/evaluate/:agent_id                 # Real-time evaluation progress
WS     /ws/logs                               # Real-time log streaming
WS     /ws/system                             # Real-time system status
```

### Background Tasks (Celery)
- Long-running optimizations (5-30 minutes)
- Batch evaluations
- Memory synchronization
- Report generation

---

## Layer 3: Integration Layer

### SuperOptiX Client

**File**: `integrations/superoptix_client.py`

**Responsibilities**:
- Wrap SuperOptiX CLI commands
- Parse SuperOptiX output
- Convert between formats
- Handle errors gracefully

**Key Methods**:
```python
class SuperOptiXClient:
    def compile_agent(agent_name: str) -> CompileResult
    def evaluate_agent(agent_name: str, load_optimized: bool = False) -> EvaluationResult
    def optimize_agent(agent_name: str, optimizer: str = "GEPA", params: dict) -> OptimizationResult
    def run_agent(agent_name: str, goal: str) -> ExecutionResult
    def get_agent_status(agent_name: str) -> AgentStatus
```

**Implementation Pattern**:
```python
import subprocess
import json

def evaluate_agent(self, agent_name: str) -> EvaluationResult:
    """Run evaluation via SuperOptiX CLI"""
    cmd = f"super agent evaluate {agent_name} --format json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        raise SuperOptiXError(result.stderr)

    data = json.loads(result.stdout)
    return EvaluationResult.from_dict(data)
```

### VAPI Client

**File**: `integrations/vapi_client.py`

**Responsibilities**:
- Manage VAPI assistants (REMUS, GENESIS, SCOUT)
- Update assistant configuration
- Deploy new versions
- Monitor call logs

**Key Methods**:
```python
class VAPIClient:
    def get_assistant(assistant_id: str) -> Assistant
    def update_assistant(assistant_id: str, config: dict) -> Assistant
    def deploy_optimized(assistant_id: str, optimized_prompts: dict) -> bool
    def get_call_logs(assistant_id: str, limit: int = 100) -> List[CallLog]
```

### Close Client

**File**: `integrations/close_client.py`

**Responsibilities**:
- Access Close CRM data
- Sync leads and contacts
- Query call transcripts
- Update custom fields

**Key Methods**:
```python
class CloseClient:
    def get_leads(filters: dict = None) -> List[Lead]
    def get_call_transcript(call_id: str) -> Transcript
    def update_lead(lead_id: str, data: dict) -> Lead
    def search_leads(query: str) -> List[Lead]
```

### Memory Manager

**File**: `integrations/memory_manager.py`

**Responsibilities**:
- Connect to Temporal Memory MCP
- Connect to Hybrid Intelligence MCP
- Synchronize data
- Provide unified search

**Key Methods**:
```python
class MemoryManager:
    def get_temporal_memory(tier: str = "all") -> TemporalMemory
    def search_hybrid_intelligence(query: str) -> List[SearchResult]
    def get_agent_context(agent_name: str) -> AgentContext
    def sync_all() -> SyncStatus
```

---

## Layer 4: Data Layer

### Database Schema (SQLite → PostgreSQL)

**Tables**:

**agents**
```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'phone_bot', 'webhook', 'standalone'
    status TEXT NOT NULL,  -- 'live', 'dev', 'optimizing', 'error'
    superspec_path TEXT,
    vapi_assistant_id TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**evaluations**
```sql
CREATE TABLE evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT REFERENCES agents(id),
    timestamp TIMESTAMP,
    pass_rate REAL,
    avg_confidence REAL,
    is_baseline BOOLEAN,
    is_optimized BOOLEAN,
    results_json TEXT,  -- Full evaluation results
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

**optimizations**
```sql
CREATE TABLE optimizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT REFERENCES agents(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT,  -- 'running', 'completed', 'failed'
    optimizer TEXT,  -- 'GEPA', 'MIPRO', etc.
    params_json TEXT,
    improvement_pct REAL,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

**executions**
```sql
CREATE TABLE executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT REFERENCES agents(id),
    timestamp TIMESTAMP,
    input_json TEXT,
    output_json TEXT,
    latency_ms INTEGER,
    cost_usd REAL,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

**system_logs**
```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP,
    level TEXT,  -- 'info', 'warning', 'error'
    source TEXT,  -- 'superoptix', 'vapi', 'close', etc.
    message TEXT,
    details_json TEXT
);
```

---

## Data Flow Examples

### Example 1: Optimize Agent Workflow

```
User clicks "Optimize REMUS"
    ↓
Frontend: POST /api/optimize/remus {optimizer: "GEPA", auto: "medium"}
    ↓
Backend: Create optimization record in DB (status: 'running')
    ↓
Backend: Queue Celery task for optimization
    ↓
Celery Worker: Call SuperOptiXClient.optimize_agent()
    ↓
SuperOptiX: Runs GEPA optimization (5-15 min)
    ↓
During optimization:
    - Celery Worker: Streams progress via WebSocket
    - Frontend: Updates UI with real-time progress
    ↓
SuperOptiX: Optimization complete, returns results
    ↓
Celery Worker: Run post-optimization evaluation
    ↓
Celery Worker: Update optimization record (status: 'completed')
    ↓
Celery Worker: Create evaluation record (is_optimized: true)
    ↓
Celery Worker: Send completion via WebSocket
    ↓
Frontend: Display comparison (baseline vs optimized)
    ↓
User clicks "Deploy"
    ↓
Frontend: POST /api/optimize/remus/deploy
    ↓
Backend: Call VAPIClient.deploy_optimized()
    ↓
VAPI: Updates assistant with new prompts
    ↓
Backend: Update agent status to 'live'
    ↓
Frontend: Show success message
```

### Example 2: View Memory Pipeline

```
User opens "Memory" page
    ↓
Frontend: GET /api/memory/temporal
Frontend: GET /api/memory/hybrid
Frontend: GET /api/memory/context/remus
    ↓
Backend: Call MemoryManager.get_temporal_memory()
Backend: Call MemoryManager.get_hybrid_intelligence_stats()
Backend: Call MemoryManager.get_agent_context('remus')
    ↓
Memory Manager: Query temporal-memory MCP
Memory Manager: Query hybrid-intelligence MCP
Memory Manager: Load agent context from config
    ↓
Backend: Return aggregated data
    ↓
Frontend: Render memory overview
    - Show facts, preferences, context counts
    - Show hybrid intelligence stats
    - Show what's loaded in REMUS
    ↓
User clicks "Sync Now"
    ↓
Frontend: POST /api/memory/sync
    ↓
Backend: Call MemoryManager.sync_all()
    ↓
Memory Manager: Refresh from MCPs
    ↓
Backend: Return updated data
    ↓
Frontend: Update display with new counts
```

---

## Deployment Architecture

### Development
```
Local machine:
- Backend: http://localhost:8000 (FastAPI)
- Frontend: http://localhost:8501 (Streamlit)
- Redis: localhost:6379
- Database: ./data/database.db (SQLite)
```

### Production (Future)
```
Docker containers:
- backend-api (FastAPI + Celery)
- frontend-ui (React build served by nginx)
- redis (message broker + cache)
- postgres (database)

Environment variables:
- SUPEROPTIX_PATH
- VAPI_API_KEY
- CLOSE_API_KEY
- OPENAI_API_KEY (for SuperOptiX)
- DATABASE_URL
- REDIS_URL
```

---

## Security Considerations

### API Keys
- Store in `.env` file (not committed to git)
- Load via environment variables
- Encrypt at rest if needed

### Authentication (Future)
- Basic auth for MVP
- OAuth/JWT for production
- Role-based access control

### Data Privacy
- Agent configurations may contain sensitive prompts
- Call logs may contain PII
- Memory system contains personal facts/preferences
- Ensure proper access control

---

## Performance Considerations

### Async Operations
- All API routes async (FastAPI native)
- Long-running operations in Celery
- WebSocket for real-time updates

### Caching
- Redis cache for frequently accessed data
- Agent configurations
- Memory system snapshots
- System status

### Database Optimization
- Indexes on foreign keys
- Indexes on timestamp fields
- Periodic vacuum/analyze

### Frontend Optimization
- Lazy loading for large datasets
- Pagination for lists
- Debounced search inputs
- Cached API responses

---

## Error Handling

### Backend Errors
```python
@app.exception_handler(SuperOptiXError)
async def superoptix_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "SuperOptiX operation failed", "details": str(exc)}
    )
```

### Frontend Errors
- Show error messages in UI
- Log to system_logs table
- Retry logic for transient failures
- Graceful degradation

---

## Monitoring & Observability

### Metrics to Track
- API request latency
- Optimization success rate
- Agent performance over time
- System resource usage
- Error rates by component

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log storage
- Search and filter capabilities

### Alerts (Future)
- Agent performance degradation
- System errors
- API failures
- Resource exhaustion

---

## Testing Strategy

### Unit Tests
- Test each integration client
- Test API route logic
- Test data models
- Test utility functions

### Integration Tests
- Test API endpoints end-to-end
- Test SuperOptiX integration
- Test VAPI integration
- Test memory system integration

### E2E Tests (Future)
- Test complete workflows
- Test UI interactions
- Test WebSocket connections

---

## Technology Choices Rationale

### FastAPI vs Flask
- FastAPI: Native async, better performance, automatic docs
- Flask: More mature, simpler for basic apps
- **Choice**: FastAPI (modern, async-first)

### Streamlit vs React
- Streamlit: Rapid development, Python-native
- React: More polished, better for complex UIs
- **Choice**: Streamlit first (MVP), React later (production)

### SQLite vs PostgreSQL
- SQLite: Simple, no setup, good for local development
- PostgreSQL: More features, better for production
- **Choice**: SQLite first, migrate to PostgreSQL as needed

### Celery vs Background Tasks
- Celery: More robust, distributed task queue
- Background Tasks: Simpler, built into FastAPI
- **Choice**: Celery (optimizations are long-running, need robust queuing)

---

**Document Status**: Complete
**Last Updated**: November 4, 2025
**Next Review**: After Phase 2 (SuperOptiX integration)
