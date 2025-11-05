# Mission Control Frontend

Streamlit-based UI for Agent Pipeline Management System.

## Features

- **Dashboard**: Real-time system metrics and performance monitoring
- **Agent Management**: List, compile, test, and manage AI agents
- **Optimization Workflows**: Start and monitor GEPA optimization runs
- **Backend Integration**: REST API client for FastAPI backend

## Setup

### Prerequisites

```bash
# Install dependencies from project root
pip install -r requirements.txt
```

### Running the App

```bash
# From the frontend directory
streamlit run app.py

# Or from project root
cd frontend && streamlit run app.py
```

The app will start on `http://localhost:8501`

## Backend Connection

The frontend connects to the FastAPI backend at `http://localhost:8000` by default.

**Start the backend first:**

```bash
cd backend
uvicorn main:app --reload
```

If the backend is not running, the UI will show a warning and limited functionality.

## Pages

### Home (app.py)
- System overview
- Quick start guide
- Backend connection status
- Recent activity feed

### Dashboard (pages/1_Dashboard.py)
- System status indicators
- Performance metrics
- Agent health overview
- Performance trends charts
- Resource monitoring

### Agents (pages/2_Agents.py)
- Agent list with status
- Add new agents
- Compile agents to SuperSpec
- Run agent tests
- View agent details and history

### Optimization (pages/3_Optimization.py)
- Configure optimization parameters
- Start GEPA optimization runs
- Monitor real-time progress
- View optimization history
- Compare baseline vs optimized
- Deploy optimized versions

## API Client

The `components/api_client.py` provides a clean interface to backend endpoints:

```python
from frontend.components.api_client import APIClient

client = APIClient("http://localhost:8000")

# List agents
response = client.list_agents()
if response.success:
    agents = response.data
    for agent in agents:
        print(agent['name'])

# Start optimization
result = client.start_optimization(
    agent_id="remus",
    optimizer="gepa",
    iterations=10
)
```

## Configuration

Backend URL can be changed in the sidebar settings or by modifying the default in session state.

## Error Handling

The app gracefully handles:
- Backend offline/unavailable
- Network timeouts
- Invalid responses
- Missing data

All errors are displayed in the UI with helpful messages.

## Development

### Adding New Pages

1. Create file: `frontend/pages/N_PageName.py`
2. Pages are auto-discovered by Streamlit
3. Use naming convention: `N_PageName.py` where N is display order

### Adding API Endpoints

1. Add method to `components/api_client.py`
2. Follow existing patterns for error handling
3. Return `APIResponse` objects

### Custom Styling

CSS styles are in `app.py` in the `st.markdown()` section. Modify as needed.

## Troubleshooting

**Backend Connection Failed**
- Ensure backend is running on port 8000
- Check firewall/network settings
- Verify backend URL in settings

**Import Errors**
- Run from correct directory
- Ensure dependencies are installed
- Check Python path

**Streamlit Won't Start**
- Install streamlit: `pip install streamlit`
- Check port 8501 is not in use
- Try different port: `streamlit run app.py --server.port 8502`

## Next Steps

### Phase 2 Enhancements
- WebSocket support for real-time updates
- Memory system integration UI
- Advanced visualization components
- Agent execution playground
- Cost tracking and monitoring

### Phase 3 Production
- Migrate to React/Next.js
- Advanced authentication
- Role-based access control
- Custom themes
- Mobile responsive design

## Support

For issues or questions:
- Check backend logs
- Review API client responses
- Enable Streamlit debug mode: `streamlit run app.py --logger.level=debug`

---

**Version**: 0.1.0
**Built with**: Streamlit, Python 3.12+
**Status**: Phase 1 - MVP Complete
