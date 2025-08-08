"""
Streamlit Chat Interface for Google Sheets Internship Journey Agent

Clean and simple interface for updating your internship journey Google Sheets 
with daily updates using AI-powered natural language processing.

To run: streamlit run app.py
"""

import streamlit as st
import os
import time
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from sheets_agent import SheetsAgent
from sheets_tools import GoogleSheetsManager

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Internship Journey Agent", 
    page_icon="📊",
    layout="wide"
)

# Clean CSS styling
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
        padding: 0;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: none;
    }
    
    .processing-step {
        padding: 8px 16px;
        margin: 4px 0;
        background-color: #f0f2f6;
        border-radius: 4px;
        border-left: 3px solid #1f77b4;
    }
    
    .processing-step.active {
        background-color: #e1f5fe;
        border-left-color: #2196f3;
    }
    
    .processing-step.completed {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
    
    .change-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        background: white;
    }
    
    .change-card.create {
        border-left: 4px solid #4caf50;
        background: #f9fff9;
    }
    
    .change-card.update {
        border-left: 4px solid #2196f3;
        background: #f8faff;
    }
    
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 500;
    }
    
    .status-complete {
        background: #e8f5e8;
        color: #2e7d32;
    }
    
    .status-progress {
        background: #fff3e0;
        color: #f57c00;
    }
    
    .status-upcoming {
        background: #e3f2fd;
        color: #1976d2;
    }
    
    .sidebar-stat {
        text-align: center;
        padding: 12px;
        margin: 8px 0;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e9ecef;
    }
    
    .sidebar-stat h3 {
        margin: 0;
        color: #1976d2;
    }
    
    .sidebar-stat p {
        margin: 4px 0 0 0;
        color: #666;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pending_changes' not in st.session_state:
    st.session_state.pending_changes = None
if 'sheet_data' not in st.session_state:
    st.session_state.sheet_data = None
if 'sheets_manager' not in st.session_state:
    try:
        st.session_state.sheets_manager = GoogleSheetsManager()
    except Exception as e:
        st.error(f"Failed to initialize Google Sheets connection: {e}")
        st.stop()

def show_processing_steps(steps, current_step):
    """Display processing steps with current progress"""
    for i, step in enumerate(steps):
        if i < current_step:
            st.markdown(f'<div class="processing-step completed">✅ {step}</div>', unsafe_allow_html=True)
        elif i == current_step:
            st.markdown(f'<div class="processing-step active">🔄 {step}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="processing-step">⏳ {step}</div>', unsafe_allow_html=True)

def create_change_card(change):
    """Create a clean change preview card"""
    action = change.get('action', 'unknown')
    data = change.get('data', {})
    reasoning = change.get('reasoning', '')
    
    # Status badge
    status = data.get('Status', 'Unknown')
    if status == 'Complete':
        status_html = '<span class="status-badge status-complete">Complete</span>'
    elif status == 'In Progress':
        status_html = '<span class="status-badge status-progress">In Progress</span>'
    else:
        status_html = '<span class="status-badge status-upcoming">Upcoming</span>'
    
    # Action icon
    action_icon = "✨ Create" if action == "create" else "🔄 Update"
    
    card_html = f"""
    <div class="change-card {action.lower()}">
        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 12px;">
            <strong>{action_icon}: {data.get('Task', 'Unknown Task')}</strong>
            <div style="margin-left: auto;">
                {status_html}
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
            <div><strong>Workstream:</strong> {data.get('Workstream', 'N/A')}</div>
            <div><strong>Priority:</strong> {data.get('Priority', 'N/A')}</div>
            <div><strong>Effort:</strong> {data.get('Effort', 'N/A')} days</div>
            <div><strong>Tags:</strong> {data.get('Tags', 'N/A')}</div>
        </div>
        
        {f'<div><strong>Sub Task:</strong> {data.get("Sub Task", "N/A")}</div>' if data.get("Sub Task") else ""}
        
        {f'<div style="margin-top: 8px; font-style: italic; color: #666;">💭 {reasoning}</div>' if reasoning else ""}
    </div>
    """
    return card_html

# Header
st.title("📊 Internship Journey Agent")
st.markdown("Transform your daily updates into structured Google Sheets tracking")

# Sidebar
with st.sidebar:
    st.header("📋 Dashboard")
    
    # Connection status
    if st.session_state.sheets_manager.get_development_mode_status():
        st.info("🔧 Development Mode\n\nUsing local CSV data")
    else:
        st.success("✅ Connected to Google Sheets")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        with st.spinner("Refreshing..."):
            st.session_state.sheet_data = st.session_state.sheets_manager.read_sheet_data()
            st.success("Data refreshed!")
            time.sleep(0.5)
            st.rerun()
    
    # Load data if needed
    if st.session_state.sheet_data is None:
        with st.spinner("Loading sheet data..."):
            st.session_state.sheet_data = st.session_state.sheets_manager.read_sheet_data()
    
    # Stats
    if st.session_state.sheet_data:
        sheet_info = st.session_state.sheets_manager.get_sheet_info()
        total_tasks = sheet_info.get('total_rows', 0)
        completed_tasks = len([row for row in st.session_state.sheet_data if row.get('Status') == 'Complete'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="sidebar-stat">
                <h3>{total_tasks}</h3>
                <p>Total Tasks</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="sidebar-stat">
                <h3>{completed_tasks}</h3>
                <p>Completed</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Workstreams
        workstreams = sheet_info.get('workstreams', [])
        if workstreams:
            st.markdown("**Active Workstreams:**")
            for ws in workstreams:
                if ws.strip():
                    st.markdown(f"• {ws}")
    
    # Data preview
    if st.session_state.sheet_data:
        with st.expander("View Sheet Data"):
            df = pd.DataFrame(st.session_state.sheet_data)
            st.dataframe(df, use_container_width=True, height=200)

# Chat interface
st.subheader("💬 Daily Updates")

# Chat history
for i, message in enumerate(st.session_state.chat_history):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])
            
            # Show changes if present
            if message.get("changes"):
                st.markdown("**Proposed Changes:**")
                for change in message["changes"]:
                    st.markdown(create_change_card(change), unsafe_allow_html=True)
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Apply Changes", key=f"apply_{i}"):
                        st.session_state.pending_changes = message["changes"]
                        st.rerun()
                with col2:
                    if st.button("❌ Reject Changes", key=f"reject_{i}"):
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "Changes rejected. Please provide different updates or clarify your requirements."
                        })
                        st.rerun()

