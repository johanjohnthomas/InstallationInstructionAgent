"""
Streamlit Web Application for the Installation Guide Generator.

This script provides a user-friendly web interface for the Research Agent.
Users can input a software name and specific device configurations (as key-value pairs)
to generate a tailored installation guide in either DOCX or Markdown format.

To run the application:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Make sure your .env file has the required API keys (OPENAI_API_KEY or GROQ_API_KEY).
3. Run the app from your terminal: `streamlit run app.py`
"""
import streamlit as st
import os
from dotenv import load_dotenv
from research_agent import ResearchAgent
from docx_generator import generate_document_from_markdown

load_dotenv()

st.set_page_config(layout="centered", page_title="Installation Guide Generator")

st.title("Installation Guide Generator")
st.write("Enter the software name and device configuration to generate an installation guide.")

software_name = st.text_input("Software Name", placeholder="e.g., Docker, VS Code")

st.subheader("Device Configuration (Key-Value Pairs)")

# Dynamic key-value pair input
config_pairs = []
num_pairs = st.session_state.get('num_pairs', 1)

for i in range(num_pairs):
    col1, col2 = st.columns(2)
    with col1:
        key = st.text_input(f"Key {i+1}", key=f"key_{i}", placeholder="e.g., OS, Version")
    with col2:
        value = st.text_input(f"Value {i+1}", key=f"value_{i}", placeholder="e.g., Ubuntu 22.04, 1.80.0")
    if key or value:
        config_pairs.append((key, value))

# Add/Remove buttons for key-value pairs
col_add_remove_buttons = st.columns(2)
with col_add_remove_buttons[0]:
    if st.button("Add More Fields"):
        st.session_state.num_pairs = num_pairs + 1
        st.experimental_rerun()
with col_add_remove_buttons[1]:
    if num_pairs > 1 and st.button("Remove Last Field"):
        st.session_state.num_pairs = num_pairs - 1
        st.experimental_rerun()

output_format = st.radio(
    "Select Output Format",
    ('DOCX', 'Markdown'),
    index=0, # Default to DOCX
    horizontal=True
)

if st.button("Generate Guide"):
    if not software_name:
        st.error("Please enter the Software Name.")
    else:
        # Convert config_pairs to a readable string for the agent
        device_config_str = ", ".join([f"{key}: {value}" for key, value in config_pairs if key and value])
        if not device_config_str:
            device_config_str = "Default configuration"

        # Determine the correct format code ('docx' or 'md')
        output_format_code = "md" if output_format == "Markdown" else "docx"

        st.session_state['software_name'] = software_name
        st.session_state['device_config_str'] = device_config_str
        st.session_state['output_format'] = output_format_code
        st.session_state['generate_clicked'] = True

        with st.spinner(f"Generating guide for {software_name} on {device_config_str} in {output_format} format... This may take a few minutes."):
            try:
                agent = ResearchAgent()
                guide_content = agent.generate_guide(software_name, device_config_str)

                if guide_content.startswith("Final answer: "):
                    guide_content = guide_content[len("Final answer: "):].strip()

                title = f"{software_name} Installation Guide for {device_config_str}"
                output_filename_base = f"{software_name.replace(' ', '_')}_Installation_Guide"
                
                generate_document_from_markdown(title, guide_content, output_filename_base, output_format_code)
                
                st.success(f"Successfully generated {output_format.upper()} file: {output_filename_base}.{output_format_code}")

                # Provide download button
                file_path = f"{output_filename_base}.{output_format_code}"
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        btn = st.download_button(
                            label=f"Download {output_format.upper()} File",
                            data=file,
                            file_name=os.path.basename(file_path),
                            mime=f"application/{output_format_code}" if output_format_code == "docx" else "text/markdown"
                        )
                else:
                    st.error(f"Generated file not found: {file_path}")

            except ValueError as e:
                st.error(f"Error initializing ResearchAgent: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred during guide generation: {e}")



