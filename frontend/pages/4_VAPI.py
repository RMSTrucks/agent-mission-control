"""
VAPI Page - Phone Bot Management

Manage VAPI assistants, deploy optimized agents,
and handle phone number assignments.
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
    page_title="VAPI - Mission Control",
    page_icon="📞",
    layout="wide"
)

# ========================================================================
# Initialize Session State
# ========================================================================

if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient("http://localhost:8000")

if 'selected_assistant' not in st.session_state:
    st.session_state.selected_assistant = None

# ========================================================================
# Page Header
# ========================================================================

st.title("📞 VAPI Phone Bot Management")
st.markdown("Manage assistants, deploy optimized agents, and assign phone numbers")

# ========================================================================
# Check VAPI Status
# ========================================================================

client = st.session_state.api_client

# Make a simple GET request to VAPI status endpoint
vapi_status_response = client._make_request("GET", "/api/vapi/status")

vapi_connected = False
if vapi_status_response.success and vapi_status_response.data:
    vapi_connected = vapi_status_response.data.get('connected', False)

# Show status banner
if vapi_connected:
    st.success("VAPI Connected")
else:
    st.error("VAPI Not Connected")
    st.warning("""
    **VAPI Not Configured**

    To use VAPI integration, set the VAPI_API_KEY environment variable:
    ```bash
    export VAPI_API_KEY=your_vapi_api_key_here
    ```

    Then restart the backend server.
    """)

st.markdown("---")

# ========================================================================
# Tabs
# ========================================================================

tab1, tab2, tab3, tab4 = st.tabs(["📋 Assistants", "🚀 Deploy Agent", "📞 Phone Numbers", "📊 Call History"])

# ========================================================================
# Tab 1: Assistants
# ========================================================================

with tab1:
    st.markdown("## VAPI Assistants")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    if not vapi_connected:
        st.info("VAPI not connected. Configure VAPI_API_KEY to view assistants.")
    else:
        # Get assistants from backend
        assistants_response = client._make_request("GET", "/api/vapi/assistants")

        if assistants_response.success and assistants_response.data:
            assistants = assistants_response.data.get('assistants', [])

            if len(assistants) == 0:
                st.info("No assistants found. Create one to get started!")
            else:
                st.markdown(f"Found **{len(assistants)}** assistant(s)")

                # Display assistants
                for assistant in assistants:
                    with st.expander(f"📞 {assistant.get('name', 'Unknown')} - {assistant.get('id', 'N/A')}", expanded=False):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown("**Configuration**")
                            st.text(f"ID: {assistant.get('id', 'N/A')}")
                            st.text(f"Name: {assistant.get('name', 'Unknown')}")

                            # Voice info
                            voice = assistant.get('voice', {})
                            st.text(f"Voice Provider: {voice.get('provider', 'N/A')}")

                            # Model info
                            model = assistant.get('model', {})
                            st.text(f"Model: {model.get('provider', 'N/A')} {model.get('model', 'N/A')}")

                        with col2:
                            st.markdown("**Actions**")

                            if st.button("📝 Edit", key=f"edit_{assistant['id']}", use_container_width=True):
                                st.session_state.selected_assistant = assistant['id']
                                st.info(f"Selected: {assistant['name']}")

                            if st.button("🗑️ Delete", key=f"delete_{assistant['id']}", use_container_width=True):
                                if st.confirm(f"Delete assistant {assistant['name']}?"):
                                    delete_response = client._make_request(
                                        "DELETE",
                                        f"/api/vapi/assistants/{assistant['id']}"
                                    )
                                    if delete_response.success:
                                        st.success("Deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"Delete failed: {delete_response.error}")

                        # Show prompts
                        st.markdown("---")
                        st.markdown("**Prompts**")

                        with st.expander("View Prompts"):
                            st.markdown("**System Prompt:**")
                            st.text_area(
                                "System",
                                value=assistant.get('systemPrompt', 'N/A'),
                                height=150,
                                disabled=True,
                                key=f"sys_{assistant['id']}"
                            )

                            st.markdown("**First Message:**")
                            st.text_area(
                                "First",
                                value=assistant.get('firstMessage', 'N/A'),
                                height=100,
                                disabled=True,
                                key=f"first_{assistant['id']}"
                            )

        else:
            st.error(f"Failed to fetch assistants: {assistants_response.error}")

# ========================================================================
# Tab 2: Deploy Agent
# ========================================================================

with tab2:
    st.markdown("## Deploy Optimized Agent to VAPI")

    if not vapi_connected:
        st.info("VAPI not connected. Configure VAPI_API_KEY to deploy agents.")
    else:
        st.markdown("""
        This deploys optimized prompts from a GEPA optimization run to a VAPI assistant.
        The assistant's system prompt and first message will be updated.
        """)

        # Get assistants for dropdown
        assistants_response = client._make_request("GET", "/api/vapi/assistants")

        if assistants_response.success and assistants_response.data:
            assistants = assistants_response.data.get('assistants', [])

            if len(assistants) == 0:
                st.warning("No assistants available. Create one first in the Assistants tab.")
            else:
                with st.form("deploy_form"):
                    st.markdown("### Deployment Configuration")

                    # Select assistant
                    assistant_options = {f"{a['name']} ({a['id']})": a['id'] for a in assistants}
                    selected_assistant_name = st.selectbox(
                        "Select VAPI Assistant",
                        options=list(assistant_options.keys())
                    )
                    selected_assistant_id = assistant_options[selected_assistant_name]

                    # Optimized prompts
                    st.markdown("### Optimized Prompts")

                    system_prompt = st.text_area(
                        "System Prompt",
                        placeholder="Enter optimized system prompt...",
                        height=200,
                        help="The main system instructions for the assistant"
                    )

                    first_message = st.text_area(
                        "First Message",
                        placeholder="Enter optimized first message...",
                        height=100,
                        help="The initial greeting when a call starts"
                    )

                    # Deploy button
                    deploy_submitted = st.form_submit_button(
                        "🚀 Deploy to VAPI",
                        use_container_width=True,
                        type="primary"
                    )

                    if deploy_submitted:
                        if not system_prompt:
                            st.error("System prompt is required!")
                        else:
                            st.markdown("---")
                            st.markdown("### Deploying...")

                            with st.spinner(f"Deploying to {selected_assistant_name}..."):
                                deploy_response = client._make_request(
                                    "POST",
                                    "/api/vapi/deploy",
                                    data={
                                        "assistant_id": selected_assistant_id,
                                        "system_prompt": system_prompt,
                                        "first_message": first_message if first_message else None
                                    }
                                )

                            if deploy_response.success:
                                st.success(f"Successfully deployed to {selected_assistant_name}!")
                                st.json(deploy_response.data)
                            else:
                                st.error(f"Deployment failed: {deploy_response.error}")

        else:
            st.error(f"Failed to fetch assistants: {assistants_response.error}")

        st.markdown("---")

        st.markdown("### Tips")
        st.info("""
        **Best Practices:**
        - Test optimized prompts thoroughly before deployment
        - Deploy during low-traffic periods
        - Keep a backup of the previous configuration
        - Monitor call performance after deployment
        """)

# ========================================================================
# Tab 3: Phone Numbers
# ========================================================================

with tab3:
    st.markdown("## Phone Number Management")

    if not vapi_connected:
        st.info("VAPI not connected. Configure VAPI_API_KEY to manage phone numbers.")
    else:
        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("🔄 Refresh Numbers", use_container_width=True):
                st.rerun()

        # Get phone numbers
        numbers_response = client._make_request("GET", "/api/vapi/phone-numbers")

        if numbers_response.success and numbers_response.data:
            phone_numbers = numbers_response.data.get('phone_numbers', [])

            if len(phone_numbers) == 0:
                st.info("No phone numbers found.")
            else:
                st.markdown(f"Found **{len(phone_numbers)}** phone number(s)")

                # Display phone numbers
                for number in phone_numbers:
                    with st.expander(f"📞 {number.get('number', 'Unknown')} - {number.get('name', 'Unnamed')}", expanded=False):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown("**Details**")
                            st.text(f"Number: {number.get('number', 'N/A')}")
                            st.text(f"Name: {number.get('name', 'N/A')}")
                            st.text(f"ID: {number.get('id', 'N/A')}")

                            # Assignment
                            assistant_id = number.get('assistantId')
                            if assistant_id:
                                st.text(f"Assigned to: {assistant_id}")
                            else:
                                st.text("Not assigned")

                        with col2:
                            st.markdown("**Actions**")

                            if st.button("🔗 Assign", key=f"assign_{number['id']}", use_container_width=True):
                                st.info("Use the assign form below")

                # Assign phone number form
                st.markdown("---")
                st.markdown("### Assign Phone Number to Assistant")

                # Get assistants
                assistants_response = client._make_request("GET", "/api/vapi/assistants")

                if assistants_response.success:
                    assistants = assistants_response.data.get('assistants', [])

                    if len(assistants) > 0 and len(phone_numbers) > 0:
                        with st.form("assign_number_form"):
                            col1, col2 = st.columns(2)

                            with col1:
                                number_options = {f"{n.get('number', 'Unknown')} - {n.get('name', 'Unnamed')}": n['id'] for n in phone_numbers}
                                selected_number_name = st.selectbox("Select Phone Number", options=list(number_options.keys()))
                                selected_number_id = number_options[selected_number_name]

                            with col2:
                                assistant_options = {f"{a['name']} ({a['id']})": a['id'] for a in assistants}
                                selected_assistant_name = st.selectbox("Select Assistant", options=list(assistant_options.keys()))
                                selected_assistant_id = assistant_options[selected_assistant_name]

                            assign_submitted = st.form_submit_button("🔗 Assign", use_container_width=True)

                            if assign_submitted:
                                with st.spinner("Assigning..."):
                                    assign_response = client._make_request(
                                        "POST",
                                        f"/api/vapi/phone-numbers/{selected_number_id}/assign",
                                        data={"assistant_id": selected_assistant_id}
                                    )

                                if assign_response.success:
                                    st.success(f"Phone number assigned to {selected_assistant_name}!")
                                    st.rerun()
                                else:
                                    st.error(f"Assignment failed: {assign_response.error}")

        else:
            st.error(f"Failed to fetch phone numbers: {numbers_response.error}")

# ========================================================================
# Tab 4: Call History
# ========================================================================

with tab4:
    st.markdown("## Call History")

    if not vapi_connected:
        st.info("VAPI not connected. Configure VAPI_API_KEY to view call history.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("🔄 Refresh Calls", use_container_width=True):
                st.rerun()

        with col2:
            # Filter by assistant
            assistants_response = client._make_request("GET", "/api/vapi/assistants")
            if assistants_response.success:
                assistants = assistants_response.data.get('assistants', [])
                assistant_filter = st.selectbox(
                    "Filter by Assistant",
                    options=["All"] + [f"{a['name']} ({a['id']})" for a in assistants]
                )

        # Get calls
        params = {}
        if assistant_filter != "All":
            # Extract assistant ID from selection
            assistant_id = assistant_filter.split("(")[1].rstrip(")")
            params["assistant_id"] = assistant_id

        calls_response = client._make_request("GET", "/api/vapi/calls", params=params)

        if calls_response.success and calls_response.data:
            calls = calls_response.data.get('calls', [])

            if len(calls) == 0:
                st.info("No calls found.")
            else:
                st.markdown(f"Found **{len(calls)}** call(s)")

                # Display calls
                for call in calls:
                    with st.expander(f"📞 Call {call.get('id', 'Unknown')} - {call.get('createdAt', 'N/A')}", expanded=False):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown("**Call Details**")
                            st.text(f"ID: {call.get('id', 'N/A')}")
                            st.text(f"Assistant: {call.get('assistantId', 'N/A')}")
                            st.text(f"Duration: {call.get('duration', 0)} seconds")
                            st.text(f"Status: {call.get('status', 'Unknown')}")
                            st.text(f"Created: {call.get('createdAt', 'N/A')}")

                        with col2:
                            st.markdown("**Actions**")

                            if st.button("📄 View Transcript", key=f"transcript_{call['id']}", use_container_width=True):
                                transcript_response = client._make_request("GET", f"/api/vapi/calls/{call['id']}")

                                if transcript_response.success:
                                    st.json(transcript_response.data)
                                else:
                                    st.error(f"Failed to load: {transcript_response.error}")

        else:
            st.error(f"Failed to fetch calls: {calls_response.error}")

# ========================================================================
# Footer
# ========================================================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
