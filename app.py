import streamlit as st
import os
from database import EmailDatabase
from email_agent import EmailAgent
import json
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    .email-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = EmailDatabase()

if 'agent' not in st.session_state:
    api_key = None
    if os.getenv('GROQ_API_KEY'):
        api_key = os.getenv('GROQ_API_KEY')
    else:
        try:
            if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                api_key = st.secrets['GROQ_API_KEY']
        except:
            pass
    
    if api_key:
        try:
            st.session_state.agent = EmailAgent(api_key)
        except Exception as e:
            st.error(f"Error initializing agent: {e}")
            st.session_state.agent = None
    else:
        st.session_state.agent = None

if 'selected_email_id' not in st.session_state:
    st.session_state.selected_email_id = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

# Header
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    st.title("📧 AI Email Productivity Agent")
    st.caption("Powered by Groq AI | LLaMA 3.1 8B Instant")
with col_header2:
    if st.session_state.agent:
        st.success("🟢 AI Connected", icon="✅")
    else:
        st.error("🔴 API Key Required", icon="⚠️")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    if st.session_state.agent is None:
        st.warning("⚠️ Configure Groq API Key")
        api_key_input = st.text_input(
            "Groq API Key",
            type="password",
            help="Get free API key from console.groq.com"
        )
        if st.button("💾 Save API Key", use_container_width=True):
            if api_key_input:
                try:
                    st.session_state.agent = EmailAgent(api_key_input)
                    os.environ['GROQ_API_KEY'] = api_key_input
                    st.success("✅ Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.success("✅ API Key Configured")
        if st.button("🔄 Change Key"):
            st.session_state.agent = None
            st.rerun()
    
    st.divider()
    
    st.header("🧠 Prompt Configuration")
    
    prompt_type = st.selectbox(
        "Select Prompt",
        ["categorization", "action_extraction", "auto_reply", "summarization"]
    )
    
    current_prompt = st.session_state.db.get_prompt(prompt_type)
    edited_prompt = st.text_area(
        "Edit Prompt",
        value=current_prompt,
        height=150,
        help="Use {from_}, {subject}, {body} as placeholders"
    )
    
    if st.button("💾 Save Prompt", use_container_width=True):
        st.session_state.db.update_prompt(prompt_type, edited_prompt)
        st.success("Saved!", icon="✅")
    
    st.divider()
    
    if st.button("🚀 Process All Emails", type="primary", use_container_width=True, disabled=st.session_state.processing):
        if st.session_state.agent:
            st.session_state.processing = True
            progress = st.progress(0)
            status = st.empty()
            
            total = len(st.session_state.db.emails)
            for idx, email in enumerate(st.session_state.db.emails):
                status.text(f"Processing {idx+1}/{total}...")
                
                cat_prompt = st.session_state.db.get_prompt('categorization')
                category = st.session_state.agent.categorize_email(email, cat_prompt)
                
                action_prompt = st.session_state.db.get_prompt('action_extraction')
                actions = st.session_state.agent.extract_actions(email, action_prompt)
                
                st.session_state.db.update_email(email['id'], {
                    'category': category,
                    'action_items': actions
                })
                
                progress.progress((idx + 1) / total)
            
            status.empty()
            progress.empty()
            st.success(f"✅ Processed {total} emails!")
            st.session_state.processing = False
            st.rerun()
        else:
            st.error("Configure API key first")

# Main content
col1, col2, col3 = st.columns([1, 1.5, 1.2])

# Column 1: Email List
with col1:
    st.subheader("📥 Inbox")
    
    filter_cat = st.selectbox(
        "Filter",
        ["All", "Important", "To-Do", "Newsletter", "Spam", "Uncategorized"],
        label_visibility="collapsed"
    )
    
    emails_to_show = st.session_state.db.emails
    if filter_cat != "All":
        if filter_cat == "Uncategorized":
            emails_to_show = [e for e in emails_to_show if not e.get('category')]
        else:
            emails_to_show = st.session_state.db.get_emails_by_category(filter_cat)
    
    if not emails_to_show:
        st.info(f"No emails in '{filter_cat}'")
    
    for email in sorted(emails_to_show, key=lambda x: x.get('timestamp', ''), reverse=True):
        category_icons = {
            "Important": "🔴",
            "To-Do": "🟡",
            "Newsletter": "🔵",
            "Spam": "⚫"
        }
        
        icon = category_icons.get(email.get('category', ''), "⚪")
        
        if st.button(
            f"{icon} {email.get('subject', 'No Subject')[:35]}...",
            key=f"email_{email.get('id')}",
            use_container_width=True,
            help=f"From: {email.get('from', 'Unknown')}"
        ):
            st.session_state.selected_email_id = email.get('id')
            st.rerun()
        
        st.caption(f"📅 {email.get('timestamp', '')[:10]}")

# Column 2: Email Details
with col2:
    st.subheader("📄 Email Details")
    
    if st.session_state.selected_email_id:
        email = st.session_state.db.get_email(st.session_state.selected_email_id)
        
        if email:
            st.markdown(f"### {email.get('subject', 'No Subject')}")
            
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.caption(f"**From:** {email.get('from', 'Unknown')}")
            with col_meta2:
                if email.get('category'):
                    st.badge(email['category'])
            
            st.caption(f"**Date:** {email.get('timestamp', 'Unknown')}")
            
            st.divider()
            
            with st.expander("📨 Email Body", expanded=True):
                st.write(email.get('body', ''))
            
            if email.get('action_items') and len(email['action_items']) > 0:
                st.markdown("**📋 Action Items:**")
                for idx, action in enumerate(email['action_items'], 1):
                    st.info(f"**{idx}.** {action.get('task', 'N/A')}\n\n⏰ {action.get('deadline', 'No deadline')}")
            
            st.divider()
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("✍️ Generate Reply", use_container_width=True):
                    if st.session_state.agent:
                        with st.spinner("Generating..."):
                            try:
                                reply_prompt = st.session_state.db.get_prompt('auto_reply')
                                reply_body = st.session_state.agent.generate_reply(email, reply_prompt)
                                
                                draft = {
                                    "to": email.get('from', 'Unknown'),
                                    "subject": f"Re: {email.get('subject', 'No Subject')}",
                                    "body": reply_body,
                                    "created_at": "2025-11-25T14:41:00"
                                }
                                
                                st.session_state.db.add_draft(email['id'], draft)
                                st.success("Draft created!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    else:
                        st.error("Configure API key")
            
            with col_btn2:
                if st.button("📝 Summarize", use_container_width=True):
                    if st.session_state.agent:
                        with st.spinner("Summarizing..."):
                            try:
                                summary_prompt = st.session_state.db.get_prompt('summarization')
                                summary = st.session_state.agent.summarize_email(email, summary_prompt)
                                st.info(f"**Summary:**\n\n{summary}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                    else:
                        st.error("Configure API key")
            
            if email.get('draft_reply'):
                st.divider()
                st.markdown("**📧 Draft Reply:**")
                draft = email['draft_reply']
                
                with st.container():
                    st.caption(f"**To:** {draft.get('to', 'Unknown')}")
                    st.caption(f"**Subject:** {draft.get('subject', 'No Subject')}")
                    st.text_area("Draft", value=draft.get('body', ''), height=150, disabled=True, label_visibility="collapsed")
                    st.warning("⚠️ Draft saved. Not sent.", icon="⚠️")
    else:
        st.info("👈 Select an email from inbox")

# Column 3: Chat
with col3:
    st.subheader("💬 AI Assistant")
    
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("💡 Ask me about your emails!")
        
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.chat_message("user").write(msg['content'])
            else:
                st.chat_message("assistant").write(msg['content'])
    
    user_query = st.chat_input("Ask about your emails...")
    
    if user_query:
        if st.session_state.agent:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            try:
                if st.session_state.selected_email_id:
                    email = st.session_state.db.get_email(st.session_state.selected_email_id)
                    context = f"Email from {email.get('from')}: {email.get('subject')}\n\n{email.get('body')}"
                else:
                    todo_emails = st.session_state.db.get_emails_by_category('To-Do')
                    context = f"Total: {len(st.session_state.db.emails)} emails\nTo-Do: {len(todo_emails)}"
                
                response = st.session_state.agent.chat_query(user_query, context)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {e}"})
                st.rerun()
        else:
            st.error("Configure API key first")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Footer Statistics
st.divider()
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.metric("📧 Total", len(st.session_state.db.emails))
with col_stat2:
    st.metric("🟡 To-Do", len(st.session_state.db.get_emails_by_category('To-Do')))
with col_stat3:
    st.metric("🔴 Important", len(st.session_state.db.get_emails_by_category('Important')))
with col_stat4:
    st.metric("⚫ Spam", len(st.session_state.db.get_emails_by_category('Spam')))
