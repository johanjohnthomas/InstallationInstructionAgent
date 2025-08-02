import os
from smolagents import ToolCallingAgent, WebSearchTool, LiteLLMModel

class ResearchAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        if self.openai_api_key:
            self.model_name = "gpt-4o-mini"
            self.api_key_for_litellm = self.openai_api_key
        elif self.groq_api_key:
            self.model_name = "groq/llama3-8b-8192" # Use LiteLLM prefix for Groq
            self.api_key_for_litellm = self.groq_api_key
        else:
            raise ValueError("No API key found for OpenAI or Groq.")

        # Initialize LiteLLMModel with the appropriate API key and model name
        self.model = LiteLLMModel(model_id=self.model_name, api_key=self.api_key_for_litellm)

        self.agent = ToolCallingAgent(
            model=self.model,
            tools=[WebSearchTool()]
        )

    def _get_master_prompt(self) -> str:
        """
        Returns the master prompt that guides the agent's research and output structure.

        Returns:
            str: The master prompt string.
        """
        return """You are a research agent. Your goal is to provide information based on web searches.
Your output should be structured into four sections: What is [Software Name]?, Installation Guide, Pros & Cons, and Next Steps.
Use the web search tool to gather accurate and up-to-date information.
"""


    def generate_guide(self, software_name: str, device_config: str) -> str:
        master_prompt = self._get_master_prompt()
        query = f"Research guide for {software_name} installation on {device_config}"
        full_prompt = f"{master_prompt}\n\n{query}"
        print(f"Agent researching: {query}")
        response = self.agent.run(full_prompt)
        return response

if __name__ == "__main__":
    # This is for testing the agent directly
    # Ensure OPENAI_API_KEY or GROQ_API_KEY is set in your .env file
    agent = ResearchAgent()
    guide = agent.generate_guide("Docker", "Ubuntu 22.04")
    print(guide)
