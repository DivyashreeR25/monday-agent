# Skylark BI Agent

An AI-powered Business Intelligence agent that answers founder-level business queries by integrating with monday.com boards containing Work Orders and Deals data.



---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   User (Browser)                     │
│              Next.js Chat + Dashboard UI             │
└──────────────────────┬──────────────────────────────┘
                       │ POST /api/chat
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend (Vercel)                │
│                    agent.py                          │
│         Groq LLM (llama-3.3-70b-versatile)          │
│              Tool Calling / Function Use             │
└──────────┬───────────────────────────────┬──────────┘
           │                               │
┌──────────▼──────────┐     ┌─────────────▼──────────┐
│  monday.com API      │     │   monday.com API        │
│  Work_Order_Tracker │     │   Deal_Funnel_Data       │
│  (176 work orders)  │     │   (200 deals)            │
└─────────────────────┘     └────────────────────────┘
```

### Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Frontend | Next.js + TypeScript | Professional UI, Vercel-native |
| Styling | Tailwind CSS | Rapid dark theme UI |
| Charts | Recharts | React-native, zero config |
| Backend | Python FastAPI | Async, clean API design |
| AI Brain | Groq API (llama-3.3-70b) | Free, fast, excellent reasoning |
| Data | monday.com GraphQL API | Live data, no hardcoding |
| Hosting | Vercel | One-click deploy, free tier |

---

## Project Structure

```
monday-agent/
├── backend/
│   ├── main.py              # FastAPI server + CORS
│   ├── agent.py             # Groq LLM + tool calling logic
│   ├── monday_client.py     # monday.com GraphQL queries
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # API keys (not committed)
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main layout (chat + dashboard)
│   │   └── layout.tsx       # Root layout
│   ├── components/
│   │   ├── ChatPanel.tsx    # Conversational chat interface
│   │   └── Dashboard.tsx    # Live charts (Recharts)
│   └── package.json
├── vercel.json              # Deployment config
├── .gitignore
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- monday.com account with boards imported
- Groq API key (free at console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/DivyashreeR25/monday-agent.git
cd monday-agent
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Create `.env` file in `backend/`:
```env
MONDAY_API_TOKEN=your_monday_api_token
GROQ_API_KEY=your_groq_api_key
```

Run backend:
```bash
python main.py
# Server runs at http://localhost:8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:3000
```

---

## monday.com Configuration

### Step 1 — Get API Token
1. Log in to monday.com
2. Click your avatar → **Administration** → **API**
3. Copy your personal API token

### Step 2 — Import CSV Data
1. In monday.com, click **+ New** → **Import data** → **Excel/CSV**
2. Import `Work_Order_Tracker_Data.csv` → name board exactly: `Work_Order_Tracker_Data`
3. Import `Deal_Funnel_Data.csv` → name board exactly: `Deal_Funnel_Data`
4. Set appropriate column types (Status, Date, Number, Text)

### Step 3 — Board Name Matching
The agent auto-detects boards by name keywords:
- Work Orders board: must contain `work order`, `workorder`, or `project`
- Deals board: must contain `deal`, `sales`, `pipeline`, or `crm`

---

## How It Works

1. User asks a natural language question in the chat
2. FastAPI sends the question to Groq LLM with available tools
3. Groq decides which monday.com data to fetch (work orders, deals, or both)
4. `monday_client.py` queries monday.com GraphQL API live
5. Groq analyzes the data and generates a business insight
6. Frontend displays the response + auto-updates charts

---

## Environment Variables (Vercel)

Add these in Vercel → Project Settings → Environment Variables:

```
MONDAY_API_TOKEN = your_token
GROQ_API_KEY    = your_key
```

---

## Sample Queries

- "How's our pipeline looking this quarter?"
- "Which sectors are performing best?"
- "Prepare a leadership update for the executive meeting"
- "Compare work order completion with our deals pipeline"
- "What's our total pipeline value by sector?"
