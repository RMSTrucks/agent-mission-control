"""
Agent Mission Control - Main Dashboard

This is the main entry point for the Mission Control Streamlit UI.
Provides overview and navigation to all system components.

Run with:
    streamlit run app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from frontend.components.api_client import APIClient

# ========================================================================
# Page Configuration
# ========================================================================

st.set_page_config(
    page_title="Agent Mission Control",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================================================
# Initialize Session State
# ========================================================================

if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient("http://localhost:8000")

if 'backend_connected' not in st.session_state:
    st.session_state.backend_connected = False

# ========================================================================
# Custom CSS
# ========================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .metric-card {
        text-align: center;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
    }
    .success-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
    .error-badge {
        background-color: #F44336;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
    .warning-badge {
        background-color: #FF9800;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# ========================================================================
# Sidebar
# ========================================================================

with st.sidebar:
    st.markdown("# 🎯 Mission Control")
    st.markdown("---")

    # Backend connection status
    st.markdown("### System Status")

    # Check backend connection
    client = st.session_state.api_client
    health_check = client.health_check()

    if health_check.success:
        st.success("Backend Connected")
        st.session_state.backend_connected = True
    else:
        st.error("Backend Offline")
        st.session_state.backend_connected = False
        st.caption(f"Error: {health_check.error}")

    st.markdown("---")

    # Navigation info
    st.markdown("### Navigation")
    st.markdown("""
    - **Home**: System overview
    - **Dashboard**: Detailed metrics
    - **Agents**: Manage agents
    - **Optimization**: Run optimizations
    """)

    st.markdown("---")

    # Quick actions
    st.markdown("### Quick Actions")

    if st.button("Refresh Status", use_container_width=True):
        st.rerun()

    if st.button("Sync All Systems", use_container_width=True):
        with st.spinner("Syncing..."):
            # TODO: Implement sync functionality
            st.info("Sync functionality coming soon")

    st.markdown("---")

    # Settings
    with st.expander("Settings"):
        backend_url = st.text_input(
            "Backend URL",
            value="http://localhost:8000",
            help="URL of the FastAPI backend"
        )

        if st.button("Update Backend URL"):
            st.session_state.api_client = APIClient(backend_url)
            st.success("Backend URL updated!")
            st.rerun()

    st.markdown("---")
    st.caption("Claude 3.0 Mission Control")
    st.caption("Version 0.1.0")

# ========================================================================
# Main Content
# ========================================================================

st.markdown('<div class="main-header">🎯 Agent Mission Control</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI Agent Pipeline Management System</div>', unsafe_allow_html=True)

# Show backend connection warning if not connected
if not st.session_state.backend_connected:
    st.warning("""
    **Backend Not Connected**

    The FastAPI backend is not running. Please start it with:
    ```bash
    cd backend && uvicorn main:app --reload
    ```
    """)

# ========================================================================
# System Overview
# ========================================================================

st.markdown("## System Overview")

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Agents",
        value="0",
        delta="0 active",
        help="Total number of agents in the system"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Optimizations",
        value="0",
        delta="0 running",
        help="Active optimization jobs"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Evaluations",
        value="0",
        delta="0 today",
        help="Total evaluations run"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="Success Rate",
        value="0%",
        delta="N/A",
        help="Overall agent success rate"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ========================================================================
# Quick Start Guide
# ========================================================================

st.markdown("## Quick Start")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Getting Started")
    st.markdown("""
    1. **Start Backend**: Run the FastAPI server
       ```bash
       cd backend && uvicorn main:app --reload
       ```

    2. **Add Agents**: Go to the Agents page to add your first agent

    3. **Run Evaluation**: Test your agent with the evaluation workflow

    4. **Optimize**: Use GEPA to optimize agent performance

    5. **Deploy**: Deploy optimized agents to production
    """)

with col2:
    st.markdown("### System Components")
    st.markdown("""
    **SuperOptiX Integration**
    - Agent compilation and testing
    - GEPA optimization engine
    - Performance evaluation

    **External Systems**
    - VAPI phone bot management
    - Close CRM integration
    - Memory systems (Temporal + Hybrid)

    **Features**
    - Real-time optimization progress
    - Performance metrics and history
    - One-click deployment
    """)

st.markdown("---")

# ========================================================================
# Recent Activity
# ========================================================================

st.markdown("## Recent Activity")

# Show placeholder when no activity
st.info("No recent activity. Start by adding an agent in the Agents page!")

# TODO: Show actual recent activity from backend
# This will be populated once the backend is implemented

st.markdown("---")

# ========================================================================
# System Information
# ========================================================================

with st.expander("System Information"):
    st.markdown("### Backend API")
    backend_info = client.get_backend_info()
    st.json(backend_info)

    st.markdown("### Environment")
    st.json({
        "streamlit_version": st.__version__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    })

# ========================================================================
# Footer
# ========================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>Agent Mission Control</strong> - Claude 3.0 Producer + Pipeline Management</p>
    <p style="font-size: 0.875rem;">Built with Streamlit + FastAPI + SuperOptiX</p>
</div>
""", unsafe_allow_html=True)
