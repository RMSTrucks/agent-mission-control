# Agent Pipeline Management System

**Claude 3.0 Mission Control** - Custom pipeline management software for AI agents

## Overview

This is a custom-built pipeline management system that provides visibility and control over:
- **Memory systems** (Temporal Memory + Hybrid Intelligence)
- **Knowledge bases** (what agents know)
- **Context loading** (what's loaded into agents)
- **Agent optimization** (SuperOptiX backend with GEPA optimizer)
- **Multi-system orchestration** (VAPI phone bots, Close CRM, etc.)

**Key Features:**
- Single UI for all operations
- Workflow-oriented buttons (one click = complete workflow across systems)
- Real-time monitoring and analytics
- SuperOptiX optimization engine integration
- VAPI phone bot management
- Close CRM integration
- Memory system visualization

## Project Status

**Current Phase**: Foundation (Week 0)
- [x] Research SuperOptiX framework
- [x] Design architecture
- [x] Create project structure
- [ ] Initialize git repository
- [ ] Begin Phase 2: SuperOptiX integration

**Next**: Week 1 - SuperOptiX installation and integration

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for React frontend, later)
- Redis (for caching and Celery)
- Git

### Installation

```bash
# Clone repository
git clone <repo-url>
cd agent-mission-control

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install SuperOptiX
pip install superoptix

# Copy config template
cp config/settings.yaml.template config/settings.yaml

# Edit config with your API keys
# - VAPI_API_KEY
# - CLOSE_API_KEY
# - OPENAI_API_KEY

# Initialize database
python backend/init_db.py
```

### Running (Development)

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A backend.celery worker --loglevel=info

# Terminal 3: Start backend
cd backend
uvicorn main:app --reload

# Terminal 4: Start frontend
cd frontend
streamlit run app.py
```

Access UI at: http://localhost:8501

## Project Structure

```
agent-mission-control/
├── CLAUDE.md                   # Claude 3.0 identity
├── CLAUDE_3.0_VISION.md       # Complete vision
├── ARCHITECTURE.md             # Technical architecture
├── README.md                   # This file
├── requirements.txt            # Python dependencies
│
├── backend/                    # FastAPI server
│   ├── main.py                # API entry point
│   ├── api/                   # REST endpoints
│   ├── core/                  # Business logic
│   ├── integrations/          # External clients
│   └── models/                # Data models
│
├── frontend/                   # Streamlit UI
│   ├── app.py                 # Main dashboard
│   ├── pages/                 # Multi-page app
│   └── components/            # Reusable components
│
├── integrations/               # API client wrappers
│   ├── superoptix_client.py  # SuperOptiX wrapper
│   ├── vapi_client.py        # VAPI wrapper
│   ├── close_client.py       # Close CRM wrapper
│   └── memory_manager.py     # Memory systems
│
├── config/                     # Configuration
│   └── settings.yaml          # Main settings
│
├── data/                       # Local storage
│   ├── database.db           # SQLite database
│   └── logs/                 # System logs
│
├── memory/                     # Memory connectors
│   ├── temporal_connector.py # Temporal memory
│   └── hybrid_connector.py   # Hybrid intelligence
│
├── playbooks/                  # Knowledge base
│   └── integration_patterns.yaml
│
├── docs/                       # Documentation
│   ├── SUPEROPTIX_RESEARCH.md
│   ├── API.md
│   └── WORKFLOWS.md
│
├── tests/                      # Tests
│   └── test_*.py
│
└── .claude/                    # Claude config
    └── boot_sequence.md
