import os
import json
from typing import Dict, List, Optional

try:
    from groq import Groq
except ImportError:
    Groq = None

class EmailAgent:
    def __init__(self, api_key: str):
        if Groq is None:
            raise ImportError("Groq package not installed")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
    
    def categorize_email(self, email: Dict, prompt_template: str) -> str:
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
            valid_categories = ["Important", "Newsletter", "Spam", "To-Do"]
            return category if category in valid_categories else "Important"
        except Exception as e:
            print(f"Categorization error: {e}")
            return "Important"
    
    def extract_actions(self, email: Dict, prompt_template: str) -> List[Dict]:
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
            
            # Remove markdown code blocks if present
            content = content.replace('```
            content = content.replace('```', '')
            content = content.strip()
            
            actions = json.loads(content)
            if not isinstance(actions, list):
                return []
            
            valid_actions = []
            for action in actions:
                if isinstance(action, dict) and 'task' in action:
                    valid_actions.append(action)
            return valid_actions
        except json.JSONDecodeError:
            return []
        except Exception:
            return []
    
    def generate_reply(self, email: Dict, prompt_template: str) -> str:
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
            return response.choices[0].message.content.strip()
        except Exception:
            return "Error generating reply. Please try again."
    
    def summarize_email(self, email: Dict, prompt_template: str) -> str:
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
            return response.choices[0].message.content.strip()
        except Exception:
            return "Error generating summary."
    
    def chat_query(self, query: str, context: str) -> str:
        try:
            prompt = f"Context:\n{context}\n\nUser Question: {query}\n\nProvide a helpful answer based on the context."
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=350
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Error processing query. Please try again."
