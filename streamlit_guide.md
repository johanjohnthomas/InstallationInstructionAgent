# Streamlit Web Interface Guide

## Overview

This guide explains how to use the Streamlit web application for the Research Agent. The web app provides a user-friendly interface for generating custom software installation guides without needing to use the command line.

## How to Run the Application

Before running, ensure you have all the necessary dependencies installed and your environment variables are set up correctly.

1.  **Install Dependencies:**
    Open your terminal and run the following command from the project's root directory:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Up Environment Variables:**
    Make sure you have a `.env` file in the root directory with your API keys. You need at least one of the following:
    ```
    OPENAI_API_KEY="your_openai_key_here"
    # or
    GROQ_API_KEY="your_groq_key_here"
    ```

3.  **Launch the App:**
    Run the following command in your terminal:
    ```bash
    streamlit run app.py
    ```
    The application should automatically open in a new tab in your web browser.

## Features

The web interface is organized into a simple form:

-   **Software Name:** A text field where you enter the name of the software you want to generate a guide for (e.g., "Docker", "VS Code").

-   **Device Configuration (Key-Value Pairs):** A dynamic section where you can specify the target device's configuration.
    -   **Key:** The attribute of the device (e.g., `OS`, `Version`, `Architecture`).
    -   **Value:** The value for that attribute (e.g., `Ubuntu 22.04`, `1.80.0`, `x86-64`).
    -   **Add More Fields:** Click this button to add another key-value pair row.
    -   **Remove Last Field:** Click this button to remove the last key-value pair row.

-   **Select Output Format:** Radio buttons to choose the output format for your guide.
    -   **DOCX:** A Microsoft Word document.
    -   **Markdown:** A plain text file with Markdown formatting.

-   **Generate Guide:** The main button to start the guide generation process.

-   **Download Button:** After a guide is successfully generated, a download button will appear, allowing you to save the file to your computer.

## How It Works

When you click "Generate Guide," the application performs the following steps:

1.  **Sends a request** to the AI Research Agent with the software name and device configuration.
2.  The AI agent **researches the topic** and generates a detailed guide in Markdown format.
3.  The application then **directly converts** the AI's raw Markdown output into the format you selected (`.docx` or `.md`). This ensures that the final document is a faithful and complete representation of the generated content.

## Example Usage

1.  Open the web application in your browser.
2.  In the **Software Name** field, type `Docker`.
3.  In the first **Device Configuration** row, enter `OS` for the key and `Ubuntu 22.04` for the value.
4.  Click **"Add More Fields"**.
5.  In the new row, enter `Architecture` for the key and `x86-64` for the value.
6.  Select **DOCX** as the output format.
7.  Click the **"Generate Guide"** button.
8.  Wait for the process to complete. A spinner will indicate that the agent is working.
9.  Once finished, a success message will appear, along with a **"Download DOCX File"** button. Click it to save your guide.
