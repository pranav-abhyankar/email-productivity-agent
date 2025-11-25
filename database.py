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
        
        # DEBUG: Print loaded prompts
        print(f"Loaded {len(self.prompts)} prompt types")
        for key in self.prompts.keys():
            template = self.prompts[key].get('template', '')
            print(f"  {key}: {len(template)} chars")
    
    def load_emails(self) -> List[Dict]:
        """Load emails from JSON file with error handling"""
        try:
            if not os.path.exists(self.inbox_file):
                print(f"Warning: {self.inbox_file} not found. Creating empty inbox.")
                return []
            
            with open(self.inbox_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                emails = data.get('emails', [])
                
                # Validate email structure
                for email in emails:
                    if 'category' not in email:
                        email['category'] = None
                    if 'action_items' not in email:
                        email['action_items'] = []
                    if 'draft_reply' not in email:
                        email['draft_reply'] = None
                
                print(f"Loaded {len(emails)} emails from {self.inbox_file}")
                return emails
        
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.inbox_file}: {e}")
            return []
        except Exception as e:
            print(f"Error loading emails: {e}")
            return []
    
    def save_emails(self):
        """Save emails to JSON file with error handling"""
        try:
            with open(self.inbox_file, 'w', encoding='utf-8') as f:
                json.dump({'emails': self.emails}, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.emails)} emails")
        except Exception as e:
            print(f"Error saving emails: {e}")
    
    def load_prompts(self) -> Dict:
        """Load prompt templates with error handling"""
        try:
            if not os.path.exists(self.prompts_file):
                print(f"Warning: {self.prompts_file} not found. Using default prompts.")
                return self._get_default_prompts()
            
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
                print(f"Loaded prompts from {self.prompts_file}")
                return prompts
        
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.prompts_file}: {e}. Using defaults.")
            return self._get_default_prompts()
        except Exception as e:
            print(f"Error loading prompts: {e}. Using defaults.")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict:
        """Return default prompts if file doesn't exist"""
        return {
            "categorization": {
                "name": "Email Categorization",
                "template": "Categorize this email as Important, Newsletter, Spam, or To-Do.\n\nFrom: {from_}\nSubject: {subject}\nBody: {body}\n\nRespond with only one word: the category name."
            },
            "action_extraction": {
                "name": "Action Item Extraction",
                "template": "Extract tasks from this email. Return empty array [] if none.\n\nFrom: {from_}\nSubject: {subject}\nBody: {body}\n\nReturn JSON array only."
            },
            "auto_reply": {
                "name": "Auto-Reply Draft",
                "template": "Write a professional reply to this email.\n\nFrom: {from_}\nSubject: {subject}\nBody: {body}\n\nWrite only the reply body."
            },
            "summarization": {
                "name": "Email Summarization",
                "template": "Summarize this email in 2-3 sentences.\n\nFrom: {from_}\nSubject: {subject}\nBody: {body}\n\nProvide only the summary."
            }
        }
    
    def save_prompts(self):
        """Save prompt templates with error handling"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.prompts)} prompts")
        except Exception as e:
            print(f"Error saving prompts: {e}")
    
    def get_email(self, email_id: int) -> Optional[Dict]:
        """Get email by ID"""
        for email in self.emails:
            if email.get('id') == email_id:
                return email
        return None
    
    def update_email(self, email_id: int, updates: Dict):
        """Update email fields"""
        for email in self.emails:
            if email.get('id') == email_id:
                email.update(updates)
                break
        self.save_emails()
    
    def get_prompt(self, prompt_type: str) -> str:
        """Get prompt template by type"""
        prompt_data = self.prompts.get(prompt_type, {})
        template = prompt_data.get('template', '')
        
        # DEBUG
        print(f"Getting prompt '{prompt_type}': {len(template)} chars")
        if not template:
            print(f"WARNING: Empty template for {prompt_type}")
            print(f"Available prompts: {list(self.prompts.keys())}")
        
        return template
    
    def update_prompt(self, prompt_type: str, template: str):
        """Update prompt template"""
        if prompt_type in self.prompts:
            self.prompts[prompt_type]['template'] = template
            self.save_prompts()
            print(f"Updated prompt '{prompt_type}' to {len(template)} chars")
        else:
            print(f"ERROR: Prompt type '{prompt_type}' not found")
    
    def get_emails_by_category(self, category: str) -> List[Dict]:
        """Filter emails by category"""
        return [e for e in self.emails if e.get('category') == category]
    
    def add_draft(self, email_id: int, draft: Dict):
        """Add draft reply to email"""
        self.update_email(email_id, {'draft_reply': draft})
