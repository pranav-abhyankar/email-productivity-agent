import os
import json
from openai import OpenAI
from typing import Dict, List, Optional

class EmailAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    def categorize_email(self, email: Dict, prompt_template: str) -> str:
        """Categorize email using LLM"""
        try:
            prompt = prompt_template.format(
                from_=email['from'],
                subject=email['subject'],
                body=email['body']
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=10
            )
            
            category = response.choices[0].message.content.strip()
            # Validate category
            valid_categories = ["Important", "Newsletter", "Spam", "To-Do"]
            return category if category in valid_categories else "Important"
        
        except Exception as e:
            print(f"Categorization error: {e}")
            return "Important"
    
    def extract_actions(self, email: Dict, prompt_template: str) -> List[Dict]:
        """Extract action items using LLM"""
        try:
            prompt = prompt_template.format(
                from_=email['from'],
                subject=email['subject'],
                body=email['body']
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            actions = json.loads(content)
            return actions if isinstance(actions, list) else []
        
        except Exception as e:
            print(f"Action extraction error: {e}")
            return []
    
    def generate_reply(self, email: Dict, prompt_template: str) -> str:
        """Generate draft reply using LLM"""
        try:
            prompt = prompt_template.format(
                from_=email['from'],
                subject=email['subject'],
                body=email['body']
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Reply generation error: {e}")
            return "Error generating reply. Please try again."
    
    def summarize_email(self, email: Dict, prompt_template: str) -> str:
        """Summarize email using LLM"""
        try:
            prompt = prompt_template.format(
                from_=email['from'],
                subject=email['subject'],
                body=email['body']
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Error generating summary."
    
    def chat_query(self, query: str, context: str) -> str:
        """Answer general queries about emails"""
        try:
            prompt = f"Context:\n{context}\n\nUser Question: {query}\n\nProvide a helpful answer based on the context."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Error processing query: {e}"
