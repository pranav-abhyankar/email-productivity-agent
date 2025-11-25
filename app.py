import streamlit as st
import os
from database import EmailDatabase
from email_agent import EmailAgent
import json

# Page configuration
st.set_page_config(page_title="Email Productivity Agent", layout="wide")

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = EmailDatabase()

if 'agent' not in st.session_state:
    api_key = os.getenv('OPENAI_API_KEY') or st.secrets.get('OPENAI_API_KEY', '')
    if api_key:
        st.session_state.agent = EmailAgent(api_key)
    else:
        st.session_state.agent = None

if 'selected_email_id' not in st.session_state:
    st.session_state.selected_email_id = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title
st.title("📧 Email Productivity Agent")

# Sidebar - API Key and Prompt Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key_input = st.text_input("OpenAI API Key", type="password", value=os.getenv('OPENAI_API_KEY', ''))
    if api_key_input and st.session_state.agent is None:
        st.session_state.agent = EmailAgent(api_key_input)
        os.environ['OPENAI_API_KEY'] = api_key_input
    
    st.divider()
    
    # Prompt Brain Configuration
    st.header("🧠 Prompt Brain")
    
    prompt_type = st.selectbox(
        "Select Prompt to Edit",
        ["categorization", "action_extraction", "auto_reply", "summarization"]
    )
    
    current_prompt = st.session_state.db.get_prompt(prompt_type)
    
    edited_prompt = st.text_area(
        f"{prompt_type.replace('_', ' ').title()} Prompt",
        value=current_prompt,
        height=200
    )
    
    if st.button("💾 Save Prompt"):
        st.session_state.db.update_prompt(prompt_type, edited_prompt)
        st.success("Prompt saved!")
    
    st.divider()
    
    # Process all emails
    if st.button("🔄 Process All Emails", type="primary"):
        if st.session_state.agent:
            with st.spinner("Processing emails..."):
                for email in st.session_state.db.emails:
                    # Categorize
                    cat_prompt = st.session_state.db.get_prompt('categorization')
                    category = st.session_state.agent.categorize_email(email, cat_prompt)
                    
                    # Extract actions
                    action_prompt = st.session_state.db.get_prompt('action_extraction')
                    actions = st.session_state.agent.extract_actions(email, action_prompt)
                    
                    # Update email
                    st.session_state.db.update_email(email['id'], {
                        'category': category,
                        'action_items': actions
                    })
                
                st.success("All emails processed!")
                st.rerun()
        else:
            st.error("Please enter OpenAI API key first")

# Main content - Three columns
col1, col2, col3 = st.columns([2, 2, 2])

# Column 1: Email List
with col1:
    st.header("📥 Inbox")
    
    # Category filter
    categories = ["All", "Important", "To-Do", "Newsletter", "Spam", "Uncategorized"]
    filter_cat = st.selectbox("Filter by Category", categories)
    
    # Display emails
    emails_to_show = st.session_state.db.emails
    if filter_cat != "All":
        if filter_cat == "Uncategorized":
            emails_to_show = [e for e in emails_to_show if not e.get('category')]
        else:
            emails_to_show = st.session_state.db.get_emails_by_category(filter_cat)
    
    for email in sorted(emails_to_show, key=lambda x: x['timestamp'], reverse=True):
        with st.container():
            # Email preview card
            category_color = {
                "Important": "🔴",
                "To-Do": "🟡",
                "Newsletter": "🔵",
                "Spam": "⚫"
            }
            
            cat_icon = category_color.get(email.get('category', ''), "⚪")
            
            if st.button(
                f"{cat_icon} **{email['subject']}**\n\n{email['from']}\n\n{email['timestamp'][:10]}",
                key=f"email_{email['id']}",
                use_container_width=True
            ):
                st.session_state.selected_email_id = email['id']
                st.rerun()
            
            st.divider()

