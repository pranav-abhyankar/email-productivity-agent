import json
from typing import List, Dict, Optional
from datetime import datetime

class EmailDatabase:
    def __init__(self, inbox_file: str = "mock_inbox.json", prompts_file: str = "prompts.json"):
        self.inbox_file = inbox_file
        self.prompts_file = prompts_file
        self.emails = self.load_emails()
        self.prompts = self.load_prompts()
    
    def load_emails(self) -> List[Dict]:
        """Load emails from JSON file"""
        try:
            with open(self.inbox_file, 'r') as f:
                data = json.load(f)
                return data.get('emails', [])
        except FileNotFoundError:
            return []
    
    def save_emails(self):
        """Save emails to JSON file"""
        with open(self.inbox_file, 'w') as f:
            json.dump({'emails': self.emails}, f, indent=2)
    
    def load_prompts(self) -> Dict:
        """Load prompt templates"""
        try:
            with open(self.prompts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_prompts(self):
        """Save prompt templates"""
        with open(self.prompts_file, 'w') as f:
            json.dump(self.prompts, f, indent=2)
    
    def get_email(self, email_id: int) -> Optional[Dict]:
        """Get email by ID"""
        for email in self.emails:
            if email['id'] == email_id:
                return email
        return None
    
    def update_email(self, email_id: int, updates: Dict):
        """Update email fields"""
        for email in self.emails:
            if email['id'] == email_id:
                email.update(updates)
                break
        self.save_emails()
    
    def get_prompt(self, prompt_type: str) -> str:
        """Get prompt template by type"""
        return self.prompts.get(prompt_type, {}).get('template', '')
    
    def update_prompt(self, prompt_type: str, template: str):
        """Update prompt template"""
        if prompt_type in self.prompts:
            self.prompts[prompt_type]['template'] = template
            self.save_prompts()
    
    def get_emails_by_category(self, category: str) -> List[Dict]:
        """Filter emails by category"""
        return [e for e in self.emails if e.get('category') == category]
    
    def add_draft(self, email_id: int, draft: Dict):
        """Add draft reply to email"""
        self.update_email(email_id, {'draft_reply': draft})
