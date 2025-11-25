import os
import json
from typing import Dict, List, Optional

try:
    from groq import Groq
except ImportError:
    Groq = None

class EmailAgent:
    def __init__(self, api_key: str):
        """Initialize EmailAgent with Groq API"""
        if Groq is None:
            raise ImportError("Groq package not installed. Install with: pip install groq")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
    
    def categorize_email(self, email: Dict, prompt_template: str) -> str:
        """Categorize email using LLM with error handling"""
        try:
            prompt = prompt_template.format(
                from_=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=20
            )
            
            category = response.choices[0].message.content.strip()
            # Validate category
            valid_categories = ["Important", "Newsletter", "Spam", "To-Do"]
            return category if category in valid_categories else "Important"
        
        except Exception as e:
            print(f"Categorization error: {e}")
            return "Important"
    
    def extract_actions(self, email: Dict, prompt_template: str) -> List[Dict]:
        """Extract action items using LLM with robust error handling"""
        try:
            prompt = prompt_template.format(
                from_=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=250
            )
            
            content = response.choices[0].message.content.strip()
            
            # Handle markdown code blocks that Groq sometimes adds
            if content.startswith("```
                # Remove code block markers
                content = content.replace("```json", "").replace("```
            
            # Parse JSON
            actions = json.loads(content)
            
            # Validate it's a list
            if not isinstance(actions, list):
                return []
            
            # Validate each action has required fields
            valid_actions = []
            for action in actions:
                if isinstance(action, dict) and 'task' in action:
                    valid_actions.append(action)
            
            return valid_actions
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in action extraction: {e}")
            return []
        except Exception as e:
            print(f"Unexpected action extraction error: {e}")
            return []
    
    def generate_reply(self, email: Dict, prompt_template: str) -> str:
        """Generate draft reply using LLM with error handling"""
        try:
            prompt = prompt_template.format(
                from_=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=350
            )
            
            return response.choices.message.content.strip()
        
        except Exception as e:
            print(f"Reply generation error: {e}")
            return "Error generating reply. Please try again."
    
    def summarize_email(self, email: Dict, prompt_template: str) -> str:
        """Summarize email using LLM with error handling"""
        try:
            prompt = prompt_template.format(
                from_=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices.message.content.strip()
        
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Error generating summary."
    
    def chat_query(self, query: str, context: str) -> str:
        """Answer general queries about emails with error handling"""
        try:
            prompt = f"Context:\n{context}\n\nUser Question: {query}\n\nProvide a helpful answer based on the context."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=350
            )
            
            return response.choices.message.content.strip()
        
        except Exception as e:
            return f"Error processing query. Please try again."
