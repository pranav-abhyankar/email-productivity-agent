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
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Email card styling */
    .email-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 5px solid #667eea;
        cursor: pointer;
    }
    
    .email-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    
    /* Selected email highlight */
    .email-selected {
        border-left: 5px solid #4CAF50;
        background: #f0f9ff;
    }
    
    /* Email detail card */
    .detail-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
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
    
    /* Faded original email when draft exists */
    .faded-content {
        opacity: 0.4;
        transition: opacity 0.3s ease;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        height: 3rem;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
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
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        height: 500px;
        overflow-y: auto;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        margin-top: 0.5rem;
    }
    
    /* Header */
    .header-container {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Action items */
    .action-item {
        background: #fef3c7;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    /* Summary box */
    .summary-box {
        background: #dbeafe;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        margin-top: 1rem;
        animation: slideIn 0.4s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    
    /* Info cards */
    .info-card {
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    
    /* Status indicator */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-offline {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #ef4444;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

if 'show_summary' not in st.session_state:
    st.session_state.show_summary = False

if 'current_summary' not in st.session_state:
    st.session_state.current_summary = ""

# Header
st.markdown('<div class="header-container">', unsafe_allow_html=True)
col_h1, col_h2, col_h3 = st.columns([3, 2, 1])
with col_h1:
    st.markdown("# ✉️ AI Email Assistant")
    st.caption("Powered by Groq AI • LLaMA 3.1 8B Instant")
with col_h2:
    # Metrics in header
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("📧 Total", len(st.session_state.db.emails), delta=None, label_visibility="visible")
    with col_m2:
        st.metric("🟡 To-Do", len(st.session_state.db.get_emails_by_category('To-Do')))
    with col_m3:
        st.metric("🔴 Important", len(st.session_state.db.get_emails_by_category('Important')))
with col_h3:
    if st.session_state.agent:
        st.markdown('<span class="status-online"></span>**AI Online**', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-offline"></span>**AI Offline**', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    if st.session_state.agent is None:
        st.warning("⚠️ Configure Groq API Key")
        api_key_input = st.text_input(
            "API Key",
            type="password",
            help="Get free key: console.groq.com"
        )
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
        st.success("✅ AI Connected")
    
    st.divider()
    
    if st.button("🚀 Process All Emails", use_container_width=True, type="primary", disabled=st.session_state.processing):
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
    
    st.divider()
    
    with st.expander("🧠 Edit Prompts"):
        prompt_type = st.selectbox(
            "Select Prompt",
            ["categorization", "action_extraction", "auto_reply", "summarization"]
        )
        
        current_prompt = st.session_state.db.get_prompt(prompt_type)
        edited_prompt = st.text_area(
            "Template",
            value=current_prompt,
            height=150
        )
        
        if st.button("💾 Save", use_container_width=True):
            st.session_state.db.update_prompt(prompt_type, edited_prompt)
            st.success("Saved!")

# Main Layout - 2 Column for cleaner look
col_left, col_right = st.columns([1, 2])

# Left Column: Email List
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
        st.info(f"No emails in '{filter_cat}'")
    
    for email in sorted(emails_to_show, key=lambda x: x.get('timestamp', ''), reverse=True):
        is_selected = st.session_state.selected_email_id == email.get('id')
        
        if st.button(
            f"{'📧' if not is_selected else '✅'} {email.get('subject', 'No Subject')[:30]}...",
            key=f"email_{email.get('id')}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.selected_email_id = email.get('id')
            st.session_state.show_summary = False
            st.rerun()
        
        # Show preview under button
        st.caption(f"👤 {email.get('from', 'Unknown')[:30]}")
        st.caption(f"📅 {email.get('timestamp', '')[:10]}")
        
        if email.get('category'):
            badge_class = {
                "Important": "badge-important",
                "To-Do": "badge-todo",
                "Newsletter": "badge-newsletter",
                "Spam": "badge-spam"
            }.get(email.get('category'), "")
            st.markdown(f'<span class="category-badge {badge_class}">{email.get("category")}</span>', unsafe_allow_html=True)
        
        st.divider()

# Right Column: Email Details with Tabs
with col_right:
    if st.session_state.selected_email_id:
        email = st.session_state.db.get_email(st.session_state.selected_email_id)
        
        if email:
            tab1, tab2, tab3 = st.tabs(["📧 Email", "💬 AI Chat", "📊 Analytics"])
            
            # Tab 1: Email Content
            with tab1:
                # Check if draft exists
                has_draft = email.get('draft_reply') is not None
                
                # Original email - faded if draft exists
                email_opacity = "faded-content" if has_draft else ""
                
                st.markdown(f'<div class="{email_opacity}">', unsafe_allow_html=True)
                st.markdown(f"## {email.get('subject', 'No Subject')}")
                
                col_meta1, col_meta2 = st.columns([2, 1])
                with col_meta1:
                    st.markdown(f"**From:** {email.get('from', 'Unknown')}")
                    st.caption(f"**Date:** {email.get('timestamp', 'Unknown')}")
                with col_meta2:
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
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Action Buttons
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button("✍️ Generate Reply", use_container_width=True, type="primary"):
                        if st.session_state.agent:
                            with st.spinner("✨ Generating reply..."):
                                try:
                                    reply_prompt = st.session_state.db.get_prompt('auto_reply')
                                    reply_body = st.session_state.agent.generate_reply(email, reply_prompt)
                                    
                                    if not reply_body.startswith("Reply generation error"):
                                        draft = {
                                            "to": email.get('from', 'Unknown'),
                                            "subject": f"Re: {email.get('subject', 'No Subject')}",
                                            "body": reply_body,
                                            "created_at": "2025-11-25T15:16:00"
                                        }
                                        st.session_state.db.add_draft(email['id'], draft)
                                        st.success("✅ Draft created!")
                                        st.rerun()
                                    else:
                                        st.error(reply_body)
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            st.error("Configure API key")
                
                with col_btn2:
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
                            st.error("Configure API key")
                
                with col_btn3:
                    if has_draft:
                        if st.button("🗑️ Delete Draft", use_container_width=True):
                            st.session_state.db.update_email(email['id'], {'draft_reply': None})
                            st.success("Draft deleted!")
                            st.rerun()
                
                # Show summary if generated
                if st.session_state.show_summary and st.session_state.current_summary:
                    st.markdown(f'<div class="summary-box"><strong>📝 AI Summary:</strong><br><br>{st.session_state.current_summary}</div>', unsafe_allow_html=True)
                
                # Show draft if exists - HIGHLIGHTED
                if has_draft:
                    st.markdown('<div class="draft-card">', unsafe_allow_html=True)
                    st.markdown("### 📧 Draft Reply ✨")
                    draft = email['draft_reply']
                    st.markdown(f"**To:** {draft.get('to', 'Unknown')}")
                    st.markdown(f"**Subject:** {draft.get('subject', 'No Subject')}")
                    st.text_area("Draft Body", value=draft.get('body', ''), height=200, label_visibility="collapsed")
                    st.warning("⚠️ Draft saved. Not sent automatically.", icon="⚠️")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Tab 2: AI Chat
            with tab2:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                
                if not st.session_state.chat_history:
                    st.info("💡 Ask me anything about this email!")
                
                for msg in st.session_state.chat_history:
                    if msg['role'] == 'user':
                        st.chat_message("user").write(msg['content'])
                    else:
                        st.chat_message("assistant").write(msg['content'])
                
                st.markdown('</div>', unsafe_allow_html=True)
                
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
                
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            # Tab 3: Analytics
            with tab3:
                st.markdown("### 📊 Email Statistics")
                
                col_stat1, col_stat2 = st.columns(2)
                
                with col_stat1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{len(email.get("body", ""))}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Characters</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_stat2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    word_count = len(email.get('body', '').split())
                    st.markdown(f'<div class="metric-value">{word_count}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Words</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.divider()
                
                st.markdown("### 📈 Category Distribution")
                categories = ["Important", "To-Do", "Newsletter", "Spam"]
                data = {cat: len(st.session_state.db.get_emails_by_category(cat)) for cat in categories}
                
                for cat, count in data.items():
                    st.progress(count / max(1, len(st.session_state.db.emails)), text=f"{cat}: {count}")
    
    else:
        st.info("👈 Select an email from the inbox to view details")
