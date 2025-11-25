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
                from_sender=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=50
            )
            category = response.choices[0].message.content.strip()
            valid_categories = ["Important", "Newsletter", "Spam", "To-Do"]
            for cat in valid_categories:
                if cat.lower() in category.lower():
                    return cat
            return "Important"
        except Exception as e:
            print(f"Categorization error: {e}")
            return "Important"
    
    def extract_actions(self, email: Dict, prompt_template: str) -> List[Dict]:
        try:
            prompt = prompt_template.format(
                from_sender=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300
            )
            content = response.choices[0].message.content.strip()
            
            start_idx = content.find('[')
            end_idx = content.rfind(']')
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx:end_idx+1]
            
            actions = json.loads(content)
            if not isinstance(actions, list):
                return []
            
            valid_actions = []
            for action in actions:
                if isinstance(action, dict) and 'task' in action:
                    valid_actions.append(action)
            return valid_actions
        except Exception as e:
            print(f"Action extraction error: {e}")
            return []
    
    def generate_reply(self, email: Dict, prompt_template: str) -> str:
        try:
            prompt = prompt_template.format(
                from_sender=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
                top_p=1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Reply generation error: {type(e).__name__} - {str(e)}"
    
    def summarize_email(self, email: Dict, prompt_template: str) -> str:
        try:
            prompt = prompt_template.format(
                from_sender=email.get('from', 'Unknown'),
                subject=email.get('subject', 'No Subject'),
                body=email.get('body', '')
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300,
                top_p=1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Summarization error: {type(e).__name__} - {str(e)}"
    
    def chat_query(self, query: str, context: str) -> str:
        try:
            prompt = f"Context:\n{context}\n\nUser Question: {query}\n\nProvide a helpful answer based on the context."
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Chat error: {type(e).__name__} - {str(e)}"