```

## Key Concepts

### SuperOptiX Backend
SuperOptiX provides the optimization engine (GEPA), BDD testing framework, and SuperSpec DSL. We build the UI and integration layers on top.

**SuperOptiX provides (30%)**:
- Optimization engine (GEPA, DSPy optimizers)
- BDD testing framework
- CLI and Python API
- Agent compilation

**We build (70%)**:
- Complete UI/frontend
- Dashboards and visualization
- Integration layers (VAPI, Close, memory)
- Workflow automation
- Monitoring and analytics

### Workflow-Oriented Design
Actions are organized by user workflows, not system structure:
- "Optimize REMUS" button → handles conversion, baseline, optimization, deployment across multiple systems
- "View Memory" page → shows temporal + hybrid intelligence in unified view
- "Deploy All" button → updates VAPI, memory, Close CRM coherently

### Visual Verification
Claude (AI) builds this software and uses Screenpipe to visually verify it works. This creates an unprecedented feedback loop where the builder can see their own work.

## Example Workflows

### Optimize an Agent
1. Open Optimize page
2. Select agent (e.g., REMUS)
3. Choose optimizer (GEPA recommended)
4. Click "Optimize"
5. Watch real-time progress
6. Review comparison (baseline vs optimized)
7. Click "Deploy" to push to VAPI

### View Memory Pipeline
1. Open Memory page
2. See temporal memory stats (facts, preferences, context)
3. See hybrid intelligence stats (29K+ conversations)
4. Search across both systems
5. Click "Sync" to refresh

### Execute Agent
1. Open Execute page
2. Select agent
3. Enter inputs
4. Click "Run"
5. View outputs and logs

## API Documentation

See [docs/API.md](docs/API.md) for complete API reference.

**Quick examples:**

```bash
# List agents
curl http://localhost:8000/api/agents

# Evaluate agent
curl -X POST http://localhost:8000/api/evaluate/remus

# Optimize agent
curl -X POST http://localhost:8000/api/optimize/remus \
  -H "Content-Type: application/json" \
  -d '{"optimizer": "GEPA", "auto": "medium"}'

# Get system status
curl http://localhost:8000/api/system/status
```

## Development

### Adding a New Integration

1. Create client in `integrations/new_system_client.py`
2. Add routes in `backend/api/new_system.py`
3. Add UI page in `frontend/pages/new_system.py`
4. Update `config/settings.yaml` with new settings
5. Add tests in `tests/test_new_system.py`

### Running Tests

```bash
pytest tests/
pytest tests/test_api.py -v
pytest tests/ --cov=backend
```

### Code Quality

```bash
# Format code
black backend/ frontend/ integrations/

# Lint
flake8 backend/ frontend/ integrations/

# Type checking
mypy backend/
```

## Deployment

### Local Development
- Runs on localhost
- SQLite database
- Local Redis

### Production (Future)
- Docker containers
- PostgreSQL database
- Cloud Redis
- Environment-specific configs

## Contributing

This is a custom project for Jake's AI agent ecosystem. Development follows the Claude 3.0 Producer methodology with ACE (Generate → Reflect → Curate → Compound).

## Troubleshooting

### SuperOptiX Installation Issues
```bash
# Ensure Python 3.11+
python --version

# Install with verbose output
pip install superoptix -v

# Test installation
super --version
```

### Frontend Won't Start
```bash
# Check Streamlit installation
streamlit version

# Clear cache
streamlit cache clear

# Run with different port
streamlit run app.py --server.port 8502
```

### Backend API Errors
```bash
# Check logs
tail -f data/logs/backend.log

# Restart with debug mode
uvicorn main:app --reload --log-level debug
```

## Resources

- [Claude 3.0 Vision](CLAUDE_3.0_VISION.md) - Complete vision document
- [Architecture](ARCHITECTURE.md) - Technical architecture
- [SuperOptiX Research](docs/SUPEROPTIX_RESEARCH.md) - Framework capabilities
- [SuperOptiX Docs](https://superagenticai.github.io/superoptix-ai/) - Official documentation

## License

Proprietary - Jake Deaton

## Contact

Built by Claude 3.0 (AI Producer) for Jake's AI agent ecosystem.

---

**Version**: 0.1.0 (Foundation)
**Status**: Active Development
**Last Updated**: November 4, 2025
