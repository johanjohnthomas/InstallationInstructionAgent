# Command-Line Interface (CLI) Guide

## Overview

This guide explains how to use the command-line interface (CLI) for the Research Agent. The CLI is ideal for power users, automation scripts, and integrating the guide generation into larger workflows.

## Setup

Before using the CLI, ensure you have all the necessary dependencies installed and your environment variables are set up correctly.

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

## Usage

The CLI is built using `click` and is invoked through the `main.py` script. The main command is `generate-guide`.

### `generate-guide` Command

This command generates a software installation guide based on the options you provide.

**Syntax:**
```bash
python main.py generate-guide [OPTIONS]
```

**Options:**

| Option | Argument | Description | Required |
| :--- | :--- | :--- | :--- |
| `--software` | TEXT | The name of the software to generate a guide for. | Yes |
| `--param` | KEY VALUE | A device configuration parameter. This option can be used multiple times for different key-value pairs. | No |
| `--format` | `docx` or `md` | The output format for the generated guide. Defaults to `docx`. | No |
| `--output` | TEXT | The base name for the output file. The file extension is added automatically. Defaults to `generated_guide`. | No |
| `--help` | | Shows the help message and exits. | |

## How It Works

When you run the `generate-guide` command, the script performs the following steps:

1.  **Sends a request** to the AI Research Agent with the software name and device parameters.
2.  The AI agent **researches the topic** and generates a detailed guide in Markdown format.
3.  The script then **directly converts** the AI's raw Markdown output into the format you selected (`.docx` or `.md`). This ensures that the final document is a faithful and complete representation of the generated content.

## Examples

### Basic Example

Generate a guide for Docker on a default device configuration in DOCX format.

```bash
python main.py generate-guide --software "Docker"
```
This will create a file named `generated_guide.docx` in your current directory.

### Specifying Device and Format

Generate a guide for Visual Studio Code on Ubuntu 22.04 in Markdown format.

```bash
python main.py generate-guide --software "Visual Studio Code" --param OS "Ubuntu 22.04" --format md
```
This will create a file named `generated_guide.md`.

### Multiple Parameters and Custom Output Name

Generate a guide for Python on Windows 11 (64-bit) and save it with a custom name.

```bash
python main.py generate-guide --software "Python" --param OS "Windows 11" --param Architecture "x86-64" --output "python_install_guide"
```
This will create a file named `python_install_guide.docx`.
