import streamlit as st
import os
from database import EmailDatabase
from email_agent import EmailAgent
import json
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Content container */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 95%;
    }
    
    /* Compact header */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Compact email list buttons */
    div[data-testid="column"]:first-child .stButton>button {
        text-align: left;
        padding: 0.6rem 0.8rem;
        height: auto;
        white-space: normal;
        line-height: 1.3;
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.2rem 0;
    }
    
    .badge-important {
        background: #ef4444;
        color: white;
    }
    
    .badge-todo {
        background: #f59e0b;
        color: white;
    }
    
    .badge-newsletter {
        background: #3b82f6;
        color: white;
    }
    
    .badge-spam {
        background: #6b7280;
        color: white;
    }
    
    /* Draft highlight */
    .draft-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #667eea;
        margin-top: 1rem;
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Faded content */
    .faded-content {
        opacity: 0.5;
    }
    
    /* Action items */
    .action-item {
        background: #fef3c7;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.4rem 0;
        border-left: 3px solid #f59e0b;
        font-size: 0.9rem;
    }
    
    /* Summary box */
    .summary-box {
        background: #dbeafe;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 3px solid #3b82f6;
        margin-top: 1rem;
        animation: slideIn 0.4s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Chat messages */
    .stChatMessage {
        background: white;
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.4rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Compact spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Email metadata compact */
    .email-meta {
        font-size: 0.75rem;
        color: #6b7280;
        margin: 0.2rem 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-online {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-offline {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Header alignment */
    .header-flex {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
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
            st.session_state.agent = None
    else:
        st.session_state.agent = None

if 'selected_email_id' not in st.session_state:
    st.session_state.selected_email_id = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

if 'show_summary' not in st.session_state:
    st.session_state.show_summary = False

if 'current_summary' not in st.session_state:
    st.session_state.current_summary = ""

# Compact Header - Single line with flexbox
status_badge = '<span class="status-badge status-online">🟢 AI Online</span>' if st.session_state.agent else '<span class="status-badge status-offline">🔴 Offline</span>'

st.markdown(f"""
    <div class="header-flex">
        <h1 style="margin: 0;">✉️ AI Email Assistant</h1>
        <div>{status_badge}</div>
    </div>
""", unsafe_allow_html=True)

# Compact metrics row
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("📧 Total", len(st.session_state.db.emails))
with col_m2:
    st.metric("🟡 To-Do", len(st.session_state.db.get_emails_by_category('To-Do')))
with col_m3:
    st.metric("🔴 Important", len(st.session_state.db.get_emails_by_category('Important')))
with col_m4:
    st.metric("⚫ Spam", len(st.session_state.db.get_emails_by_category('Spam')))

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    if st.session_state.agent is None:
        st.warning("⚠️ API Key Required")
        api_key_input = st.text_input("Groq API Key", type="password")
        if st.button("💾 Connect", use_container_width=True, type="primary"):
            if api_key_input:
                try:
                    st.session_state.agent = EmailAgent(api_key_input)
                    os.environ['GROQ_API_KEY'] = api_key_input
                    st.success("✅ Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.success("✅ Connected")
    
    st.divider()
    
    if st.button("🚀 Process All", use_container_width=True, type="primary", disabled=st.session_state.processing):
        if st.session_state.agent:
            st.session_state.processing = True
            progress = st.progress(0)
            
            total = len(st.session_state.db.emails)
            for idx, email in enumerate(st.session_state.db.emails):
                cat_prompt = st.session_state.db.get_prompt('categorization')
                category = st.session_state.agent.categorize_email(email, cat_prompt)
                
                action_prompt = st.session_state.db.get_prompt('action_extraction')
                actions = st.session_state.agent.extract_actions(email, action_prompt)
                
                st.session_state.db.update_email(email['id'], {
                    'category': category,
                    'action_items': actions
                })
                
                progress.progress((idx + 1) / total)
            
            progress.empty()
            st.success(f"✅ Done!")
            st.session_state.processing = False
            st.rerun()
        else:
            st.error("Configure API key")
    
    st.divider()
    
    with st.expander("🧠 Prompts"):
        prompt_type = st.selectbox(
            "Type",
            ["categorization", "action_extraction", "auto_reply", "summarization"]
        )
        
        current_prompt = st.session_state.db.get_prompt(prompt_type)
        edited_prompt = st.text_area("Template", value=current_prompt, height=120)
        
        if st.button("💾 Save", use_container_width=True):
            st.session_state.db.update_prompt(prompt_type, edited_prompt)
            st.success("Saved!")

# Main Layout
col_left, col_right = st.columns([1, 2.5])

# Left: Compact Email List
with col_left:
    st.markdown("### 📥 Inbox")
    
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
        st.info(f"No emails")
    
    for email in sorted(emails_to_show, key=lambda x: x.get('timestamp', ''), reverse=True):
        is_selected = st.session_state.selected_email_id == email.get('id')
        
        icon = "✅" if is_selected else "📧"
        subject = email.get('subject', 'No Subject')[:35]
        
        if st.button(
            f"{icon} {subject}",
            key=f"email_{email.get('id')}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.selected_email_id = email.get('id')
            st.session_state.show_summary = False
            st.rerun()
        
        st.markdown(f'<div class="email-meta">👤 {email.get("from", "Unknown")[:25]}<br>📅 {email.get("timestamp", "")[:10]}</div>', unsafe_allow_html=True)
        
        if email.get('category'):
            badge_class = {
                "Important": "badge-important",
                "To-Do": "badge-todo",
                "Newsletter": "badge-newsletter",
                "Spam": "badge-spam"
            }.get(email.get('category'), "")
            st.markdown(f'<span class="category-badge {badge_class}">{email.get("category")}</span>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

# Right: Email Details
with col_right:
    if st.session_state.selected_email_id:
        email = st.session_state.db.get_email(st.session_state.selected_email_id)
        
        if email:
            tab1, tab2, tab3 = st.tabs(["📧 Email", "💬 AI Chat", "📊 Stats"])
            
            with tab1:
                has_draft = email.get('draft_reply') is not None
                
                st.markdown(f"## {email.get('subject', 'No Subject')}")
                st.caption(f"**From:** {email.get('from', 'Unknown')} • **Date:** {email.get('timestamp', 'Unknown')[:16]}")
                
                if email.get('category'):
                    badge_class = {
                        "Important": "badge-important",
                        "To-Do": "badge-todo",
                        "Newsletter": "badge-newsletter",
                        "Spam": "badge-spam"
                    }.get(email.get('category'), "")
                    st.markdown(f'<span class="category-badge {badge_class}">{email.get("category")}</span>', unsafe_allow_html=True)
                
                st.divider()
                
                with st.expander("📄 Email Body", expanded=not has_draft):
                    st.write(email.get('body', ''))
                
                if email.get('action_items') and len(email['action_items']) > 0:
                    st.markdown("**📋 Action Items:**")
                    for idx, action in enumerate(email['action_items'], 1):
                        st.markdown(f'<div class="action-item">**{idx}.** {action.get("task", "N/A")}<br>⏰ {action.get("deadline", "No deadline")}</div>', unsafe_allow_html=True)
                
                col_b1, col_b2, col_b3 = st.columns(3)
                
                with col_b1:
                    if st.button("✍️ Reply", use_container_width=True, type="primary"):
                        if st.session_state.agent:
                            with st.spinner("✨ Generating..."):
                                try:
                                    reply_prompt = st.session_state.db.get_prompt('auto_reply')
                                    reply_body = st.session_state.agent.generate_reply(email, reply_prompt)
                                    
                                    if not reply_body.startswith("Reply generation error"):
                                        draft = {
                                            "to": email.get('from', 'Unknown'),
                                            "subject": f"Re: {email.get('subject', 'No Subject')}",
                                            "body": reply_body,
                                            "created_at": "2025-11-25T15:32:00"
                                        }
                                        st.session_state.db.add_draft(email['id'], draft)
                                        st.success("✅ Draft created!")
                                        st.rerun()
                                    else:
                                        st.error(reply_body)
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            st.error("No API key")
                
                with col_b2:
                    if st.button("📝 Summarize", use_container_width=True):
                        if st.session_state.agent:
                            with st.spinner("✨ Summarizing..."):
                                try:
                                    summary_prompt = st.session_state.db.get_prompt('summarization')
                                    summary = st.session_state.agent.summarize_email(email, summary_prompt)
                                    if not summary.startswith("Summarization error"):
                                        st.session_state.show_summary = True
                                        st.session_state.current_summary = summary
                                        st.rerun()
                                    else:
                                        st.error(summary)
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            st.error("No API key")
                
                with col_b3:
                    if has_draft:
                        if st.button("🗑️ Delete", use_container_width=True):
                            st.session_state.db.update_email(email['id'], {'draft_reply': None})
                            st.success("Deleted!")
                            st.rerun()
                
                if st.session_state.show_summary and st.session_state.current_summary:
                    st.markdown(f'<div class="summary-box"><strong>📝 Summary:</strong><br>{st.session_state.current_summary}</div>', unsafe_allow_html=True)
                
                if has_draft:
                    st.markdown("---")
                    st.markdown("### 📧 Draft Reply ✨")
                    draft = email['draft_reply']
                    st.info(f"**To:** {draft.get('to')} • **Subject:** {draft.get('subject')}")
                    st.text_area("Body", value=draft.get('body', ''), height=180, label_visibility="collapsed", key="draft")
                    st.warning("⚠️ Draft not sent automatically")
            
            with tab2:
                st.markdown("### 💬 Ask AI")
                
                user_query = st.chat_input("Ask about this email...")
                
                if user_query:
                    if st.session_state.agent:
                        st.session_state.chat_history.append({"role": "user", "content": user_query})
                        
                        try:
                            context = f"Email from {email.get('from')}: {email.get('subject')}\n\n{email.get('body')}"
                            response = st.session_state.agent.chat_query(user_query, context)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                            st.rerun()
                        except Exception as e:
                            st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {e}"})
                            st.rerun()
                    else:
                        st.error("Configure API key")
                
                st.divider()
                
                if not st.session_state.chat_history:
                    st.info("💡 Ask about sentiment, action items, or get analysis")
                else:
                    st.markdown("### 📜 History (Newest First)")
                    for msg in reversed(st.session_state.chat_history):
                        if msg['role'] == 'user':
                            st.chat_message("user").write(msg['content'])
                        else:
                            st.chat_message("assistant").write(msg['content'])
                
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with tab3:
                st.markdown("### 📊 Statistics")
                
                col_s1, col_s2 = st.columns(2)
                
                with col_s1:
                    st.metric("📝 Characters", len(email.get("body", "")))
                
                with col_s2:
                    st.metric("📖 Words", len(email.get('body', '').split()))
                
                st.divider()
                
                st.markdown("### 📈 Distribution")
                categories = ["Important", "To-Do", "Newsletter", "Spam"]
                
                for cat in categories:
                    count = len(st.session_state.db.get_emails_by_category(cat))
                    pct = count / max(1, len(st.session_state.db.emails))
                    st.progress(pct, text=f"{cat}: {count} ({int(pct*100)}%)")
    
    else:
        st.info("👈 Select an email")
