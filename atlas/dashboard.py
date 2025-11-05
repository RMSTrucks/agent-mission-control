"""
ATLAS Dashboard - Simple Chat Interface

Run with: streamlit run dashboard.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from run_atlas import ATLASAgent, config

# Page config
st.set_page_config(
    page_title="ATLAS Agent Dashboard",
    page_icon="SUCCESS:",
    layout="wide"
)

# Initialize agent in session state
if 'agent' not in st.session_state:
    st.session_state.agent = ATLASAgent()
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("SUCCESS: ATLAS Agent")
    st.caption(f"v{config['version']}")

    st.divider()

    st.subheader("Configuration")
    st.text(f"Model: {config['model']['name']}")
    st.text(f"Temperature: {config['model']['temperature']}")
    st.text(f"Max Context: {config['conversation']['max_context_length']}")

    st.divider()

    st.subheader("Status")
    st.success("Agent Ready")

    memory_enabled = config['memory']['enabled']
    st.text(f"Memory: {'Enabled' if memory_enabled else 'Disabled'}")

    knowledge_enabled = config['knowledge']['enabled']
    st.text(f"Knowledge: {'Enabled' if knowledge_enabled else 'Disabled'}")

    tools_count = len(config['tools'])
    st.text(f"Tools: {tools_count}")

    st.divider()

    if st.button("Reset Conversation", type="primary"):
        st.session_state.agent.reset()
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("About ATLAS")
    st.caption(config['description'])

    st.divider()

    st.caption(f"Stage: {config['metadata']['stage']}")
    st.caption(f"Author: {config['metadata']['author']}")

# Main chat interface
st.title("Chat with ATLAS")

# Display greeting if no messages
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        greeting = st.session_state.agent.get_greeting()
        st.write(greeting)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Add to messages
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.chat(prompt)
            st.write(response)

    # Add to messages
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Messages",
        len(st.session_state.messages)
    )

with col2:
    st.metric(
        "Conversation Depth",
        len(st.session_state.agent.conversation_history)
    )

with col3:
    st.metric(
        "Model",
        config['model']['name'].split('-')[-1].upper()
    )
