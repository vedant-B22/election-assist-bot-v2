# 🗳️ ElectionBot — Election Process Education Assistant

> Built for **PromptWars Hackathon** | Challenge: Election Process Education

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Cloud%20Run-blue?style=for-the-badge&logo=google-cloud)](https://election-bot-v2-265912819375.us-central1.run.app)
[![Python](https://img.shields.io/badge/Python-3.11-green?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-lightgrey?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Gemini-orange?style=for-the-badge&logo=google)](https://cloud.google.com/vertex-ai)

---

## 🎯 What It Does

ElectionBot is an interactive AI-powered assistant that helps Indian citizens understand the complete election process — from voter registration to government formation — in a simple, neutral, and engaging way.

### Features
- 💬 **AI Chat** — Ask any question about Indian elections, get clear neutral answers powered by Google Vertex AI (Gemini)
- 📅 **Timeline** — Visual step-by-step timeline of the entire election process
- 🧠 **Quiz** — Test your election knowledge with an interactive quiz
- 📖 **Glossary** — Quick reference for 10 common election terms

---

## 🏗️ Architecture
User Browser
│
▼
Flask App (Cloud Run)
│
▼
Vertex AI REST API
(Gemini 2.0 Flash)
│
▼
AI Response → User

---

## 🧠 Approach & Logic

The assistant uses a carefully designed system prompt that keeps responses:
- **Neutral** — never favours any party or candidate
- **Educational** — focused on process, not politics  
- **Simple** — easy to understand for all citizens
- **Structured** — numbered steps for processes

The app calls the Vertex AI REST API directly using the Cloud Run metadata token for authentication — no API keys needed, secure by design.

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| AI | Google Vertex AI — Gemini 2.0 Flash |
| Deployment | Google Cloud Run |
| Container | Docker |
| Frontend | Vanilla HTML/CSS/JS |
| Testing | pytest |

---

## 📊 Evaluation Criteria

| Criteria | Implementation |
|---|---|
| ✅ Code Quality | Clean separation of concerns, input validation, env vars for config |
| ✅ Security | No hardcoded secrets, metadata token auth, input length limits |
| ✅ Efficiency | Direct REST API calls, minimal dependencies, single worker |
| ✅ Testing | pytest suite covering all routes and validation |
| ✅ Accessibility | ARIA labels, semantic HTML, keyboard navigation |
| ✅ Google Services | Vertex AI (Gemini 2.0 Flash), Cloud Run deployment |

---

## 🚀 Local Setup

```bash
# Clone the repo
git clone https://github.com/vedant-B22/election-assist-bot-v2
cd election-assist-bot-v2

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

Visit `http://localhost:8080`

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/
```

---

## ☁️ Deployment

Deployed on **Google Cloud Run** using Docker:

```bash
gcloud run deploy election-bot-v2 \
  --source . \
  --project election-assist-bot \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=election-assist-bot,LOCATION=us-central1
```

---

## 📁 Project Structure
election-assist-bot-v2/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container config
├── README.md              # This file
├── templates/
│   └── index.html         # Frontend UI
└── tests/
└── test_app.py        # Unit tests

---

## 💡 Chosen Vertical

**Election Process Education** — helping voters understand the full process from announcement to government formation, making democracy more accessible to every citizen.

---

## 🙏 Built With

- [Google Vertex AI](https://cloud.google.com/vertex-ai) — Gemini 2.0 Flash
- [Google Cloud Run](https://cloud.google.com/run) — Serverless deployment
- [Flask](https://flask.palletsprojects.com) — Python web framework
- Built for [PromptWars Hackathon](https://hack2skill.com) by Vedant Baviskar

---

*ElectionBot is neutral and educational. It does not promote any political party or candidate.*