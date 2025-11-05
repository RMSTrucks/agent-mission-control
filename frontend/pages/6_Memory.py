"""
Memory Page - Temporal Memory & Hybrid Intelligence

Manage curated facts, preferences, conversation search,
and agent context loading.
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
    page_title="Memory - Mission Control",
    page_icon="🧠",
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

st.title("🧠 Memory System")
st.markdown("Temporal Memory (facts, preferences) + Hybrid Intelligence (conversation search)")

# ========================================================================
# Check Memory Status
# ========================================================================

client = st.session_state.api_client
status_response = client._make_request("GET", "/api/memory/status")

memory_status = {}
if status_response.success and status_response.data:
    memory_status = status_response.data.get('status', {})

# Show status banner
temporal_status = memory_status.get('temporal', {}).get('status', 'unknown')
hybrid_status = memory_status.get('hybrid', {}).get('status', 'unknown')
overall_status = memory_status.get('overall', 'unknown')

col1, col2, col3 = st.columns(3)

with col1:
    if temporal_status == 'healthy':
        st.success("Temporal Memory: Connected")
    else:
        st.warning("Temporal Memory: Offline")

with col2:
    if hybrid_status == 'healthy':
        st.success("Hybrid Intelligence: Connected")
    else:
        st.warning("Hybrid Intelligence: Offline")

with col3:
    if overall_status == 'healthy':
        st.success("Overall: Healthy")
    else:
        st.warning("Overall: Degraded")

st.markdown("---")

# ========================================================================
# Tabs
# ========================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Facts",
    "⚙️ Preferences",
    "🔍 Search Conversations",
    "🤖 Agent Context",
    "📊 Statistics"
])

# ========================================================================
# Tab 1: Facts
# ========================================================================

with tab1:
    st.markdown("## Curated Facts")

    col1, col2 = st.columns([1, 3])

    with col1:
        tier_filter = st.selectbox(
            "Filter by Tier",
            options=["All", "Tier 1", "Tier 2", "Tier 3"],
            help="Tier 1 = most important, Tier 3 = least important"
        )

        if st.button("🔄 Refresh Facts", use_container_width=True):
            st.rerun()

    # Get facts from backend
    params = {}
    if tier_filter != "All":
        tier = int(tier_filter.split(" ")[1])
        params["tier"] = tier

    facts_response = client._make_request("GET", "/api/memory/facts", params=params)

    if facts_response.success and facts_response.data:
        facts = facts_response.data.get('facts', [])

        if len(facts) == 0:
            st.info("No facts found. Add facts to build agent context.")
        else:
            st.markdown(f"Found **{len(facts)}** fact(s)")

            # Group by tier
            facts_by_tier = {1: [], 2: [], 3: []}
            for fact in facts:
                tier = fact.get('tier', 3)
                facts_by_tier[tier].append(fact)

            # Display by tier
            for tier in [1, 2, 3]:
                tier_facts = facts_by_tier[tier]
                if tier_facts:
                    with st.expander(f"📌 Tier {tier} ({len(tier_facts)} facts)", expanded=(tier == 1)):
                        for fact in tier_facts:
                            st.markdown(f"- {fact.get('content', 'N/A')}")
                            if fact.get('created_at'):
                                st.caption(f"Added: {fact['created_at']}")
                            st.markdown("---")

    else:
        st.error(f"Failed to fetch facts: {facts_response.error}")

    st.markdown("---")

    # Add new fact
    st.markdown("### Add New Fact")

    with st.form("add_fact_form"):
        fact_content = st.text_area(
            "Fact Content",
            placeholder="Enter a curated fact about the user or system...",
            height=100
        )

        fact_tier = st.select_slider(
            "Tier",
            options=[1, 2, 3],
            value=3,
            help="1 = most important, 3 = least important"
        )

        add_fact_submitted = st.form_submit_button("Add Fact", use_container_width=True)

        if add_fact_submitted:
            if not fact_content:
                st.error("Fact content is required!")
            else:
                add_response = client._make_request(
                    "POST",
                    "/api/memory/facts",
                    data={
                        "content": fact_content,
                        "tier": fact_tier
                    }
                )

                if add_response.success:
                    st.success("Fact added successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to add fact: {add_response.error}")

# ========================================================================
# Tab 2: Preferences
# ========================================================================

with tab2:
    st.markdown("## User Preferences")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔄 Refresh Preferences", use_container_width=True):
            st.rerun()

    # Get preferences from backend
    prefs_response = client._make_request("GET", "/api/memory/preferences")

    if prefs_response.success and prefs_response.data:
        preferences = prefs_response.data.get('preferences', [])

        if len(preferences) == 0:
            st.info("No preferences found. Add preferences to personalize agent behavior.")
        else:
            st.markdown(f"Found **{len(preferences)}** preference(s)")

            for pref in preferences:
                st.markdown(f"- {pref.get('content', 'N/A')}")
                if pref.get('created_at'):
                    st.caption(f"Added: {pref['created_at']}")
                st.markdown("---")

    else:
        st.error(f"Failed to fetch preferences: {prefs_response.error}")

    st.markdown("---")

    # Add new preference
    st.markdown("### Add New Preference")

    with st.form("add_pref_form"):
        pref_content = st.text_area(
            "Preference Content",
            placeholder="Enter a user preference...",
            height=100
        )

        add_pref_submitted = st.form_submit_button("Add Preference", use_container_width=True)

        if add_pref_submitted:
            if not pref_content:
                st.error("Preference content is required!")
            else:
                add_response = client._make_request(
                    "POST",
                    "/api/memory/preferences",
                    data={"content": pref_content}
                )

                if add_response.success:
                    st.success("Preference added successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to add preference: {add_response.error}")

# ========================================================================
# Tab 3: Search Conversations
# ========================================================================

with tab3:
    st.markdown("## Search Conversations")
    st.caption("Full-text search across 29K+ indexed conversations via Hybrid Intelligence")

    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])

        with col1:
            search_query = st.text_input(
                "Search Query",
                placeholder="Enter search keywords...",
                help="Search across conversation summaries and content"
            )

        with col2:
            search_limit = st.number_input(
                "Max Results",
                min_value=1,
                max_value=50,
                value=10
            )

        search_submitted = st.form_submit_button("🔍 Search", use_container_width=True)

    if search_submitted and search_query:
        with st.spinner("Searching conversations..."):
            search_response = client._make_request(
                "POST",
                "/api/memory/search",
                data={
                    "query": search_query,
                    "limit": search_limit
                }
            )

        if search_response.success and search_response.data:
            results = search_response.data.get('results', [])
            count = search_response.data.get('count', 0)

            st.success(f"Found {count} result(s)")

            if results:
                for result in results:
                    with st.expander(
                        f"📄 {result.get('summary', 'No summary')} (Score: {result.get('relevance_score', 0):.2f})",
                        expanded=False
                    ):
                        st.markdown("**Summary:**")
                        st.write(result.get('summary', 'N/A'))

                        st.markdown("**Content Preview:**")
                        st.text_area(
                            "Content",
                            value=result.get('content', 'N/A'),
                            height=150,
                            disabled=True,
                            key=f"content_{result['id']}"
                        )

                        st.caption(f"ID: {result['id']}")
                        st.caption(f"Timestamp: {result.get('timestamp', 'N/A')}")

                        if result.get('metadata'):
                            st.caption(f"Metadata: {result['metadata']}")

        else:
            st.error(f"Search failed: {search_response.error}")

# ========================================================================
# Tab 4: Agent Context
# ========================================================================

with tab4:
    st.markdown("## Agent Context")
    st.caption("Complete context package for an agent (facts + preferences + conversations)")

    # Agent selector
    agent_id = st.text_input(
        "Agent ID",
        value="remus",
        help="Enter agent identifier (e.g., remus, genesis, scout)"
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("📥 Load Context", use_container_width=True, type="primary"):
            with st.spinner(f"Loading context for {agent_id}..."):
                context_response = client._make_request(
                    "GET",
                    f"/api/memory/context/{agent_id}"
                )

            if context_response.success and context_response.data:
                context = context_response.data.get('context', {})
                formatted = context_response.data.get('formatted', '')

                st.markdown("---")

                # Context summary
                st.markdown("### Context Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Facts", len(context.get('facts', [])))
                with col2:
                    st.metric("Preferences", len(context.get('preferences', [])))
                with col3:
                    st.metric("Context Items", len(context.get('context_items', [])))
                with col4:
                    st.metric("Conversations", len(context.get('relevant_conversations', [])))

                st.markdown("---")

                # Formatted context for agent
                st.markdown("### Formatted Context (for Agent Prompt)")

                st.text_area(
                    "Context to inject into agent",
                    value=formatted,
                    height=300,
                    help="Copy this and inject into agent system prompt"
                )

                # Raw context
                with st.expander("View Raw Context Data"):
                    st.json(context)

            else:
                st.error(f"Failed to load context: {context_response.error}")

# ========================================================================
# Tab 5: Statistics
# ========================================================================

with tab5:
    st.markdown("## Memory Statistics")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔄 Refresh Stats", use_container_width=True):
            st.rerun()

        st.markdown("---")

        if st.button("🔄 Sync All Memory", use_container_width=True, type="primary"):
            with st.spinner("Syncing..."):
                sync_response = client._make_request("POST", "/api/memory/sync")

            if sync_response.success:
                st.success("Sync completed!")
                sync_data = sync_response.data
                st.json(sync_data)
                st.rerun()
            else:
                st.error(f"Sync failed: {sync_response.error}")

    # Get stats
    stats_response = client._make_request("GET", "/api/memory/stats")

    if stats_response.success and stats_response.data:
        stats = stats_response.data.get('stats', {})

        # Temporal Memory stats
        st.markdown("### Temporal Memory")

        temporal_stats = stats.get('temporal', {})
        if temporal_stats:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                facts_stats = temporal_stats.get('facts', {})
                st.metric("Total Facts", facts_stats.get('total', 0))

            with col2:
                st.metric("Tier 1", facts_stats.get('tier_1', 0))

            with col3:
                st.metric("Tier 2", facts_stats.get('tier_2', 0))

            with col4:
                st.metric("Tier 3", facts_stats.get('tier_3', 0))

            st.metric("Preferences", temporal_stats.get('preferences', 0))
            st.metric("Context Items", temporal_stats.get('context', 0))

            if temporal_stats.get('last_sync'):
                st.caption(f"Last sync: {temporal_stats['last_sync']}")

        # Hybrid Intelligence stats
        st.markdown("### Hybrid Intelligence")

        hybrid_stats = stats.get('hybrid', {})
        if hybrid_stats:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Conversations", f"{hybrid_stats.get('total_conversations', 0):,}")
                st.metric("Indexed Messages", f"{hybrid_stats.get('indexed_messages', 0):,}")

            with col2:
                date_range = hybrid_stats.get('date_range', {})
                st.text(f"Earliest: {date_range.get('earliest', 'N/A')}")
                st.text(f"Latest: {date_range.get('latest', 'N/A')}")

            st.metric("Index Size", f"{hybrid_stats.get('index_size_mb', 0)} MB")

            if hybrid_stats.get('last_indexed'):
                st.caption(f"Last indexed: {hybrid_stats['last_indexed']}")

        # Cached contexts
        st.markdown("### Cache")
        st.metric("Cached Agent Contexts", stats.get('cached_contexts', 0))

    else:
        st.error(f"Failed to fetch stats: {stats_response.error}")

# ========================================================================
# Footer
# ========================================================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
