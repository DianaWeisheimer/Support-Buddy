# 🔧 Ariba Case Assistant

AI-powered support engineering tool for SAP Ariba cases.

## Features

- **Case context panel** — ID, category, priority and problem description
- **Investigation log** — track steps already investigated
- **Next steps suggestion** — Claude analyzes the full context and suggests what to do next
- **Message improver** — refine customer-facing messages using case context as reference

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

### 3. Add your API key

Enter your [Anthropic API key](https://console.anthropic.com) in the sidebar.

## Tech stack

- [Streamlit](https://streamlit.io) — UI framework
- [Anthropic Python SDK](https://github.com/anthropic/anthropic-sdk-python) — Claude API
- Model: `claude-sonnet-4-20250514`
