import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from smolagents import ToolCallingAgent, LiteLLMModel
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class SheetsAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

        if self.google_api_key:
            self.model_name = "gemini/gemini-2.5-pro"  # Use LiteLLM prefix for Gemini
            self.api_key_for_litellm = self.google_api_key
        elif self.openai_api_key:
            self.model_name = "gpt-4o-mini"
            self.api_key_for_litellm = self.openai_api_key
        elif self.groq_api_key:
            self.model_name = "groq/llama3-8b-8192"
            self.api_key_for_litellm = self.groq_api_key
        else:
            raise ValueError("No API key found for Google, OpenAI, or Groq.")

        # Initialize LiteLLMModel with the appropriate API key and model name
        self.model = LiteLLMModel(model_id=self.model_name, api_key=self.api_key_for_litellm)

        self.agent = ToolCallingAgent(
            model=self.model,
            tools=[]  # No tools needed for this agent
        )
        
    def parse_daily_updates(self, updates_text: str, existing_sheet_data: List[Dict]) -> List[Dict]:
        """
        Parse daily updates and determine what changes need to be made to the sheet.
        
        Args:
            updates_text: The daily updates text from user
            existing_sheet_data: Current sheet data as list of dictionaries
            
        Returns:
            List of changes to make (updates and new entries)
        """
        
        # Create context for the AI about existing sheet structure
        sheet_context = self._create_sheet_context(existing_sheet_data)
        
        prompt = f"""You are an intelligent agent that processes daily work updates and translates them into structured Google Sheets data for an internship journey tracking system.

EXISTING SHEET DATA CONTEXT:
{sheet_context}

DAILY UPDATES TO PROCESS:
{updates_text}

YOUR TASK:
1. Analyze the daily updates and identify individual tasks/activities
2. For each identified task, determine if it should:
   - UPDATE an existing row in the sheet (if the task continues/completes an existing workstream)
   - CREATE a new row (if it's genuinely new work)
3. Infer the correct status based on verb tense and context:
   - Past tense ("completed", "finished", "did") → "Complete" 
   - Present continuous ("working on", "currently", "am doing") → "In Progress"
   - Future tense ("will", "going to", "plan to") → "Upcoming"
   - Conditional/blocked language → "On Hold"
4. Estimate effort in man-days (assume 8 hours = 1 day, estimate based on task complexity and time mentioned)
5. Try to fit tasks into existing workstreams and use existing tags when possible
6. Maintain timeline coherence - tasks should flow logically

RESPONSE FORMAT (JSON):
{{
  "changes": [
    {{
      "action": "update|create",
      "row_id": "existing_row_number_if_updating",
      "data": {{
        "Workstream": "string",
        "Task": "string", 
        "Sub Task": "string",
        "Start Date": "MM/DD/YYYY",
        "End Date": "MM/DD/YYYY",
        "Effort": "number",
        "Status": "Complete|In Progress|Upcoming|On Hold|Deferred",
        "Priority": "High|Medium|Low",
        "Tags": "comma,separated,tags"
      }},
      "reasoning": "Why this action was chosen and how the data was inferred"
    }}
  ]
}}

Be conservative - prefer updating existing rows over creating new ones when the work is clearly related. Respond ONLY with valid JSON."""

        try:
            response = self.agent.run(prompt)
            response_text = str(response).strip()
            
            # Clean up the response to extract JSON
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()
            
            changes_data = json.loads(response_text)
            return changes_data.get("changes", [])
            
        except Exception as e:
            raise Exception(f"Error parsing daily updates: {str(e)}")
    
    def _create_sheet_context(self, existing_data: List[Dict]) -> str:
        """Create a readable context summary of existing sheet data"""
        if not existing_data:
            return "No existing data in sheet."
        
        context = "CURRENT SHEET ROWS:\n"
        for i, row in enumerate(existing_data, 1):
            context += f"Row {i}: {row.get('Workstream', '')} | {row.get('Task', '')} | {row.get('Status', '')} | {row.get('Tags', '')}\n"
        
        # Add summary of workstreams and common tags
        workstreams = list(set([row.get('Workstream', '') for row in existing_data if row.get('Workstream')]))
        all_tags = []
        for row in existing_data:
            if row.get('Tags'):
                all_tags.extend([tag.strip() for tag in row.get('Tags', '').split(',')])
        common_tags = list(set(all_tags))
        
        context += f"\nEXISTING WORKSTREAMS: {', '.join(workstreams)}\n"
        context += f"EXISTING TAGS: {', '.join(common_tags)}\n"
        
        return context
    
    def infer_dates(self, task_description: str, status: str) -> Tuple[str, str]:
        """
        Infer start and end dates based on task description and status
        """
        today = datetime.now()
        
        if status == "Complete":
            # For completed tasks, assume they ended today or recently
            end_date = today
            # Estimate start date based on task complexity (simple heuristic)
            if any(word in task_description.lower() for word in ['research', 'analysis', 'study']):
                start_date = today - timedelta(days=3)  # Research tasks ~3 days
            elif any(word in task_description.lower() for word in ['implement', 'build', 'create', 'develop']):
                start_date = today - timedelta(days=5)  # Implementation ~5 days  
            else:
                start_date = today - timedelta(days=1)  # Default ~1 day
                
        elif status == "In Progress":
            # Started recently, will finish soon
            start_date = today - timedelta(days=1)
            end_date = today + timedelta(days=2)
            
        elif status == "Upcoming":
            # Will start soon
            start_date = today + timedelta(days=1)
            end_date = today + timedelta(days=5)
            
        else:  # On Hold, Deferred, etc.
            start_date = today
            end_date = today + timedelta(days=7)
        
        return start_date.strftime("%m/%d/%Y"), end_date.strftime("%m/%d/%Y")
    
    def estimate_effort(self, task_description: str, updates_context: str) -> float:
        """
        Estimate effort in man-days based on task description and context
        """
        # Simple heuristics for effort estimation
        base_effort = 0.5  # Default half day
        
        # Complexity indicators
        if any(word in task_description.lower() for word in ['complex', 'advanced', 'comprehensive']):
            base_effort *= 2
        
        # Task type adjustments
        if any(word in task_description.lower() for word in ['research', 'analysis']):
            base_effort *= 1.5
        elif any(word in task_description.lower() for word in ['implement', 'build', 'develop']):
            base_effort *= 2
        elif any(word in task_description.lower() for word in ['review', 'check', 'read']):
            base_effort *= 0.5
        
        # Context clues from updates
        if 'all day' in updates_context.lower():
            base_effort = 1.0
        elif 'few hours' in updates_context.lower():
            base_effort = 0.25
        elif 'morning' in updates_context.lower() or 'afternoon' in updates_context.lower():
            base_effort = 0.5
        
        return min(base_effort, 1.0)  # Cap at 1 day per task
    
    def validate_changes(self, changes: List[Dict], existing_data: List[Dict]) -> List[Dict]:
        """
        Validate and clean up the proposed changes
        """
        validated_changes = []
        
        for change in changes:
            # Validate required fields
            if not change.get('data', {}).get('Task'):
                continue  # Skip if no task description
                
            # Auto-fill missing dates if not provided
            task_desc = change['data'].get('Task', '')
            status = change['data'].get('Status', 'Upcoming')
            
            if not change['data'].get('Start Date') or not change['data'].get('End Date'):
                start_date, end_date = self.infer_dates(task_desc, status)
                change['data']['Start Date'] = start_date
                change['data']['End Date'] = end_date
            
            # Auto-estimate effort if not provided
            if not change['data'].get('Effort'):
                change['data']['Effort'] = self.estimate_effort(task_desc, task_desc)
            
            # Set default priority if not provided
            if not change['data'].get('Priority'):
                change['data']['Priority'] = 'Medium'
                
            validated_changes.append(change)
        
        return validated_changes
    
    def preview_changes(self, changes: List[Dict], existing_data: List[Dict]) -> str:
        """
        Generate a human-readable preview of what changes will be made
        """
        if not changes:
            return "No changes to make."
        
        preview = "PREVIEW OF CHANGES TO GOOGLE SHEETS:\n\n"
        
        for i, change in enumerate(changes, 1):
            action = change.get('action', 'unknown')
            data = change.get('data', {})
            reasoning = change.get('reasoning', 'No reasoning provided')
            
            preview += f"{i}. ACTION: {action.upper()}\n"
            
            if action == 'update' and change.get('row_id'):
                preview += f"   Updating Row {change['row_id']}\n"
            else:
                preview += f"   Creating New Row\n"
            
            preview += f"   Workstream: {data.get('Workstream', 'N/A')}\n"
            preview += f"   Task: {data.get('Task', 'N/A')}\n"
            preview += f"   Sub Task: {data.get('Sub Task', 'N/A')}\n"
            preview += f"   Status: {data.get('Status', 'N/A')}\n"
            preview += f"   Effort: {data.get('Effort', 'N/A')} days\n"
            preview += f"   Priority: {data.get('Priority', 'N/A')}\n"
            preview += f"   Tags: {data.get('Tags', 'N/A')}\n"
            preview += f"   Reasoning: {reasoning}\n\n"
        
        return preview