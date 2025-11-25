import streamlit as st
import os
from database import EmailDatabase
from email_agent import EmailAgent
import json
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db' not in st.session_state:
    try:
        st.session_state.db = EmailDatabase()
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        st.stop()

if 'agent' not in st.session_state:
    # Try to get Groq API key from multiple sources
    api_key = None
    
    # 1. Environment variable
    if os.getenv('GROQ_API_KEY'):
        api_key = os.getenv('GROQ_API_KEY')
    else:
        # 2. Streamlit secrets (only if file exists)
        try:
            if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                api_key = st.secrets['GROQ_API_KEY']
        except (FileNotFoundError, KeyError, AttributeError):
            pass
    
    # Initialize agent if we have a key
    if api_key:
        try:
            st.session_state.agent = EmailAgent(api_key)
        except Exception as e:
            st.error(f"Error initializing AI agent: {e}")
            st.session_state.agent = None
    else:
        st.session_state.agent = None

if 'selected_email_id' not in st.session_state:
    st.session_state.selected_email_id = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

# Title
st.title("📧 Email Productivity Agent")
st.caption("Powered by Groq AI - LLaMA 3.1")

# Sidebar - API Key and Prompt Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    if st.session_state.agent is None:
        st.warning("⚠️ Groq API key not configured")
        api_key_input = st.text_input(
            "Enter Groq API Key",
            type="password",
            value=os.getenv('GROQ_API_KEY', ''),
            help="Get your free API key from console.groq.com"
        )
        if api_key_input:
            try:
                st.session_state.agent = EmailAgent(api_key_input)
                os.environ['GROQ_API_KEY'] = api_key_input
                st.success("✅ API key configured!")
                st.rerun()
            except Exception as e:
                st.error(f"Error setting up agent: {e}")
    else:
        st.success("✅ API Key Configured")
    
    st.divider()
    
    # Prompt Brain Configuration
    st.header("🧠 Prompt Brain")
    
    prompt_type = st.selectbox(
        "Select Prompt to Edit",
        ["categorization", "action_extraction", "auto_reply", "summarization"],
        help="Choose which prompt template to customize"
    )
    
    current_prompt = st.session_state.db.get_prompt(prompt_type)
    
    edited_prompt = st.text_area(
        f"{prompt_type.replace('_', ' ').title()} Prompt",
        value=current_prompt,
        height=200,
        help="Use {from_}, {subject}, {body} as placeholders"
    )
    
    col_save, col_reset = st.columns(2)
    
    with col_save:
        if st.button("💾 Save", use_container_width=True):
            try:
                st.session_state.db.update_prompt(prompt_type, edited_prompt)
                st.success("Saved!")
            except Exception as e:
                st.error(f"Error saving: {e}")
    
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Process all emails
    if st.button("🔄 Process All Emails", type="primary", use_container_width=True, disabled=st.session_state.processing):
        if st.session_state.agent:
            st.session_state.processing = True
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                total_emails = len(st.session_state.db.emails)
                
                for idx, email in enumerate(st.session_state.db.emails):
                    status_text.text(f"Processing {idx + 1}/{total_emails}: {email.get('subject', 'No Subject')[:30]}...")
                    
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
                    
                    progress_bar.progress((idx + 1) / total_emails)
                
                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ Processed {total_emails} emails successfully!")
                st.session_state.processing = False
                st.rerun()
            
            except Exception as e:
                st.error(f"Error during processing: {e}")
                st.session_state.processing = False
        else:
            st.error("Please configure Groq API key first")

# Main content - Three columns
col1, col2, col3 = st.columns(3)


# Column 1: Email List
with col1:
    st.header("📥 Inbox")
    
    # Category filter
    categories = ["All", "Important", "To-Do", "Newsletter", "Spam", "Uncategorized"]
    filter_cat = st.selectbox("Filter by Category", categories, label_visibility="collapsed")
    
    # Display emails
    emails_to_show = st.session_state.db.emails
    
    if filter_cat != "All":
        if filter_cat == "Uncategorized":
            emails_to_show = [e for e in emails_to_show if not e.get('category')]
        else:
            emails_to_show = st.session_state.db.get_emails_by_category(filter_cat)
    
    if not emails_to_show:
        st.info(f"No emails in '{filter_cat}' category")
    
    for email in sorted(emails_to_show, key=lambda x: x.get('timestamp', ''), reverse=True):
        with st.container():
            # Email preview card
            category_color = {
                "Important": "🔴",
                "To-Do": "🟡",
                "Newsletter": "🔵",
                "Spam": "⚫"
            }
            
            cat_icon = category_color.get(email.get('category', ''), "⚪")
            
            button_label = f"{cat_icon} **{email.get('subject', 'No Subject')[:40]}**\n\n{email.get('from', 'Unknown')}\n\n{email.get('timestamp', '')[:10]}"
            
            if st.button(
                button_label,
                key=f"email_{email.get('id')}",
                use_container_width=True
            ):
                st.session_state.selected_email_id = email.get('id')
                st.rerun()
            
            st.divider()

