import os
import click
from dotenv import load_dotenv
from research_agent import ResearchAgent
from docx_generator import generate_document_from_markdown

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@click.group()
def cli():
    """A CLI tool for generating software installation guides."""
    pass

@cli.command()
@click.option('--software', required=True, help='The name of the software to generate a guide for.')
@click.option('--param', 'params', multiple=True, type=(str, str), help='Device configuration parameter (e.g., --param OS "Ubuntu 22.04"). Can be used multiple times.')
@click.option('--format', 'output_format', type=click.Choice(['docx', 'md']), default='docx', help='Output format: docx or md (Markdown).')
@click.option('--output', 'output_filename', default='generated_guide', help='Base name for the output file (e.g., "my_guide"). Extension will be added automatically.')
def generate_guide(software, params, output_format, output_filename):
    """
    Generates a tailored installation guide for a specific software and device configuration.

    This command initializes the ResearchAgent, passes the user's query, and generates
    a document in the specified format (DOCX or Markdown).

    Example Usage:
    
    python main.py generate-guide --software "Docker" --param OS "Ubuntu 22.04" --format docx
    """
    # Convert params to a readable string for the agent
    device_config_str = ", ".join([f"{key}: {value}" for key, value in params])
    if not device_config_str:
        device_config_str = "Default configuration"
        
    print("Environment variables loaded.")
    print(f"OPENAI_API_KEY: {'Loaded' if OPENAI_API_KEY else 'Not Loaded'}")
    print(f"GROQ_API_KEY: {'Loaded' if GROQ_API_KEY else 'Not Loaded'}")

    try:
        agent = ResearchAgent()
        print(f"\nTesting ResearchAgent with {software} on {device_config_str}...")
        guide_content = agent.generate_guide(software, device_config_str)
        print("\n--- Generated Guide (Partial) ---")
        print(guide_content[:500]) # Print first 500 characters for brevity
        print("\n--- End of Partial Guide ---")

        # Remove "Final answer: " prefix if present
        if guide_content.startswith("Final answer: "):
            guide_content = guide_content[len("Final answer: "):].strip()

        title = f"{software} Installation Guide for {device_config_str}"
        
        # Generate document based on selected format
        generate_document_from_markdown(title, guide_content, output_filename, output_format)
        print(f"\nGenerated {output_format.upper()} file: {output_filename}.{output_format}")

    except ValueError as e:
        print(f"Error initializing ResearchAgent: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during agent execution: {e}")




if __name__ == "__main__":
    cli()