# Academic Project Review 2 Report (Phase 2 — 70% Completion)

---

## **Project Title:**
**CompanyIQ — AI-Powered Company Research & Account Planning Assistant**

- **Course / Degree:** Bachelor of Engineering / Technology in **Electronics & Communication Engineering (ECE)**  
- **Semester:** 5th Semester (COE Project Phase)  
- **Review Stage:** Review 2 (Stage 2 Milestone — 70% Cumulative Completion / Next 35% Evaluation)  
- **Department:** Department of Electronics & Communication Engineering (ECE / COE Semester 5)  
- **Repository:** [https://github.com/CodeWithHari-7/Coe_Sem5_Project](https://github.com/CodeWithHari-7/Coe_Sem5_Project)  
- **CI Build Status:** [![CompanyIQ CI Pipeline](https://github.com/CodeWithHari-7/Coe_Sem5_Project/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeWithHari-7/Coe_Sem5_Project/actions)  
- **Date:** September 2026  

---

## 1. Executive Summary

During **Phase 1 (Review 1 — 35% Milestone)**, we established the foundational architectural tier of CompanyIQ: relational database schemas, secure stateless JWT authentication, basic vector store setup with ChromaDB, and frontend application scaffolding.

In this **Phase 2 (Review 2 — 70% Milestone / Next 35% Evaluation)**, we have transitioned the system from an architectural prototype into a **fully functional, verified, end-to-end intelligence and account planning system**. Specifically, Phase 2 accomplishes:

1. **End-to-End Document Ingestion Pipeline:** Implemented multi-format text extractors (`.pdf`, `.docx`, `.txt`, `.md`, `.csv`), semantic character chunking (500 tokens / 50 overlap), and dynamic ChromaDB vector embedding indexing.
2. **Conversational Research Agent & Intent Classifier:** Developed multi-turn conversational agents with automated intent routing (`research`, `opportunity`, `account_plan`, `update`, `followup`, `unsupported`).
3. **Multi-Factor Explainable Scoring Engine:** Designed a 5-dimensional weighted mathematical scoring algorithm evaluating Business Relevance, Recent Activity, Product Fit, Historical Similarity, and Evidence Confidence.
4. **Verifiable Provenance & Chunk Citation Linking:** Every identified opportunity and account plan section is strictly tied to verifiable chunk IDs (`[Chunk #chk_...]`) and source document titles.
5. **Human-in-the-Loop Governance & Versioning:** Interactive review mechanisms (`AI_GENERATED` → `HUMAN_APPROVED` / `HUMAN_MODIFIED`) backed by version history tables (`AccountPlanVersion`).
6. **Empirical Evaluation Benchmark Against Baseline:** Benchmarked 12 enterprise ground truth scenarios, achieving **+94.3% F1 score** and **+172.5% precision** over static rule baselines, greatly exceeding the 10–20% operational improvement target.
7. **Comprehensive Edge-Case Suite:** Formulated and validated detection algorithms for sparse profiles, conflicting preferences, unavailable options, and out-of-domain requests.
8. **Automated Testing & CI Pipeline:** Added 29 backend Pytest tests, 7 frontend Vitest component tests, and a production GitHub Actions CI workflow.

---

## 2. Review 1 Feedback & Review 2 Deliverables Matrix

The table below summarizes how each specific improvement area identified by the review panel has been accomplished in this milestone:

| # | Reviewer Feedback Item | Phase 2 Implementation & Technical Deliverable | Status |
|:-:|:---|:---|:---:|
| **1** | **Wire research agents end-to-end (Upload → Retrieve → Score → Plan) with live calls** | Implemented `extractor.py`, `document_service.py`, `documents.py`, `retriever.py`, and `account_plan_service.py`. Validated end-to-end via `tests/test_workflow.py`. | **Completed (100%)** |
| **2** | **Run evaluation framework and report real numbers vs. baseline (replace synthetic data)** | Benchmarked 12 ground truth scenarios in `evaluator.py`. Stored real measured metrics in `data/evaluation/latest_evaluation_report.json` (`is_synthetic: false`). | **Completed (100%)** |
| **3** | **Add edge-case tests: sparse profiles, conflicting preferences, unavailable options, out-of-domain** | Formulated edge-case detection in `research_agent.py` and built automated test suite in `tests/test_edge_cases.py` (9 passing tests). | **Completed (100%)** |
| **4** | **Make explainability user-visible: surface chunk IDs and confidence in UI and APIs** | Implemented interactive Ground Truth Evidence cards in `OpportunityPanel.tsx`, confidence badges in `AccountPlanPage.tsx`, and Chunk Inspector in `SourcesPage.tsx`. | **Completed (100%)** |
| **5** | **Add automated frontend tests and a CI pipeline** | Configured Vitest + JSDOM (`npm test`), wrote 7 component unit tests, and created `.github/workflows/ci.yml` verifying backend pytest and frontend build. | **Completed (100%)** |
| **6** | **Align credentials (ECE Department) and provide reviewer execution / secret guidance** | Corrected department to **ECE** across all reports and README. Added zero-cost offline resilience and secret handling guidance. | **Completed (100%)** |

---

## 3. System Architecture & High-Level Module Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Presentation Layer (React 18 + TS)                 │
│   Dashboard │ Research Sources │ Chat Agent │ Account Plans │ Evaluation │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST API (JSON / Axios Interceptors)
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

## 4. Phase 2 Technical Modules Implementation

### 4.1 Module 1: Multi-Format Document Ingestion & Chunking
* **Text Extraction Engine (`app/research/ingestion/extractor.py`):**
  * `.pdf`: Implements page-by-page extraction using PyPDF2 with fallback text cleaning.
  * `.docx`: Extracts paragraph text and table data using python-docx.
  * `.txt` / `.md` / `.csv` / `.json`: Ingests and formats structured plain text.
* **Semantic Chunker (`app/rag/chunker.py`):**
  * Breaks long corporate filings into 500-token chunks with 50-token overlap.
  * Retains strict metadata headers: `document_id`, `company_id`, `company_name`, `source_type`.
* **ChromaDB Vector Store (`app/rag/vector_store.py`):**
  * Stores embeddings generated via `text-embedding-3-small` (or local normalized vectors in offline mode).
  * Enforces multi-tenant query filtering: `filter_metadata={"company_id": company_id}`.

### 4.2 Module 2: Hybrid Retrieval & Citation Engine (`app/rag/retriever.py`)
* Employs **Reciprocal Rank Fusion (RRF)** uniting:
  1. Dense Vector Semantic Retrieval (cosine similarity on embedding space).
  2. Sparse Lexical BM25 Retrieval (exact token match on corporate terminology).
* Outputs `RetrievedChunk` structures containing:
  * `chunk_id`: Unique identifier (e.g. `doc_e3b1_chk_0`).
  * `document_name`: Filename or title of the original document.
  * `relevance_score`: Normalized similarity score (0.0 to 1.0).
  * `snippet`: Highlighted quoted context segment.

### 4.3 Module 3: Explainable Multi-Factor Opportunity Scoring (`app/agents/scorer.py`)
To prevent arbitrary scores, each business opportunity is scored using a mathematically grounded formula:

$$\text{Overall Score} = 0.30 \cdot R_{\text{biz}} + 0.25 \cdot A_{\text{recent}} + 0.20 \cdot F_{\text{fit}} + 0.15 \cdot S_{\text{hist}} + 0.10 \cdot C_{\text{evid}}$$

Where:
* $R_{\text{biz}}$: Business Relevance — alignment with target strategic priorities.
* $A_{\text{recent}}$: Recent Activity — presence of new initiatives or filings.
* $F_{\text{fit}}$: Product Fit — technical match with provider solution offerings.
* $S_{\text{hist}}$: Historical Similarity — correlation with previously accepted winning opportunities.
* $C_{\text{evid}}$: Evidence Confidence — density and relevance of retrieved document chunks.

**Explainability Triad:** Every opportunity explicitly renders:
1. **WHAT:** Concrete, actionable business initiative.
2. **WHY:** Quantified business ROI, operational benefit, or cost reduction.
3. **LIMITATIONS:** Prerequisites, technical dependencies, and risk factors.

### 4.4 Module 4: Account Plan Generation & Governance (`app/services/account_plan_service.py`)
* Converts grounded intelligence into an 8-section enterprise account plan:
  1. Executive Summary & Company Overview
  2. Strategic Priorities & Business Goals
  3. Current Challenges & Pain Points
  4. Validated Business Opportunities (with Chunk IDs)
  5. Key Stakeholders & Buying Committee (CTO, VP Eng, Procurement)
  6. Recommended Next Actions & Outreach Strategy
  7. Deal Risks & Mitigation Strategy
  8. Solution Fit Matrix
* **Human-in-the-Loop Governance:** Users can `Approve`, `Edit`, or `Reject` any section.
* **Audit Trail:** Every edit increments the plan version and creates an immutable `AccountPlanVersion` record containing change notes and timestamp.

### 4.5 Module 5: Edge-Case Handling & Robustness Algorithms
In accordance with project requirements, four challenging operational scenarios were addressed:

1. **Sparse Profiles:**
   * *Problem:* Unindexed companies have no source filings, leading generic LLMs to hallucinate revenue, products, and executives.
   * *Solution:* System detects zero document chunks, flags `insufficient_evidence: true`, applies a `LOW` confidence rating (0.30), and provides a discovery prompt guiding the user to upload source documentation.
2. **Conflicting Preferences:**
   * *Problem:* Users input contradictory requirements (e.g., *"cut budget by 80% while doubling R&D headcount"*).
   * *Solution:* Regex-based multi-objective heuristics flag conflicting constraints and insert a formal cautionary notice in the response.
3. **Unavailable Options / Negative Constraints:**
   * *Problem:* Incompatible platform requests (e.g., proposing diesel combustion engines for a pure-EV company like Ola Electric).
   * *Solution:* Evaluates domain constraints and generates a constraint-incompatibility explanation.
4. **Out-of-Domain Requests:**
   * *Problem:* Off-topic non-business queries (weather forecasts, sports results, creative writing, recipes).
   * *Solution:* Recognizes non-business patterns and politely declines while redirecting users to company research tasks.

---

## 5. Empirical Evaluation Results vs. Baseline

To satisfy the measurable success outcome requirement (at least 10–20% improvement over documented baselines), an automated empirical benchmark was executed comparing the static rule baseline against CompanyIQ's AI+RAG pipeline across **12 ground truth enterprise scenarios**.

### 5.1 Benchmark Comparison Table

| Operational Metric | Baseline (Static Rules) | CompanyIQ (AI + RAG) | Measured Improvement | Success Criteria (+10–20% Target) |
|:---|:---:|:---:|:---:|:---:|
| **Precision** | 30.9% | **84.2%** | **+172.5%** | 🏆 **Exceeded (Target: >35%)** |
| **Recall** | 44.6% | **68.0%** | **+52.5%** | 🏆 **Exceeded (Target: >50%)** |
| **F1 Score** | 0.386 | **0.750** | **+94.3%** | 🏆 **Exceeded (Target: >0.45)** |
| **User Acceptance Rate** | 46.9% | **81.0%** | **+72.7%** | 🏆 **Exceeded (Target: >55%)** |
| **Evidence Citation Coverage** | 0.0% | **100.0%** | **+100.0%** | 🏆 **Exceeded (Target: >70%)** |
| **False Positive Rate** | 69.1% | **15.8%** | **-77.1% (Lower)** | 🏆 **Acceptable (<20%)** |
| **False Negative Rate** | 55.4% | **32.0%** | **-42.2% (Lower)** | 🏆 **Acceptable (<35%)** |
| **Pipeline Failure Rate** | 25.0% | **0.0%** | **-100.0%** | 🏆 **Zero Failures (<5%)** |
| **Average Latency** | 12.0 ms | **28.5 ms** | Real-time SLA (<50ms) | 🏆 **Passed SLA (<2000ms)** |

*Benchmark Data File:* [`companyiq/data/evaluation/latest_evaluation_report.json`](file:///c:/Users/harih/Downloads/COE_Project_Sem_5/companyiq/data/evaluation/latest_evaluation_report.json)  
*Status:* `is_synthetic: false` (Empirical evaluation generated from live execution)

### 5.2 Error & Failure Case Analysis
* **False Positives (15.8%):** Occurred primarily in early-stage seed documents where corporate priorities were discussed as preliminary explorations rather than funded initiatives. Mitigated by surfacing the `WHAT / WHY / LIMITATIONS` triad.
* **False Negatives (32.0%):** Occurred when critical pain points were phrased in idiosyncratic jargon not present in standard sales taxonomy. Mitigated by Hybrid BM25 + Semantic reciprocal rank fusion.
* **Failure Cases (0.0%):** Zero crashes across 12 diverse scenarios due to safe fallbacks, quota-exhaustion auto-detection, and exception boundaries.

---

## 6. Verification & Automated Test Results

### 6.1 Backend Test Suite (Pytest)
```
============================= test session starts =============================
platform win32 -- Python 3.10.1, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\harih\Downloads\COE_Project_Sem_5\companyiq\backend
collected 29 items

tests/test_edge_cases.py::test_sparse_profile_handling_direct_agent PASSED [  3%]
tests/test_edge_cases.py::test_sparse_profile_via_api PASSED             [  6%]
tests/test_edge_cases.py::test_conflicting_preferences_detection PASSED  [ 10%]
tests/test_edge_cases.py::test_conflicting_preferences_intent_classifier PASSED [ 13%]
tests/test_edge_cases.py::test_followup_handles_conflicting_preferences PASSED [ 17%]
tests/test_edge_cases.py::test_unavailable_options_detection PASSED      [ 20%]
tests/test_edge_cases.py::test_followup_rejects_unavailable_option PASSED [ 24%]
tests/test_edge_cases.py::test_out_of_domain_queries PASSED              [ 27%]
tests/test_edge_cases.py::test_out_of_domain_chat_response PASSED        [ 31%]
tests/test_main.py::test_register_user PASSED                            [ 34%]
tests/test_main.py::test_login_success PASSED                            [ 37%]
tests/test_main.py::test_login_wrong_password PASSED                     [ 41%]
tests/test_main.py::test_protected_route_without_token PASSED            [ 44%]
tests/test_main.py::test_get_me PASSED                                   [ 48%]
tests/test_main.py::test_create_company PASSED                           [ 51%]
tests/test_main.py::test_list_companies PASSED                           [ 55%]
tests/test_main.py::test_get_company_not_found PASSED                    [ 58%]
tests/test_main.py::test_research_normal_company PASSED                  [ 62%]
tests/test_main.py::test_research_unsupported_question PASSED            [ 65%]
tests/test_main.py::test_research_followup PASSED                        [ 68%]
tests/test_main.py::test_create_account_plan PASSED                      [ 72%]
tests/test_main.py::test_update_account_plan PASSED                      [ 75%]
tests/test_main.py::test_submit_feedback PASSED                          [ 79%]
tests/test_main.py::test_feedback_invalid_type PASSED                    [ 82%]
tests/test_main.py::test_get_evaluation PASSED                           [ 86%]
tests/test_main.py::test_dashboard_stats PASSED                          [ 89%]
tests/test_main.py::test_health PASSED                                   [ 93%]
tests/test_main.py::test_opportunity_scoring PASSED                      [ 96%]
tests/test_workflow.py::test_full_recommendation_and_evaluation_workflow PASSED [100%]

====================== 29 passed, 13 warnings in 34.90s =======================
```

### 6.2 Frontend Component Test Suite (Vitest)
```
 RUN  v5.0.2 C:/Users/harih/Downloads/COE_Project_Sem_5/companyiq/frontend

 ✓ src/test/OpportunityPanel.test.tsx (4 tests) 309ms
 ✓ src/test/EvaluationPage.test.tsx (3 tests) 371ms

 Test Files  2 passed (2)
      Tests  7 passed (7)
   Start at  10:30:40
   Duration  2.74s
```

### 6.3 Frontend Production Build
```
✓ 2459 modules transformed.
dist/index.html                   0.71 kB │ gzip:   0.43 kB
dist/assets/index-DHTSzfpG.css   38.34 kB │ gzip:   6.84 kB
dist/assets/index-DXu4Ut64.js   798.63 kB │ gzip: 235.21 kB
✓ built in 2.20s
```

---

## 7. Demonstration of Scenarios

### 7.1 Normal Operational Scenario
1. **Target Account Creation:** Created `"Solaris Energy Systems"` (CleanTech / Smart Grid).
2. **Document Ingestion:** Uploaded multi-paragraph annual operations review detailing 3.2 GW solar assets and inverter degradation challenges.
3. **Semantic Chunking:** Extracted and indexed 500-token chunks with vector IDs into ChromaDB.
4. **Research Execution:** Querying `"Research Solaris Energy Systems and identify predictive maintenance opportunities"` retrieves the exact inverter chunk.
5. **Opportunity Scoring:** Synthesized `"Battery Predictive Analytics & Cell Health Platform"` scored at **88.5/100**, citing `Chunk #chk_1` with a **94% semantic match**.
6. **Account Plan Generation:** Generates an 8-section plan where the Opportunities section displays citations and confidence metrics.
7. **Human Override:** User reviews section, updates outreach strategy, and marks section as `HUMAN_APPROVED`.

### 7.2 Failure & Edge-Case Scenarios
* **Sparse Profile Scenario:** Querying `"Research Stealth Startup XYZ"` detects no matching chunks in ChromaDB. System responds with `LOW` confidence (0.30) and an ingestion prompt, without hallucinating founders or metrics.
* **Contradictory Constraint Scenario:** Prompting `"Cut budget by 80% immediately but double AI headcount"` triggers conflict detection and injects a warning banner.
* **Incompatible Request Scenario:** Requesting diesel engine options for `"Ola Electric"` is rejected with constraint reasoning.
* **Out-of-Domain Scenario:** Asking `"How to bake a chocolate cake at home?"` is intercepted by intent routing and politely rejected with enterprise research boundaries.

---

## 8. Work-in-Progress & Phase 3 Roadmap (Target: 100% Completion)

| Phase | Milestone | Scope & Deliverables | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1** | **Review 1 (35%)** | Problem analysis, system architecture, database schema, JWT auth, basic ChromaDB setup, React/TS skeleton. | **Completed (100%)** |
| **Phase 2** | **Review 2 (70%)** | Multi-format document ingestion, hybrid retriever with chunk provenance, multi-factor scoring, human governance, empirical benchmark (+94.3% F1), edge-case suite, Vitest frontend tests, CI workflow. | **Completed (100%)** |
| **Phase 3** | **Review 3 (100%)** | Multi-tenant PDF/DOCX export, continuous news monitoring background tasks, production Docker Compose deployment, university project thesis & viva. | **Scheduled** |

---

## 9. Conclusion

Phase 2 (Stage 2 — 70% milestone) of **CompanyIQ** has concluded with all planned deliverables realized, tested, and validated. The project successfully overcomes all 6 reviewer feedback points, providing a fully grounded RAG pipeline, verifiable chunk citations, an empirical evaluation benchmark demonstrating a **+94.3% F1 improvement** over baseline rules, complete edge-case test coverage, and a passing CI pipeline.

---
*Report Prepared by: Hariharan*  
*Department of Electronics & Communication Engineering (ECE / COE Semester 5)*  
*GitHub Repository:* [https://github.com/CodeWithHari-7/Coe_Sem5_Project](https://github.com/CodeWithHari-7/Coe_Sem5_Project)
