"""
Optimization Page - GEPA Workflow Management

Start, monitor, and manage agent optimizations using GEPA.
Track progress and compare baseline vs optimized performance.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from frontend.components.api_client import APIClient

# ========================================================================
# Page Configuration
# ========================================================================

st.set_page_config(
    page_title="Optimization - Mission Control",
    page_icon="🚀",
    layout="wide"
)

# ========================================================================
# Initialize Session State
# ========================================================================

if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient("http://localhost:8000")

if 'optimization_agent' not in st.session_state:
    st.session_state.optimization_agent = None

if 'optimization_running' not in st.session_state:
    st.session_state.optimization_running = False

# ========================================================================
# Page Header
# ========================================================================

st.title("🚀 Agent Optimization")
st.markdown("Optimize agents using GEPA (Genetic Prompt Adaptation)")

# ========================================================================
# Tabs
# ========================================================================

tab1, tab2, tab3 = st.tabs(["🎯 Start Optimization", "📊 Monitor Progress", "📈 Results & History"])

# ========================================================================
# Tab 1: Start Optimization
# ========================================================================

with tab1:
    st.markdown("## Start New Optimization")

    # Get available agents
    client = st.session_state.api_client
    agents_response = client.list_agents()

    if not agents_response.success:
        st.error(f"Failed to fetch agents: {agents_response.error}")

        if "Cannot connect" in str(agents_response.error):
            st.info("""
            **Backend Not Running**

            Start the FastAPI backend:
            ```bash
            cd backend && uvicorn main:app --reload
            ```
            """)
    elif not agents_response.data or len(agents_response.data) == 0:
        st.warning("No agents available. Add an agent first in the Agents page.")
    else:
        agents = agents_response.data

        # Optimization form
        with st.form("optimization_form"):
            st.markdown("### Configuration")

            # Agent selection
            agent_options = {agent['name']: agent['id'] for agent in agents}
            selected_agent_name = st.selectbox(
                "Select Agent",
                options=list(agent_options.keys()),
                help="Choose which agent to optimize"
            )
            selected_agent_id = agent_options[selected_agent_name]

            col1, col2 = st.columns(2)

            with col1:
                # Optimizer selection
                optimizer = st.selectbox(
                    "Optimizer",
                    options=["gepa", "mipro", "grid_search"],
                    index=0,
                    help="Optimization algorithm to use"
                )

                # Iterations
                iterations = st.slider(
                    "Iterations",
                    min_value=5,
                    max_value=50,
                    value=10,
                    help="Number of optimization iterations"
                )

            with col2:
                # Auto level
                auto_level = st.select_slider(
                    "Automation Level",
                    options=["low", "medium", "high"],
                    value="medium",
                    help="How much autonomy to give the optimizer"
                )

                # Optimization goal
                optimization_goal = st.selectbox(
                    "Primary Goal",
                    options=["accuracy", "latency", "cost", "balanced"],
                    index=3,
                    help="What to optimize for"
                )

            # Advanced settings
            with st.expander("Advanced Settings"):
                col1, col2 = st.columns(2)

                with col1:
                    population_size = st.number_input(
                        "Population Size",
                        min_value=5,
                        max_value=50,
                        value=10,
                        help="Number of candidates per generation (GEPA)"
                    )

                    mutation_rate = st.slider(
                        "Mutation Rate",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.3,
                        help="Probability of prompt mutation"
                    )

                with col2:
                    crossover_rate = st.slider(
                        "Crossover Rate",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.7,
                        help="Probability of prompt crossover"
                    )

                    early_stopping = st.checkbox(
                        "Early Stopping",
                        value=True,
                        help="Stop if no improvement for N iterations"
                    )

                    if early_stopping:
                        patience = st.number_input(
                            "Patience",
                            min_value=1,
                            max_value=10,
                            value=3,
                            help="Iterations without improvement before stopping"
                        )

            # Submit button
            submitted = st.form_submit_button(
                "🚀 Start Optimization",
                use_container_width=True,
                type="primary"
            )

            if submitted:
                st.markdown("---")
                st.markdown("### Starting Optimization...")

                # Prepare optimization parameters
                params = {
                    "auto_level": auto_level,
                    "optimization_goal": optimization_goal,
                    "population_size": population_size,
                    "mutation_rate": mutation_rate,
                    "crossover_rate": crossover_rate,
                    "early_stopping": early_stopping
                }

                if early_stopping:
                    params["patience"] = patience

                # Start optimization
                with st.spinner(f"Starting optimization for {selected_agent_name}..."):
                    result = client.start_optimization(
                        agent_id=selected_agent_id,
                        optimizer=optimizer,
                        iterations=iterations,
                        params=params
                    )

                if result.success:
                    st.success("Optimization started successfully!")
                    st.session_state.optimization_agent = selected_agent_id
                    st.session_state.optimization_running = True

                    # Show job details
                    if result.data:
                        st.json(result.data)

                    st.info("Switch to the 'Monitor Progress' tab to track optimization progress")
                else:
                    st.error(f"Failed to start optimization: {result.error}")

        st.markdown("---")

        # Optimization workflow explanation
        with st.expander("How Optimization Works"):
            st.markdown("""
            ### GEPA Optimization Process

            1. **Baseline Evaluation**: Run tests on current agent version
            2. **Initialize Population**: Create initial candidate prompts
            3. **Iterative Optimization**:
               - Evaluate all candidates
               - Select best performers
               - Apply genetic operations (mutation, crossover)
               - Create next generation
            4. **Convergence**: Stop when performance plateaus or max iterations reached
            5. **Final Evaluation**: Test optimized version
            6. **Comparison**: Show improvement vs baseline

            **Typical Results**: 10-20% improvement in success rate

            **Duration**: 5-30 minutes depending on agent complexity
            """)

# ========================================================================
# Tab 2: Monitor Progress
# ========================================================================

with tab2:
    st.markdown("## Optimization Progress")

    if st.session_state.optimization_agent and st.session_state.optimization_running:
        agent_id = st.session_state.optimization_agent

        # Progress header
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(f"### Optimizing: {agent_id}")

        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        with col3:
            auto_refresh = st.checkbox("Auto-refresh", value=True)

        st.markdown("---")

        # Get optimization status
        status_response = client.get_optimization_status(agent_id)

        if status_response.success and status_response.data:
            status = status_response.data

            # Progress metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                current_iter = status.get('current_iteration', 0)
                total_iter = status.get('total_iterations', 0)
                st.metric("Progress", f"{current_iter}/{total_iter}")

            with col2:
                best_score = status.get('best_score', 0)
                st.metric("Best Score", f"{best_score:.1f}%")

            with col3:
                elapsed_time = status.get('elapsed_seconds', 0)
                st.metric("Elapsed", f"{elapsed_time//60:.0f}m {elapsed_time%60:.0f}s")

            with col4:
                status_text = status.get('status', 'unknown')
                if status_text == 'running':
                    st.success("Running")
                elif status_text == 'completed':
                    st.success("Completed")
                    st.session_state.optimization_running = False
                elif status_text == 'failed':
                    st.error("Failed")
                    st.session_state.optimization_running = False
                else:
                    st.info(status_text.upper())

            # Progress bar
            if total_iter > 0:
                progress = current_iter / total_iter
                st.progress(progress)

            st.markdown("---")

            # Performance chart
            st.markdown("### Performance Over Iterations")

            if status.get('iteration_history'):
                history = status['iteration_history']

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(len(history))),
                    y=history,
                    mode='lines+markers',
                    name='Best Score',
                    line=dict(color='#1E88E5', width=3),
                    marker=dict(size=8)
                ))

                fig.update_layout(
                    xaxis_title="Iteration",
                    yaxis_title="Score (%)",
                    height=400,
                    showlegend=True,
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Performance data will appear as optimization progresses")

            st.markdown("---")

            # Live logs
            st.markdown("### Optimization Logs")

            log_container = st.container()
            with log_container:
                if status.get('logs'):
                    # Show recent logs
                    logs = status['logs']
                    st.text_area(
                        "Recent Activity",
                        value="\n".join(logs[-20:]) if isinstance(logs, list) else logs,
                        height=200,
                        disabled=True
                    )
                else:
                    st.info("No logs available yet")

            # Auto-refresh
            if auto_refresh and status_text == 'running':
                time.sleep(5)
                st.rerun()

        else:
            st.error(f"Failed to get optimization status: {status_response.error}")

            if st.button("Clear Optimization State"):
                st.session_state.optimization_agent = None
                st.session_state.optimization_running = False
                st.rerun()

    else:
        st.info("No active optimization. Start one in the 'Start Optimization' tab!")

        st.markdown("""
        ### Monitoring Features

        When an optimization is running, you'll see:

        - **Real-time Progress**: Current iteration and best score
        - **Performance Chart**: Score improvements over time
        - **Live Logs**: Detailed activity log
        - **Auto-refresh**: Automatic updates every 5 seconds
        """)

# ========================================================================
# Tab 3: Results & History
# ========================================================================

with tab3:
    st.markdown("## Optimization Results & History")

    # Agent selector
    col1, col2 = st.columns([3, 1])

    with col1:
        agents_response = client.list_agents()

        if agents_response.success and agents_response.data:
            agents = agents_response.data
            agent_options = {agent['name']: agent['id'] for agent in agents}

            selected_agent_name = st.selectbox(
                "Select Agent",
                options=list(agent_options.keys())
            )
            selected_agent_id = agent_options[selected_agent_name]
        else:
            st.warning("No agents available")
            selected_agent_id = None

    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    if selected_agent_id:
        st.markdown("---")

        # Get optimization history
        history_response = client.get_optimization_history(selected_agent_id)

        if history_response.success and history_response.data:
            history = history_response.data

            if len(history) > 0:
                st.markdown(f"### Optimization History ({len(history)} runs)")

                # Show latest result
                latest = history[0]

                # Comparison metrics
                st.markdown("#### Latest Optimization")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    baseline = latest.get('baseline_score', 0)
                    st.metric("Baseline", f"{baseline:.1f}%")

                with col2:
                    optimized = latest.get('optimized_score', 0)
                    st.metric("Optimized", f"{optimized:.1f}%")

                with col3:
                    improvement = optimized - baseline
                    st.metric("Improvement", f"+{improvement:.1f}%")

                with col4:
                    duration = latest.get('duration_minutes', 0)
                    st.metric("Duration", f"{duration:.1f}m")

                # Comparison chart
                st.markdown("#### Performance Comparison")

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    name='Baseline',
                    x=['Performance'],
                    y=[baseline],
                    marker_color='#FF9800'
                ))

                fig.add_trace(go.Bar(
                    name='Optimized',
                    x=['Performance'],
                    y=[optimized],
                    marker_color='#4CAF50'
                ))

                fig.update_layout(
                    barmode='group',
                    yaxis_title="Success Rate (%)",
                    height=400,
                    showlegend=True
                )

                st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")

                # Deployment actions
                st.markdown("#### Actions")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("🚀 Deploy Optimized Version", use_container_width=True):
                        with st.spinner("Deploying..."):
                            deploy_result = client.deploy_optimized(selected_agent_id)

                            if deploy_result.success:
                                st.success("Deployed successfully!")
                            else:
                                st.error(f"Deployment failed: {deploy_result.error}")

                with col2:
                    if st.button("↩️ Rollback to Baseline", use_container_width=True):
                        with st.spinner("Rolling back..."):
                            rollback_result = client.rollback_agent(selected_agent_id)

                            if rollback_result.success:
                                st.success("Rolled back successfully!")
                            else:
                                st.error(f"Rollback failed: {rollback_result.error}")

                with col3:
                    if st.button("📥 Download Results", use_container_width=True):
                        st.info("Download functionality coming soon")

                st.markdown("---")

                # Full history
                st.markdown("#### All Optimization Runs")

                with st.expander("View All History", expanded=False):
                    for idx, run in enumerate(history):
                        st.markdown(f"**Run {idx + 1}** - {run.get('timestamp', 'Unknown')}")
                        st.json(run)
                        st.markdown("---")

            else:
                st.info("No optimization history for this agent yet.")

        else:
            st.error(f"Failed to fetch history: {history_response.error}")

    else:
        st.info("Select an agent to view optimization history")

# ========================================================================
# Footer
# ========================================================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