# Process pending changes
if st.session_state.pending_changes:
    steps = ["Validating Changes", "Connecting to Sheets", "Applying Updates", "Refreshing Data"]
    
    st.markdown("### Applying Changes")
    progress_container = st.container()
    
    for step_idx, step in enumerate(steps):
        with progress_container:
            show_processing_steps(steps, step_idx)
        
        if step_idx == 0:
            time.sleep(0.5)
        elif step_idx == 1:
            time.sleep(0.3)
        elif step_idx == 2:
            success = st.session_state.sheets_manager.write_changes_to_sheet(
                st.session_state.pending_changes, 
                st.session_state.sheet_data
            )
            time.sleep(0.5)
        elif step_idx == 3:
            st.session_state.sheet_data = st.session_state.sheets_manager.read_sheet_data()
            time.sleep(0.3)
    
    # Final step
    with progress_container:
        show_processing_steps(steps, len(steps))
    
    if success:
        st.success("✅ Changes applied successfully!")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "Perfect! I've updated your internship journey sheet with the new information."
        })
    else:
        st.error("❌ Failed to apply changes. Please check your connection.")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "I encountered an issue updating the sheet. Please check your Google Sheets connection."
        })
    
    st.session_state.pending_changes = None
    time.sleep(1)
    st.rerun()

# Chat input
user_input = st.chat_input("Enter your daily updates... (e.g., 'Today I completed the authentication module and started database work')")

if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Process with feedback
    processing_steps = [
        "Analyzing update",
        "Understanding context", 
        "Matching workstreams",
        "Inferring status",
        "Generating changes"
    ]
    
    st.markdown("### Processing Your Update")
    progress_container = st.container()
    
    try:
        agent = SheetsAgent()
        
        for step_idx, step in enumerate(processing_steps):
            with progress_container:
                show_processing_steps(processing_steps, step_idx)
            
            if step_idx == 4:  # Last step - actual processing
                changes = agent.parse_daily_updates(user_input, st.session_state.sheet_data)
            else:
                time.sleep(0.4)  # Simulate processing
        
        # Complete
        with progress_container:
            show_processing_steps(processing_steps, len(processing_steps))
        
        if changes:
            validated_changes = agent.validate_changes(changes, st.session_state.sheet_data)
            
            response = f"**Analysis Complete!** I found {len(validated_changes)} change(s) for your sheet.\n\n"
            response += "**Summary:**\n"
            
            for i, change in enumerate(validated_changes, 1):
                action = change.get('action', 'unknown').title()
                task = change.get('data', {}).get('Task', 'Unknown task')
                status = change.get('data', {}).get('Status', 'Unknown')
                response += f"{i}. {action}: *{task}* → **{status}**\n"
            
            response += "\nReview the changes below and choose to apply or reject them."
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "changes": validated_changes
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "I couldn't identify specific changes from your update. Please be more specific about what you completed, what's in progress, or what's upcoming."
            })
    
    except Exception as e:
        st.error(f"Processing failed: {e}")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"I encountered an error processing your update: {str(e)}. Please try rephrasing your update."
        })
    
    st.rerun()

# Help section
with st.expander("💡 How to Use"):
    st.markdown("""
    **Tips for better results:**
    
    • **Be specific**: Mention what you completed, what's in progress, and what's upcoming
    • **Include timeframes**: "today", "this morning", "will finish by Friday"
    • **Reference existing work**: Connect updates to existing workstreams when possible
    
    **Example updates:**
    • "Today I completed the API documentation and started frontend testing"
    • "Finished debugging the auth system, now working on database integration"
    • "Attended team meeting, planning to implement the dashboard next week"
    """)

# Development mode notice
if st.session_state.sheets_manager.get_development_mode_status():
    st.info("""
    **Development Mode**: Working with local CSV data. To connect to Google Sheets:
    1. Set up a Google Service Account
    2. Add credentials to your `.env` file
    3. Add your Google Sheets ID
    4. Restart the application
    """)