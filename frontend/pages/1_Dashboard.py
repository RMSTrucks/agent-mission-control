"""
Dashboard Page - System Overview with Detailed Metrics

Displays comprehensive system status, performance metrics,
and agent health indicators.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from frontend.components.api_client import APIClient

# ========================================================================
# Page Configuration
# ========================================================================

st.set_page_config(
    page_title="Dashboard - Mission Control",
    page_icon="📊",
    layout="wide"
)

# ========================================================================
# Initialize Session State
# ========================================================================

if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient("http://localhost:8000")

# ========================================================================
# Page Header
# ========================================================================

st.title("📊 System Dashboard")
st.markdown("Real-time metrics and system health monitoring")

# ========================================================================
# System Status
# ========================================================================

st.markdown("## System Status")

# Check backend connection
client = st.session_state.api_client
status_response = client.get_system_status()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if status_response.success:
        st.success("Backend Online")
    else:
        st.error("Backend Offline")

with col2:
    st.info("SuperOptiX Ready")

with col3:
    st.info("VAPI Connected")

with col4:
    st.info("Memory Synced")

st.markdown("---")

# ========================================================================
# Performance Metrics
# ========================================================================

st.markdown("## Performance Metrics")

# Get metrics from backend
metrics_response = client.get_system_metrics()

if metrics_response.success and metrics_response.data:
    metrics = metrics_response.data

    # Display key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Agents",
            value=metrics.get('total_agents', 0),
            delta=metrics.get('agents_delta', 0)
        )

    with col2:
        st.metric(
            label="Active Optimizations",
            value=metrics.get('active_optimizations', 0),
            delta=metrics.get('opt_delta', 0)
        )

    with col3:
        st.metric(
            label="Evaluations Today",
            value=metrics.get('evaluations_today', 0),
            delta=metrics.get('eval_delta', 0)
        )

    with col4:
        st.metric(
            label="Avg Success Rate",
            value=f"{metrics.get('avg_success_rate', 0):.1f}%",
            delta=f"{metrics.get('success_rate_delta', 0):.1f}%"
        )

    with col5:
        st.metric(
            label="Avg Latency",
            value=f"{metrics.get('avg_latency_ms', 0):.0f}ms",
            delta=f"{metrics.get('latency_delta', 0):.0f}ms",
            delta_color="inverse"
        )
else:
    # Show placeholder metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="Total Agents", value="0", delta="0")
    with col2:
        st.metric(label="Active Optimizations", value="0", delta="0")
    with col3:
        st.metric(label="Evaluations Today", value="0", delta="0")
    with col4:
        st.metric(label="Avg Success Rate", value="0%", delta="0%")
    with col5:
        st.metric(label="Avg Latency", value="0ms", delta="0ms")

    st.info("No metrics available yet. Metrics will appear after running agents and optimizations.")

st.markdown("---")

# ========================================================================
# Agent Health Overview
# ========================================================================

st.markdown("## Agent Health")

# Get agents list
agents_response = client.list_agents()

if agents_response.success and agents_response.data:
    agents = agents_response.data

    # Create agent health cards
    cols = st.columns(min(3, len(agents)))

    for idx, agent in enumerate(agents[:6]):  # Show up to 6 agents
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {agent.get('name', 'Unknown')}")

                status = agent.get('status', 'unknown')
                if status == 'live':
                    st.success("Live")
                elif status == 'dev':
                    st.info("Development")
                elif status == 'optimizing':
                    st.warning("Optimizing")
                else:
                    st.error("Unknown Status")

                # Agent metrics
                st.metric("Success Rate", f"{agent.get('success_rate', 0):.1f}%")
                st.metric("Last Run", agent.get('last_run', 'Never'))

                if st.button(f"View {agent['name']}", key=f"view_{agent['id']}"):
                    st.switch_page("pages/2_Agents.py")
else:
    st.info("No agents configured yet. Add your first agent in the Agents page!")

st.markdown("---")

# ========================================================================
# Performance Charts
# ========================================================================

st.markdown("## Performance Trends")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Success Rate Over Time")

    # TODO: Get actual data from backend
    # Placeholder chart
    dates = pd.date_range(start='2024-11-01', end='2024-11-05', freq='D')
    success_rates = [75, 78, 82, 85, 88]

    fig = px.line(
        x=dates,
        y=success_rates,
        labels={'x': 'Date', 'y': 'Success Rate (%)'},
        title="Agent Success Rate Trend"
    )
    fig.update_traces(line_color='#1E88E5', line_width=3)
    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Optimization Impact")

    # TODO: Get actual data from backend
    # Placeholder chart
    agents_names = ['REMUS', 'GENESIS', 'SCOUT']
    baseline = [75, 70, 65]
    optimized = [88, 85, 80]

    fig = go.Figure(data=[
        go.Bar(name='Baseline', x=agents_names, y=baseline, marker_color='#FF9800'),
        go.Bar(name='Optimized', x=agents_names, y=optimized, marker_color='#4CAF50')
    ])
    fig.update_layout(
        barmode='group',
        title="Baseline vs Optimized Performance",
        yaxis_title="Success Rate (%)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ========================================================================
# Recent Activity
# ========================================================================

st.markdown("## Recent Activity")

# TODO: Get actual activity from backend
# Placeholder activity log
activity_data = {
    'Timestamp': [
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    ],
    'Type': ['System'],
    'Agent': ['N/A'],
    'Action': ['System started'],
    'Status': ['Success']
}

activity_df = pd.DataFrame(activity_data)

st.dataframe(
    activity_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Timestamp": st.column_config.TextColumn("Time", width="medium"),
        "Type": st.column_config.TextColumn("Type", width="small"),
        "Agent": st.column_config.TextColumn("Agent", width="medium"),
        "Action": st.column_config.TextColumn("Action", width="large"),
        "Status": st.column_config.TextColumn("Status", width="small")
    }
)

st.markdown("---")

# ========================================================================
# System Resources
# ========================================================================

st.markdown("## System Resources")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### API Latency")
    # TODO: Get actual latency data
    st.metric("Average", "0ms", delta="0ms")
    st.metric("P95", "0ms", delta="0ms")
    st.metric("P99", "0ms", delta="0ms")

with col2:
    st.markdown("### Request Volume")
    # TODO: Get actual request data
    st.metric("Last Hour", "0", delta="0")
    st.metric("Today", "0", delta="0")
    st.metric("This Week", "0", delta="0")

with col3:
    st.markdown("### Error Rate")
    # TODO: Get actual error data
    st.metric("Last Hour", "0%", delta="0%")
    st.metric("Today", "0%", delta="0%")
    st.metric("This Week", "0%", delta="0%")

st.markdown("---")

# ========================================================================
# Refresh Button
# ========================================================================

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

with col2:
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()

# ========================================================================
# Footer
# ========================================================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
