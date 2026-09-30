# CompanyIQ — AI-Powered Company Research & Account Planning Assistant

> **COE Semester 5 Project** — Department of Electronics & Communication Engineering (ECE)  
> An intelligent B2B sales intelligence platform combining Grounded RAG (Retrieval-Augmented Generation), autonomous research agents, verifiable chunk provenance citations, and human-in-the-loop account plan validation.

[![CompanyIQ CI Pipeline](https://github.com/CodeWithHari-7/Coe_Sem5_Project/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeWithHari-7/Coe_Sem5_Project/actions)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)
![React 18](https://img.shields.io/badge/React-18-61dafb.svg)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)
![Tests](https://img.shields.io/badge/tests-29%20backend%20%7C%207%20frontend-brightgreen.svg)

---

## 🚀 Project Overview

Users in business and commerce often receive generic, ungrounded information and must manually evaluate complex options across scattered documents, significantly slowing decision velocity.

**CompanyIQ** solves this problem by integrating contextual user signals with a curated, multi-format knowledge base to:
1. **Ingest & Ground Enterprise Sources:** Extracts text from PDF, DOCX, TXT, Markdown, and CSV files, generating semantic embeddings stored in local ChromaDB.
2. **Execute Conversational Research:** Multi-turn conversational research agent with intent routing and edge-case detection.
3. **Multi-Factor Opportunity Scoring:** Explainable scoring across 5 weighted dimensions (Business Relevance, Recent Activity, Product Fit, Historical Similarity, Evidence Confidence).
4. **Verifiable Explainability & Provenance:** Every opportunity and account plan section references specific chunk IDs (`[Chunk #chk_...]`), document sources, and similarity match percentages.
5. **Human-in-the-Loop Governance:** Users approve, edit, or reject AI-generated sections with full versioning history and change tracking.
6. **Empirical Evaluation Benchmark:** Automated benchmark engine comparing static baseline heuristics against the AI+RAG pipeline across 12 ground truth enterprise scenarios.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Presentation Layer (React 18 + TS)                 │
│   Dashboard │ Research Sources │ Chat Agent │ Account Plans │ Evaluation │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST API (JSON / Axios)
┌────────────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Asynchronous Backend Engine                  │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────┐  │
│  │ Document Ingestion    │  │ Intent Classification │  │ Opportunity │  │
│  │ (PDF/DOCX/TXT/MD/CSV) │  │ & Edge-Case Handler   │  │ Scorer      │  │
│  └───────────┬───────────┘  └───────────┬───────────┘  └──────┬──────┘  │
│              │                          │                     │         │
│  ┌───────────▼───────────┐  ┌───────────▼───────────┐         │         │
│  │ Semantic Chunker      │  │ Hybrid Retriever      │◄────────┘         │
│  │ (500 tokens / 50 ovr) │  │ (Semantic + BM25)     │                   │
│  └───────────┬───────────┘  └───────────┬───────────┘                   │
│              │                          │                               │
│  ┌───────────▼───────────┐  ┌───────────▼───────────┐                   │
│  │ ChromaDB Vector Store │  │ LLM Synthesis Engine  │                   │
│  │ (Persistent Local)    │  │ (OpenAI / Demo Mode)  │                   │
│  └───────────────────────┘  └───────────┬───────────┘                   │
│                                         │                               │
│  ┌──────────────────────────────────────▼────────────────────────────┐  │
│  │ Account Plan Generator with Chunk Citations ([Chunk #chk_...])    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│                        Persistence & Storage Layer                      │
│        SQLite / PostgreSQL (Metadata, Plans, Feedback, Chunks)          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Measured Empirical Evaluation Results vs. Baseline

The system was evaluated against a static rule baseline across **12 ground truth enterprise scenarios** (automotive, IT/cloud, healthcare, fintech, renewables, and 4 edge cases).

> **Measurable Success Outcome:** The objective mandates at least a 10–20% improvement in primary operational metrics. **CompanyIQ achieves a +94.3% improvement in F1 Score and +172.5% improvement in Precision**, significantly exceeding the target.

| Operational Metric | Baseline (Static Rules) | CompanyIQ (AI+RAG) | Net Improvement | Target (+10–20%) |
| :--- | :---: | :---: | :---: | :---: |
| **Precision** | 30.9% | **84.2%** | **+172.5%** | ✅ Exceeded |
| **Recall** | 44.6% | **68.0%** | **+52.5%** | ✅ Exceeded |
| **F1 Score** | 0.386 | **0.750** | **+94.3%** | ✅ Exceeded |
| **User Acceptance Rate** | 46.9% | **81.0%** | **+72.7%** | ✅ Exceeded |
| **Evidence Citation Coverage** | 0.0% | **100.0%** | **+100.0%** | ✅ Exceeded |
| **False Positive Rate** | 69.1% | **15.8%** | **-77.1%** (Lower) | ✅ Exceeded |
| **False Negative Rate** | 55.4% | **32.0%** | **-42.2%** (Lower) | ✅ Exceeded |
| **Failure Rate** | 25.0% | **0.0%** | **-100.0%** (Robust) | ✅ Exceeded |
| **Average Latency** | 12.0 ms | **28.5 ms** | Real-time SLA | ✅ Passed |

*Source: `companyiq/data/evaluation/latest_evaluation_report.json` generated by `Evaluator.run_empirical_benchmark()`.*

---

## 🛡️ Edge-Case Handling & Robustness

The research agent actively tests and handles the four edge cases defined in the objective:
1. **Sparse Profiles:** When an unindexed company is queried, the system detects zero evidence coverage, returns a `LOW` confidence rating (0.30), flags `insufficient_evidence: true`, and prompts the user to upload source documentation rather than hallucinating commercial claims.
2. **Conflicting Preferences:** Multi-objective contradictions (e.g. *"cut R&D budget by 80% while doubling R&D headcount"*) are caught by conflict detection heuristics, generating a formal notice in conversational responses.
3. **Unavailable Options / Incompatibilities:** Incompatible requests (e.g. proposing diesel powertrains for a pure electric mobility firm like Ola Electric) are flagged with clear constraint explanations.
4. **Out-of-Domain Requests:** Non-business queries (weather forecasts, sports results, creative writing, cooking recipes) are gracefully routed with clear domain boundaries.

---

## 🔬 Verifiable Explainability & Provenance

Reviewers can trace each recommendation directly to source documents:
- **Opportunity Cards:** Surface ground truth evidence badges showing Document Title, Chunk ID (`Chunk #chk_...`), exact quoted snippet, and semantic match percentage.
- **Account Plans:** Each section displays its computed confidence score (`85% Conf`) and an expandable **Section Provenance Citations** list linking claims to chunk IDs.
- **Research Sources Inspector:** Reviewers can navigate to `/sources`, select any ingested document, and click **View Chunks** to inspect vector IDs, token lengths, and raw chunk texts.

---

## 🏃 Quick Start for Reviewers

### One-Click Single URL Launcher (Recommended)

To run the entire application on a single port (`http://localhost:8000`) without managing separate terminal windows:

```cmd
run_single_url.bat
```

1. Open your browser at **http://localhost:8000**
2. Login with reviewer credentials:
   - **Email:** `admin@companyiq.demo` (or `analyst@companyiq.demo`)
   - **Password:** `Admin@123!` (or `Analyst@123!`)
3. Explore the pre-seeded enterprise accounts (Tata Motors, Infosys), upload new documents in **Research Sources**, generate grounded account plans, and inspect the **Evaluation Dashboard**.

---

### Running the Automated Test Suites

Both backend and frontend have comprehensive automated test suites:

#### 1. Backend Tests (29 tests — Unit, Edge-Case, Workflow & Evaluation)
```bash
cd companyiq/backend
pytest tests/ -v
```
*Result: 29 passed in ~35 seconds (100% pass rate).*

#### 2. Frontend Tests (7 Vitest Component Tests)
```bash
cd companyiq/frontend
npm test
```
*Result: 2 test files, 7 passed (OpportunityPanel, EvaluationPage).*

#### 3. Frontend Production Build Verification
```bash
cd companyiq/frontend
npm run build
```
*Result: TypeScript check (`tsc`) + Vite production bundle successfully built.*

---

## 🔑 Environment & Secret Handling Guidance

The repository includes safe defaults allowing complete offline and zero-cost operation without requiring paid API credits.

### Configuration Template (`companyiq/backend/.env`)

```env
# ============================================================================
# Security Secret (Generate with: python -c "import secrets; print(secrets.token_hex(32))")
# ============================================================================
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-long-abc123xyz
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ============================================================================
# AI & LLM Provider Configuration
# ============================================================================
# Options: 'demo' (zero cost, deterministic high precision) | 'openai' | 'gemini'
LLM_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
DEMO_MODE=false

# Optional: Add your OpenAI or Gemini key to enable live online generative completions
# If the key is exhausted or missing, the system automatically falls back to deterministic RAG
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# ============================================================================
# Vector Store & Database
# ============================================================================
CHROMA_PERSIST_DIRECTORY=./chroma_db
DATABASE_URL=sqlite:///./companyiq.db
```

### Guidance for Reviewers:
- **Zero-Cost Operation:** The system features a built-in deterministic intelligence engine that guarantees 100% test passage and full UI interactivity even when no OpenAI API credits are available.
- **Quota Resilience:** If an OpenAI API key returns HTTP 429 (Quota Exceeded), the backend logs a fast-fallback warning and transparently serves high-precision grounded research without latency penalties.

---

## 📁 Project Structure

```
COE_Project_Sem_5/
├── .github/workflows/
│   └── ci.yml                          # Continuous Integration workflow
├── companyiq/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── agents/                 # Research agent, LLM provider, prompt engineering
│   │   │   ├── api/                    # REST routers: auth, companies, documents, research, plans
│   │   │   ├── evaluation/             # Empirical benchmark runner & baseline recommender
│   │   │   ├── models/                 # SQLAlchemy database schema
│   │   │   ├── rag/                    # Multi-format extractor, chunker, vector store, retriever
│   │   │   ├── research/ingestion/     # PDF, DOCX, TXT, MD, CSV text extractors
│   │   │   ├── schemas/                # Pydantic validation schemas
│   │   │   └── services/               # DocumentService, AccountPlanService, AuthService
│   │   ├── tests/
│   │   │   ├── test_main.py            # Core API functionality & authentication
│   │   │   ├── test_edge_cases.py      # Sparse, conflict, unavailable, out-of-domain tests
│   │   │   └── test_workflow.py        # End-to-end integration test (Upload → Score → Plan)
│   │   └── requirements.txt
│   ├── data/
│   │   └── evaluation/
│   │       ├── benchmark_dataset.json  # 12 Ground truth enterprise scenarios
│   │       └── latest_evaluation_report.json # Empirical measured benchmark results
│   └── frontend/
│       ├── src/
│       │   ├── components/             # Layout, OpportunityPanel with chunk citations
│       │   ├── pages/                  # Dashboard, Research, Sources, AccountPlans, Evaluation
│       │   ├── services/               # Axios API client (documentsApi, evaluationApi, etc.)
│       │   └── test/                   # Vitest tests: OpportunityPanel.test, EvaluationPage.test
│       ├── package.json
│       └── vite.config.ts
├── run_single_url.bat                  # One-click Windows launch script
├── Review_1_Report.md                  # Academic Review Report (ECE Department)
└── README.md                           # This documentation
```

---

## 📚 Academic Context

- **Department:** Department of Electronics & Communication Engineering (ECE)
- **Course / Semester:** COE Semester 5 Project
- **Review Stage:** Review 1 & Review 2 Milestone Deliverables
- **Author:** Hariharan
- **Repository:** [https://github.com/CodeWithHari-7/Coe_Sem5_Project.git](https://github.com/CodeWithHari-7/Coe_Sem5_Project.git)

---

## 📄 License

MIT License — Developed for academic review and research purposes.
