# CompanyIQ — AI-Powered Company Research & Account Planning Assistant

> **COE Semester 5 Project** — An intelligent B2B sales intelligence platform combining RAG (Retrieval-Augmented Generation), LLM-based research agents, and human-in-the-loop account planning.

---

## 🚀 Project Overview

CompanyIQ is a full-stack AI application that automates company research and generates evidence-grounded account plans for B2B sales teams. It replaces manual research with an AI-powered pipeline that:

- **Researches companies** using an LLM agent + RAG over uploaded documents
- **Identifies business opportunities** with a multi-factor scoring engine
- **Generates structured account plans** with AI confidence scores
- **Tracks human feedback** (accept / reject / edit) to evaluate AI quality
- **Detects research changes** and sends notifications when company intelligence updates

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                       │
│  Dashboard │ Research Chat │ Account Plans │ Evaluation  │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (FastAPI)
┌────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend                        │
│  Auth │ Companies │ Research │ Plans │ Evaluation        │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Research Agent Pipeline             │    │
│  │  Intent Classification → RAG Retrieval → LLM →  │    │
│  │  Opportunity Scoring → Account Plan Generation   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌───────────────┐   ┌──────────────┐                   │
│  │  SQLite / PG  │   │   ChromaDB   │                   │
│  │  (Structured) │   │  (Vectors)   │                   │
│  └───────────────┘   └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
companyiq/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── agents/             # LLM provider + research agent + demo data
│   │   ├── api/                # REST API routes (auth, companies, research, plans)
│   │   ├── evaluation/         # Evaluation framework (Baseline vs. AI+RAG)
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── rag/                # Chunker, vector store, hybrid retriever
│   │   ├── schemas/            # Pydantic schemas for all API I/O
│   │   ├── services/           # Business logic (account plans, auth, change detection)
│   │   ├── utils/              # Structured logging
│   │   ├── config.py           # Pydantic settings from .env
│   │   ├── database.py         # DB engine + session
│   │   └── main.py             # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # React + TypeScript + TailwindCSS frontend
│   ├── src/
│   │   ├── components/         # Layout, Sidebar, Panels
│   │   ├── pages/              # Dashboard, Research, Companies, Account Plans, Evaluation
│   │   ├── services/           # API service layer (axios)
│   │   ├── store/              # Zustand auth store
│   │   └── App.tsx             # React Router setup
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Full stack Docker deployment
├── .env.example                # Environment variable template
└── README.md                   # This file
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, TailwindCSS, Recharts, React Router |
| Backend | FastAPI (Python 3.11), SQLAlchemy, Pydantic v2 |
| AI/LLM | OpenAI GPT-4o-mini / Google Gemini |
| Vector DB | ChromaDB (hybrid BM25 + semantic search) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT Bearer tokens (python-jose + passlib/bcrypt) |
| Deployment | Docker + Docker Compose |

---

## 🏃 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repo
git clone https://github.com/CodeWithHari-7/Coe_Sem5_Project.git
cd Coe_Sem5_Project/companyiq

# Copy env and configure
cp .env.example backend/.env
# Edit backend/.env — set LLM_API_KEY or keep DEMO_MODE=true

# Start everything
docker-compose up --build
```

- Frontend: http://localhost:5173  
- Backend API: http://localhost:8000/api/docs

### Option 2: Local Development

**Backend:**
```bash
cd companyiq/backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp ../.env.example .env        # Edit .env
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd companyiq/frontend
npm install
npm run dev
```

---

## 🔐 Demo Login

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@companyiq.demo | Admin@123! |
| Analyst | analyst@companyiq.demo | Analyst@123! |

---

## 🎯 Key Features

### 🔬 AI Research Engine
- Conversational research interface with intent classification
- RAG pipeline: document ingestion → chunking → hybrid retrieval → LLM synthesis
- Evidence-grounded outputs with confidence scores and source citations
- Demo mode with pre-crafted Tata Motors intelligence data

### 📊 Opportunity Scoring
Multi-factor scoring across 5 dimensions (weighted, configurable):
- Business Relevance (30%)
- Recent Activity (25%)
- Product Fit (20%)
- Historical Similarity (15%)
- Evidence Confidence (10%)

### 📝 Account Plans
- AI-generated, structured account plans with 8 sections
- Human-in-the-loop: Approve / Edit / Reject each section
- Version history tracking
- Export to Markdown

### 📈 Evaluation Dashboard
- Baseline vs. AI+RAG system comparison
- Metrics: Precision, Recall, F1, Acceptance Rate, Evidence Coverage, Failure Rate
- Radar chart and bar chart visualizations

### 🔔 Notifications
- Research change detection with impact levels
- Unread notification badge
- Mark-as-read functionality

---

## 🧪 Evaluation Methodology

The system is evaluated against a **keyword-matching baseline**:

| Metric | Baseline | AI+RAG | Improvement |
|--------|----------|--------|-------------|
| Precision | 52% | 76% | +46.2% |
| Recall | 48% | 71% | +47.9% |
| F1 Score | 50% | 73.5% | +47.0% |
| Acceptance Rate | 41% | 68% | +65.9% |
| Evidence Coverage | 35% | 82% | +134.3% |

> ⚠️ **Note:** Current evaluation metrics are synthetic/illustrative. Real evaluation requires live user feedback data with `DEMO_MODE=false`.

---

## 🌍 Environment Variables

See [`.env.example`](companyiq/.env.example) for all configuration options.

Key variables:
```env
LLM_PROVIDER=openai          # openai | gemini | local
LLM_API_KEY=your-key-here
MODEL_NAME=gpt-4o-mini
DEMO_MODE=false              # true = use synthetic data, no LLM needed
DATABASE_URL=sqlite:///./companyiq.db
```

---

## 📚 Academic Context

This project was developed as part of **COE (Computer Engineering) Semester 5** to demonstrate:
- Retrieval-Augmented Generation (RAG) in production systems
- Human-AI collaboration patterns (HITL)
- Evaluation frameworks for AI-generated recommendations
- Full-stack AI application development

---

## 📄 License

MIT License — developed for academic purposes.