# Column 2: Email Details
with col2:
    st.header("📄 Email Details")
    
    if st.session_state.selected_email_id:
        email = st.session_state.db.get_email(st.session_state.selected_email_id)
        
        if email:
            st.subheader(email['subject'])
            st.text(f"From: {email['from']}")
            st.text(f"To: {email['to']}")
            st.text(f"Date: {email['timestamp']}")
            
            if email.get('category'):
                st.badge(email['category'])
            
            st.divider()
            
            st.write("**Email Body:**")
            st.text_area("Body", value=email['body'], height=200, disabled=True, label_visibility="collapsed")
            
            # Action items
            if email.get('action_items'):
                st.write("**📋 Action Items:**")
                for idx, action in enumerate(email['action_items'], 1):
                    st.write(f"{idx}. {action.get('task', 'N/A')}")
                    if action.get('deadline'):
                        st.write(f"   ⏰ Deadline: {action['deadline']}")
            
            st.divider()
            
            # Manual actions
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✍️ Generate Reply", use_container_width=True):
                    if st.session_state.agent:
                        with st.spinner("Generating reply..."):
                            reply_prompt = st.session_state.db.get_prompt('auto_reply')
                            reply_body = st.session_state.agent.generate_reply(email, reply_prompt)
                            
                            draft = {
                                "to": email['from'],
                                "subject": f"Re: {email['subject']}",
                                "body": reply_body,
                                "created_at": "2025-11-25T01:26:00"
                            }
                            
                            st.session_state.db.add_draft(email['id'], draft)
                            st.success("Draft created!")
                            st.rerun()
            
            with col_b:
                if st.button("📝 Summarize", use_container_width=True):
                    if st.session_state.agent:
                        with st.spinner("Summarizing..."):
                            summary_prompt = st.session_state.db.get_prompt('summarization')
                            summary = st.session_state.agent.summarize_email(email, summary_prompt)
                            st.info(summary)
            
            # Show draft if exists
            if email.get('draft_reply'):
                st.divider()
                st.write("**📧 Draft Reply:**")
                draft = email['draft_reply']
                st.text(f"To: {draft['to']}")
                st.text(f"Subject: {draft['subject']}")
                st.text_area("Draft Body", value=draft['body'], height=150, label_visibility="collapsed")
                st.warning("⚠️ Draft saved. Not sent automatically.")
    else:
        st.info("Select an email from the inbox to view details")

# Column 3: Email Agent Chat
with col3:
    st.header("💬 Email Agent Chat")
    
    # Chat interface
    chat_container = st.container(height=400)
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.write(f"**You:** {msg['content']}")
            else:
                st.write(f"**Agent:** {msg['content']}")
    
    # Chat input
    user_query = st.text_input("Ask the agent...", key="chat_input", placeholder="e.g., 'What tasks do I need to do?'")
    
    if st.button("Send", type="primary") and user_query:
        if st.session_state.agent:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Prepare context
            if st.session_state.selected_email_id:
                email = st.session_state.db.get_email(st.session_state.selected_email_id)
                context = f"Selected Email:\nFrom: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}\nCategory: {email.get('category', 'N/A')}"
            else:
                # All emails context
                todo_emails = st.session_state.db.get_emails_by_category('To-Do')
                context = f"Total emails: {len(st.session_state.db.emails)}\nTo-Do emails: {len(todo_emails)}"
                for email in todo_emails[:3]:
                    context += f"\n- {email['subject']} from {email['from']}"
            
            # Get agent response
            with st.spinner("Thinking..."):
                response = st.session_state.agent.chat_query(user_query, context)
            
            st.session_state.chat_history.append({"role": "agent", "content": response})
            st.rerun()
        else:
            st.error("Please configure OpenAI API key")
    
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Footer stats
st.divider()
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.metric("Total Emails", len(st.session_state.db.emails))
with col_stat2:
    todo_count = len(st.session_state.db.get_emails_by_category('To-Do'))
    st.metric("To-Do", todo_count)
with col_stat3:
    important_count = len(st.session_state.db.get_emails_by_category('Important'))
    st.metric("Important", important_count)
with col_stat4:
    spam_count = len(st.session_state.db.get_emails_by_category('Spam'))
    st.metric("Spam", spam_count)
