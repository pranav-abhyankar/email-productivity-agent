import json
from typing import List, Dict, Optional
from datetime import datetime
import os

class EmailDatabase:
    def __init__(self, inbox_file: str = "mock_inbox.json", prompts_file: str = "prompts.json"):
        self.inbox_file = inbox_file
        self.prompts_file = prompts_file
        self.emails = self.load_emails()
        self.prompts = self.load_prompts()
    
    def load_emails(self) -> List[Dict]:
        try:
            if not os.path.exists(self.inbox_file):
                return []
            
            with open(self.inbox_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                emails = data.get('emails', [])
                
                for email in emails:
                    if 'category' not in email:
                        email['category'] = None
                    if 'action_items' not in email:
                        email['action_items'] = []
                    if 'draft_reply' not in email:
                        email['draft_reply'] = None
                
                return emails
        except Exception as e:
            print(f"Error loading emails: {e}")
            return []
    
    def save_emails(self):
        try:
            with open(self.inbox_file, 'w', encoding='utf-8') as f:
                json.dump({'emails': self.emails}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving emails: {e}")
    
    def load_prompts(self) -> Dict:
        try:
            if not os.path.exists(self.prompts_file):
                return self._get_default_prompts()
            
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict:
        return {
            "categorization": {
                "name": "Email Categorization",
                "template": "Categorize as Important, Newsletter, Spam, or To-Do.\nFrom: {from_sender}\nSubject: {subject}\nBody: {body}\nOne word only:"
            },
            "action_extraction": {
                "name": "Action Item Extraction",
                "template": "Extract tasks.\nFrom: {from_sender}\nBody: {body}\nJSON array or []:"
            },
            "auto_reply": {
                "name": "Auto-Reply Draft",
                "template": "Write professional reply.\nFrom: {from_sender}\nSubject: {subject}\nBody: {body}\nReply:"
            },
            "summarization": {
                "name": "Email Summarization",
                "template": "Summarize in 2 sentences.\nFrom: {from_sender}\nSubject: {subject}\nBody: {body}\nSummary:"
            }
        }
    
    def save_prompts(self):
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving prompts: {e}")
    
    def get_email(self, email_id: int) -> Optional[Dict]:
        for email in self.emails:
            if email.get('id') == email_id:
                return email
        return None
    
    def update_email(self, email_id: int, updates: Dict):
        for email in self.emails:
            if email.get('id') == email_id:
                email.update(updates)
                break
        self.save_emails()
    
    def get_prompt(self, prompt_type: str) -> str:
        return self.prompts.get(prompt_type, {}).get('template', '')
    
    def update_prompt(self, prompt_type: str, template: str):
        if prompt_type in self.prompts:
            self.prompts[prompt_type]['template'] = template
            self.save_prompts()
    
    def get_emails_by_category(self, category: str) -> List[Dict]:
        return [e for e in self.emails if e.get('category') == category]
    
    def add_draft(self, email_id: int, draft: Dict):
        self.update_email(email_id, {'draft_reply': draft})
