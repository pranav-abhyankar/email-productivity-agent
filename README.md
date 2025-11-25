# 🤖 AI Email Productivity Agent

An intelligent email management system powered by Groq's LLaMA 3.1 8B model that automatically categorizes emails, extracts action items, generates draft replies, and provides AI-powered email analysis through an intuitive chat interface.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1_8B-purple)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **🎯 Smart Email Categorization** – Automatically classifies emails into **Important**, **To-Do**, **Newsletter**, or **Spam** categories  
- **📋 Action Item Extraction** – Identifies tasks and deadlines from email content  
- **✍️ AI Draft Replies** – Generates professional, context-aware email responses  
- **📝 Email Summarization** – Condenses long emails into concise 2–3 sentence summaries  
- **💬 AI Chat Interface** – Ask questions about emails and get instant AI-powered insights  
- **🎨 Modern UI** – Beautiful, responsive interface with gradient backgrounds and smooth animations  
- **⚙️ Customizable Prompts** – Edit AI behavior through configurable prompt templates  
- **📊 Email Analytics** – View statistics, counts, and category distribution  

---

## Project Link

[Streamlit Link](https://ai-email-agent-project.streamlit.app/)

---

## 🏗️ Architecture

The project consists of four main components:

### 1. Email Agent (`email_agent.py`)

Handles all AI operations using **Groq's LLaMA 3.1 8B Instant** model:

- Email categorization  
- Action item extraction with JSON parsing  
- Reply generation with creative temperature settings  
- Email summarization  
- Contextual chat queries about any email  

### 2. Database Layer (`database.py`)

JSON-based storage system managing:

- Email data (inbox, categories, action items, drafts)  
- Prompt templates  
- CRUD operations with automatic persistence to disk  

### 3. User Interface (`app.py`)

Streamlit web application featuring:

- Two-column responsive layout  
- Tab-based navigation (**Email**, **AI Chat**, **Analytics**)  
- Real-time UI updates when emails are processed or edited  
- Custom CSS styling with gradient backgrounds and subtle animations  

### 4. Data Files

- `mock_inbox.json` – Sample email data for testing  
- `prompts.json` – AI prompt templates for different tasks  

---

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.13** or higher  
- **Groq API key** (free at [console.groq.com](https://console.groq.com))  

### Installation

1. **Clone the repository**

   ~~~bash
   git clone https://github.com/pranav-abhyankar/email-productivity-agent.git
   cd email-productivity-agent
   ~~~

2. **Install dependencies**

   ~~~bash
   pip install -r requirements.txt
   ~~~

3. **Set up Groq API Key**

   Create a `.env` file in the project root:

   ~~~bash
   GROQ_API_KEY=your_groq_api_key_here
   ~~~

   Or set it as an environment variable:

   ~~~bash
   export GROQ_API_KEY="your_groq_api_key_here"
   ~~~

### Running the Application

**Start the Streamlit app:**

~~~bash
streamlit run app.py
~~~

The application will open in your default browser at `http://localhost:8501`.

---

## 📧 Mock Inbox Setup

The project includes a pre-configured `mock_inbox.json` with sample emails.

### Loading Your Own Emails

Edit `mock_inbox.json` with your email data:

~~~json
{
  "emails": [
    {
      "id": 1,
      "from": "sender@example.com",
      "subject": "Meeting Request",
      "body": "Email content here...",
      "timestamp": "2025-11-25T10:30:00",
      "category": null,
      "action_items": [],
      "draft_reply": null
    }
  ]
}
~~~

### Email Structure

- **id** (required): Unique integer identifier  
- **from** (required): Sender email address  
- **subject** (required): Email subject line  
- **body** (required): Email content  
- **timestamp** (required): ISO 8601 format datetime  
- **category** (optional): Assigned category (`Important` / `To-Do` / `Newsletter` / `Spam`)  
- **action_items** (optional): Array of extracted tasks and deadlines  
- **draft_reply** (optional): Generated draft response object  

---

## ⚙️ Prompt Configuration

Customize AI behavior by editing `prompts.json` or through the UI sidebar.

### Prompt Structure Example

~~~json
{
  "categorization": {
    "name": "Email Categorization",
    "template": "Categorize this email...\nFrom: {from_sender}\nSubject: {subject}\nBody: {body}"
  }
}
~~~

### Available Prompts

1. **categorization** – Email category assignment  
2. **action_extraction** – Task and deadline extraction  
3. **auto_reply** – Draft reply generation  
4. **summarization** – Email summary creation  

### Placeholder Variables

Use these in your prompt templates:

- `{from_sender}` – Sender email address  
- `{subject}` – Email subject  
- `{body}` – Email content  

### Editing Prompts via UI

1. Open the sidebar in the application  
2. Expand the **🧠 Prompts** section  
3. Select prompt type from dropdown  
4. Edit the template text  
5. Click **💾 Save**  

---

## 📖 Usage Examples

### Basic Workflow

1. **Configure API Key**
   - Enter your Groq API key in the sidebar  
   - Click **💾 Connect**

2. **Process Emails**
   - Click **🚀 Process All** in the sidebar  
   - The app will:
     - Categorize all emails  
     - Extract action items  
   - View results in inbox with color-coded badges  

3. **Manage Individual Emails**
   - Click on an email in the inbox to view full details  
   - View extracted action items  
   - Generate draft replies  
   - Create summaries  
   - Chat with AI about the selected email  

### Feature Examples

**Email Categorization:**

- Automatically sorts emails into 4 categories  
- Visual badges show category at a glance  
- Filter inbox by category using the dropdown  

**Action Item Extraction Example Output:**

~~~json
[
  {
    "task": "Review quarterly report",
    "deadline": "November 30, 2025"
  },
  {
    "task": "Schedule team meeting",
    "deadline": "This week"
  }
]
~~~

**Draft Reply Generation:**

- Click **✍️ Reply** on any email  
- AI generates a professional response  
- Draft is saved locally (not sent automatically)  
- You can edit the draft before sending via your email client  

**Email Summarization:**

- Click **📝 Summarize**  
- Get a 2–3 sentence summary  
- Very useful for long or dense emails  

**AI Chat Interface:**

Ask questions like:

- "What's the sentiment of this email?"  
- "What are the key points?"  
- "Should I prioritize this?"  

The AI uses email context to respond.

---

## 🔍 Advanced Usage

### Custom Prompts Example

~~~text
You are a {role} assistant. Analyze this email.

Context:
From: {from_sender}
Subject: {subject}
Body: {body}

Instructions:
- Be professional
- Identify urgency level
- Suggest action items

Response:
~~~

### Batch Processing

- Add multiple emails in `mock_inbox.json`  
- Click **🚀 Process All**  
- All emails will be:
  - Categorized  
  - Parsed for action items  
  - Ready for summaries and replies  

---

## 🎨 UI Features

### Layout

- **Left Column (1/3)**:  
  - Email inbox with filters  
  - Category dropdown  
  - Status indicators  

- **Right Column (2/3)**:  
  - Email details  
  - Tabs for content, chat, and stats  

### Tabs

1. **📧 Email** – Full email content, action items, reply and summarize buttons  
2. **💬 AI Chat** – Conversational interface for email analysis  
3. **📊 Stats** – Email statistics & category distribution visualizations  

### Visual Indicators

- ✅ Selected email  
- 📧 Unread / unselected email  
- 🔴 **Important** (red badge)  
- 🟡 **To-Do** (yellow badge)  
- 🔵 **Newsletter** (blue badge)  
- ⚫ **Spam** (gray badge)  
- 🟢 **AI Online**  
- 🔴 **AI Offline** (e.g., invalid API key)  

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit 1.32.0  
- **AI Engine**: Groq API (LLaMA 3.1 8B Instant)  
- **Backend**: Python 3.13  
- **Storage**: JSON file system (no external DB required)  
- **Styling**: Custom CSS with animations  
- **Deployment**: Streamlit Cloud / local  

---

## 📁 Project Structure

~~~text
email-productivity-agent/
├── app.py              # Main Streamlit application
├── email_agent.py      # AI agent with Groq integration
├── database.py         # JSON database management
├── mock_inbox.json     # Sample email data
├── prompts.json        # AI prompt templates
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore file
└── README.md           # Project documentation
~~~

---

## 🔧 Configuration Files

### `requirements.txt`

~~~text
streamlit==1.32.0
groq==0.36.0
python-dotenv==1.0.0
~~~

### `.env` (Create this file)

~~~text
GROQ_API_KEY=your_api_key_here
~~~

### `.gitignore`

~~~text
.env
__pycache__/
*.pyc
.streamlit/
~~~

---

## 🚢 Deployment

### Streamlit Cloud

1. Push code to GitHub  
2. Go to Streamlit Cloud (share.streamlit.io)  
3. Connect your repository  
4. Add secrets in the Streamlit Cloud dashboard:

   ~~~text
   GROQ_API_KEY = "your_api_key_here"
   ~~~

5. Deploy – the app will be built and hosted automatically  

### Local Deployment

~~~bash
streamlit run app.py --server.port 8501
~~~

---

## 🤝 Contributing

Contributions are welcome! Please feel free to contribute to this project.

---

## 📝 License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com) for providing ultra-fast LLM inference  
- [Streamlit](https://streamlit.io) for the amazing web framework  
- [Meta AI](https://ai.meta.com) for the LLaMA 3.1 model  

<!--
---

## 🎯 Future Enhancements

- Gmail API integration for real email access  
- Multi-account support  
- Email scheduling  
- Advanced analytics dashboard  
- Custom user-defined categories  
- Sentiment analysis  
- Template library for common responses  
- Calendar integration  
- Mobile responsive design  
- Email threading support  
-->
---

⭐ If you find this project useful, please consider giving it a **star** on GitHub!