# Column 2: Email Details
with col2:
    st.header("📄 Email Details")
    
    if st.session_state.selected_email_id:
        email = st.session_state.db.get_email(st.session_state.selected_email_id)
        
        if email:
            st.subheader(email.get('subject', 'No Subject'))
            st.text(f"From: {email.get('from', 'Unknown')}")
            st.text(f"To: {email.get('to', 'Unknown')}")
            st.text(f"Date: {email.get('timestamp', 'Unknown')}")
            
            if email.get('category'):
                st.markdown(f"**Category:** {email['category']}")
            
            st.divider()
            
            st.write("**Email Body:**")
            st.text_area("Body", value=email.get('body', ''), height=200, disabled=True, label_visibility="collapsed")
            
            # Action items
            if email.get('action_items') and len(email['action_items']) > 0:
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
                            try:
                                reply_prompt = st.session_state.db.get_prompt('auto_reply')
                                reply_body = st.session_state.agent.generate_reply(email, reply_prompt)
                                
                                draft = {
                                    "to": email.get('from', 'Unknown'),
                                    "subject": f"Re: {email.get('subject', 'No Subject')}",
                                    "body": reply_body,
                                    "created_at": "2025-11-25T13:55:00"
                                }
                                
                                st.session_state.db.add_draft(email['id'], draft)
                                st.success("Draft created!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error generating reply: {e}")
                    else:
                        st.error("Configure API key first")
            
            with col_b:
                if st.button("📝 Summarize", use_container_width=True):
                    if st.session_state.agent:
                        with st.spinner("Summarizing..."):
                            try:
                                summary_prompt = st.session_state.db.get_prompt('summarization')
                                summary = st.session_state.agent.summarize_email(email, summary_prompt)
                                st.info(summary)
                            except Exception as e:
                                st.error(f"Error summarizing: {e}")
                    else:
                        st.error("Configure API key first")
            
            # Show draft if exists
            if email.get('draft_reply'):
                st.divider()
                st.write("**📧 Draft Reply:**")
                draft = email['draft_reply']
                st.text(f"To: {draft.get('to', 'Unknown')}")
                st.text(f"Subject: {draft.get('subject', 'No Subject')}")
                st.text_area("Draft Body", value=draft.get('body', ''), height=150, label_visibility="collapsed", disabled=True)
                st.warning("⚠️ Draft saved. Not sent automatically.")
    else:
        st.info("👈 Select an email from the inbox to view details")

# Column 3: Email Agent Chat
with col3:
    st.header("💬 Email Agent Chat")
    
    # Chat interface
    chat_container = st.container(height=400)
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("💡 Ask me anything about your emails!")
        
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.write(f"**You:** {msg['content']}")
            else:
                st.write(f"**🤖 Agent:** {msg['content']}")
    
    # Chat input
    user_query = st.text_input(
        "Ask the agent...",
        key="chat_input",
        placeholder="e.g., 'What tasks do I need to do?'",
        label_visibility="collapsed"
    )
    
    col_send, col_clear = st.columns(2)
    
    with col_send:
        if st.button("Send", type="primary", use_container_width=True) and user_query:
            if st.session_state.agent:
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                
                # Prepare context
                try:
                    if st.session_state.selected_email_id:
                        email = st.session_state.db.get_email(st.session_state.selected_email_id)
                        context = f"Selected Email:\nFrom: {email.get('from', 'Unknown')}\nSubject: {email.get('subject', 'No Subject')}\nBody: {email.get('body', '')}\nCategory: {email.get('category', 'N/A')}"
                    else:
                        # All emails context
                        todo_emails = st.session_state.db.get_emails_by_category('To-Do')
                        context = f"Total emails: {len(st.session_state.db.emails)}\nTo-Do emails: {len(todo_emails)}"
                        for email in todo_emails[:3]:
                            context += f"\n- {email.get('subject', 'No Subject')} from {email.get('from', 'Unknown')}"
                    
                    # Get agent response
                    with st.spinner("Thinking..."):
                        response = st.session_state.agent.chat_query(user_query, context)
                    
                    st.session_state.chat_history.append({"role": "agent", "content": response})
                    st.rerun()
                
                except Exception as e:
                    st.session_state.chat_history.append({"role": "agent", "content": f"Error: {str(e)}"})
                    st.rerun()
            else:
                st.error("Please configure Groq API key first")
    
    with col_clear:
        if st.button("Clear", use_container_width=True):
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



