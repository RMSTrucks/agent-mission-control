"""
Agents Page - Agent Management

List, compile, test, and manage AI agents.
Provides interface to SuperOptiX agent operations.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from frontend.components.api_client import APIClient

# ========================================================================
# Page Configuration
# ========================================================================

st.set_page_config(
    page_title="Agents - Mission Control",
    page_icon="🤖",
    layout="wide"
)

# ========================================================================
# Initialize Session State
# ========================================================================

if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient("http://localhost:8000")

if 'selected_agent' not in st.session_state:
    st.session_state.selected_agent = None

# ========================================================================
# Page Header
# ========================================================================

st.title("🤖 Agent Management")
st.markdown("Manage, compile, and test your AI agents")

# ========================================================================
# Tabs
# ========================================================================

tab1, tab2, tab3 = st.tabs(["📋 Agent List", "➕ Add Agent", "🔍 Agent Details"])

# ========================================================================
# Tab 1: Agent List
# ========================================================================

with tab1:
    st.markdown("## Available Agents")

    # Refresh button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Refresh List", use_container_width=True):
            st.rerun()

    # Get agents from backend
    client = st.session_state.api_client
    agents_response = client.list_agents()

    if not agents_response.success:
        st.error(f"Failed to fetch agents: {agents_response.error}")

        # Show helpful message if backend is offline
        if "Cannot connect" in str(agents_response.error):
            st.info("""
            **Backend Not Running**

            Start the FastAPI backend:
            ```bash
            cd backend && uvicorn main:app --reload
            ```
            """)
    elif not agents_response.data or len(agents_response.data) == 0:
        # No agents yet
        st.info("No agents configured yet. Add your first agent using the 'Add Agent' tab!")

        st.markdown("""
        ### Quick Start

        1. Click the **Add Agent** tab
        2. Enter agent name and details
        3. Click **Create Agent**
        4. Compile and test your agent
        """)
    else:
        # Display agents
        agents = agents_response.data

        st.markdown(f"Found **{len(agents)}** agent(s)")

        # Create agent cards
        for agent in agents:
            with st.expander(f"🤖 {agent.get('name', 'Unknown')} - {agent.get('status', 'unknown').upper()}", expanded=True):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.markdown("**Details**")
                    st.text(f"ID: {agent.get('id', 'N/A')}")
                    st.text(f"Type: {agent.get('type', 'N/A')}")
                    st.text(f"Status: {agent.get('status', 'unknown')}")

                with col2:
                    st.markdown("**Performance**")
                    st.text(f"Success Rate: {agent.get('success_rate', 0):.1f}%")
                    st.text(f"Last Run: {agent.get('last_run', 'Never')}")
                    st.text(f"Total Runs: {agent.get('total_runs', 0)}")

                with col3:
                    st.markdown("**Actions**")

                    # View details button
                    if st.button("📊 View", key=f"view_{agent['id']}", use_container_width=True):
                        st.session_state.selected_agent = agent['id']
                        st.info(f"Selected agent: {agent['name']}")

                    # Compile button
                    if st.button("🔨 Compile", key=f"compile_{agent['id']}", use_container_width=True):
                        with st.spinner(f"Compiling {agent['name']}..."):
                            result = client.compile_agent(agent['id'])

                            if result.success:
                                st.success("Compilation successful!")
                                if result.data:
                                    st.json(result.data)
                            else:
                                st.error(f"Compilation failed: {result.error}")

                    # Test button
                    if st.button("🧪 Test", key=f"test_{agent['id']}", use_container_width=True):
                        with st.spinner(f"Running tests for {agent['name']}..."):
                            result = client.evaluate_agent(agent['id'])

                            if result.success:
                                st.success("Tests completed!")
                                if result.data:
                                    st.json(result.data)
                            else:
                                st.error(f"Tests failed: {result.error}")

                st.markdown("---")

                # Additional agent info
                with st.container():
                    info_col1, info_col2 = st.columns(2)

                    with info_col1:
                        if agent.get('superspec_path'):
                            st.text(f"SuperSpec: {agent['superspec_path']}")

                    with info_col2:
                        if agent.get('vapi_assistant_id'):
                            st.text(f"VAPI ID: {agent['vapi_assistant_id']}")

# ========================================================================
# Tab 2: Add Agent
# ========================================================================

with tab2:
    st.markdown("## Add New Agent")

    with st.form("add_agent_form"):
        st.markdown("### Agent Details")

        agent_name = st.text_input(
            "Agent Name",
            placeholder="e.g., REMUS, GENESIS, SCOUT",
            help="Unique name for the agent"
        )

        agent_type = st.selectbox(
            "Agent Type",
            options=["phone_bot", "webhook", "standalone"],
            help="Type of agent deployment"
        )

        agent_description = st.text_area(
            "Description",
            placeholder="Describe what this agent does...",
            help="Agent description and purpose"
        )

        col1, col2 = st.columns(2)

        with col1:
            superspec_path = st.text_input(
                "SuperSpec Path (optional)",
                placeholder="path/to/agent.yaml",
                help="Path to SuperSpec YAML file"
            )

        with col2:
            vapi_assistant_id = st.text_input(
                "VAPI Assistant ID (optional)",
                placeholder="asst_xxxxx",
                help="VAPI assistant ID if already exists"
            )

        submitted = st.form_submit_button("Create Agent", use_container_width=True)

        if submitted:
            if not agent_name:
                st.error("Agent name is required!")
            else:
                # TODO: Create agent via API
                st.info("Agent creation will be implemented when backend is ready")

                # Show what would be sent
                st.json({
                    "name": agent_name,
                    "type": agent_type,
                    "description": agent_description,
                    "superspec_path": superspec_path if superspec_path else None,
                    "vapi_assistant_id": vapi_assistant_id if vapi_assistant_id else None
                })

    st.markdown("---")

    st.markdown("### Import from SuperSpec")

    with st.form("import_superspec_form"):
        spec_file = st.file_uploader(
            "Upload SuperSpec YAML",
            type=['yaml', 'yml'],
            help="Import agent from existing SuperSpec file"
        )

        import_submitted = st.form_submit_button("Import", use_container_width=True)

        if import_submitted:
            if spec_file is not None:
                st.info("SuperSpec import will be implemented when backend is ready")
                st.text(f"File: {spec_file.name}")
            else:
                st.warning("Please select a file to import")

# ========================================================================
# Tab 3: Agent Details
# ========================================================================

with tab3:
    st.markdown("## Agent Details")

    if st.session_state.selected_agent:
        agent_id = st.session_state.selected_agent

        # Get agent details
        agent_response = client.get_agent(agent_id)

        if agent_response.success and agent_response.data:
            agent = agent_response.data

            # Agent header
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"### {agent.get('name', 'Unknown')}")
                st.caption(f"ID: {agent_id}")

            with col2:
                status = agent.get('status', 'unknown')
                if status == 'live':
                    st.success("Live")
                elif status == 'dev':
                    st.info("Development")
                elif status == 'optimizing':
                    st.warning("Optimizing")
                else:
                    st.error(status.upper())

            with col3:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()

            st.markdown("---")

            # Agent metrics
            st.markdown("### Performance Metrics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Success Rate", f"{agent.get('success_rate', 0):.1f}%")
            with col2:
                st.metric("Total Runs", agent.get('total_runs', 0))
            with col3:
                st.metric("Avg Latency", f"{agent.get('avg_latency_ms', 0):.0f}ms")
            with col4:
                st.metric("Last Run", agent.get('last_run', 'Never'))

            st.markdown("---")

            # Action buttons
            st.markdown("### Actions")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("🔨 Compile Agent", use_container_width=True):
                    with st.spinner("Compiling..."):
                        result = client.compile_agent(agent_id)

                        if result.success:
                            st.success("Compilation successful!")
                            with st.expander("View Output"):
                                st.text(result.output)
                        else:
                            st.error(f"Compilation failed: {result.error}")

            with col2:
                if st.button("🧪 Run Tests", use_container_width=True):
                    with st.spinner("Running tests..."):
                        result = client.evaluate_agent(agent_id)

                        if result.success:
                            st.success("Tests completed!")
                            with st.expander("View Results"):
                                st.json(result.data)
                        else:
                            st.error(f"Tests failed: {result.error}")

            with col3:
                if st.button("🚀 Optimize", use_container_width=True):
                    st.info("Use the Optimization page to optimize this agent")
                    st.session_state.optimization_agent = agent_id

            with col4:
                if st.button("📊 View History", use_container_width=True):
                    st.info("Fetching history...")
                    history_response = client.get_evaluation_history(agent_id)

                    if history_response.success:
                        st.json(history_response.data)
                    else:
                        st.error(f"Failed to fetch history: {history_response.error}")

            st.markdown("---")

            # Agent configuration
            st.markdown("### Configuration")

            with st.expander("View Full Configuration", expanded=False):
                st.json(agent)

            # Evaluation history
            st.markdown("### Recent Evaluations")

            eval_history = client.get_evaluation_history(agent_id)

            if eval_history.success and eval_history.data:
                # TODO: Display evaluation history in a nice table
                st.json(eval_history.data)
            else:
                st.info("No evaluation history yet. Run tests to see results here.")

        else:
            st.error(f"Failed to load agent details: {agent_response.error}")

    else:
        st.info("Select an agent from the Agent List to view details")

        st.markdown("""
        ### How to View Agent Details

        1. Go to the **Agent List** tab
        2. Click **View** on any agent
        3. Details will appear here
        """)

# ========================================================================
# Footer
# ========================================================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
