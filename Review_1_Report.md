# Academic Project Review 1 Report (Phase 1 — 35% Completion)

---

## **Project Title:**
**CompanyIQ — AI-Powered Company Research & Account Planning Assistant**

- **Course / Degree:** Bachelor of Engineering / Technology (Computer Science & Engineering)  
- **Semester:** 5th Semester  
- **Review Stage:** Review 1 (Phase 1 Milestone — 35% Completion)  
- **Repository:** [https://github.com/CodeWithHari-7/Coe_Sem5_Project.git](https://github.com/CodeWithHari-7/Coe_Sem5_Project.git)  
- **Date:** September 2026  

---

## 1. Executive Summary

In enterprise B2B sales, account executives (AEs) and sales development representatives (SDRs) spend an estimated 15 to 25 hours every week manually scavenging corporate websites, financial 10-K filings, press releases, and industry news to prepare meaningful account plans. Despite the rise of general-purpose large language models (LLMs) like ChatGPT, raw models are insufficient for enterprise selling: they frequently hallucinate financial figures, lack access to real-time proprietary or fresh market data, and fail to provide verifiable source citations that sales teams can trust.

**CompanyIQ** addresses this bottleneck by developing an autonomous, end-to-end sales intelligence assistant. It unites Retrieval-Augmented Generation (RAG), autonomous multi-agent task execution, and interactive human-in-the-loop validation within a modern web dashboard.

This **Review 1 Report** documents the successful completion of **Phase 1 (35% milestone)**. During this phase, I established the end-to-end foundational architecture:
1. Designed and structured the relational data schemas and entity-relationship models using SQLAlchemy and Pydantic.
2. Implemented stateless, secure JWT authentication with bcrypt password hashing and token blacklisting.
3. Built the document processing and RAG pipeline foundation, integrating text chunking, embedding generation (`text-embedding-3-small`), and ChromaDB persistent vector storage.
4. Scaffolded the FastAPI asynchronous backend architecture and RESTful endpoint hierarchy.
5. Developed the React 18 + TypeScript + Vite frontend client, including responsive layout infrastructure, routing guards, global state management, and the initial interactive user interface.
6. Conducted preliminary functional testing and vector retrieval validation.

---

## 2. Problem Statement & Motivation

### 2.1 The Problem
Preparing an enterprise account strategy requires synthesizing multiple disparate data sources:
- **Corporate Fundamentals:** Company history, leadership hierarchy, tech stack, and offerings.
- **Financial & Regulatory Disclosures:** Revenue trajectory, risk factors, and strategic initiatives from annual reports and SEC filings.
- **Dynamic Market Signals:** Recent leadership changes, funding rounds, strategic acquisitions, and product launches.

When sales professionals do this manually, research is slow, shallow, and inconsistent across teams. When they rely on generic AI chatbots, three acute issues arise:
1. **Hallucination Risk:** Standard LLMs confidently fabricate revenue numbers, executive names, or product capabilities.
2. **Absence of Provenance:** Generic chatbots provide answers without exact document citations, making verification tedious.
3. **Lack of Sales Context:** Generic models produce generic essays rather than structured, actionable frameworks (e.g., MEDDPICC, pain point matrices, and personalized outreach drafts).

### 2.2 Project Motivation
By building **CompanyIQ**, our goal is to bridge the gap between autonomous AI capabilities and enterprise reliability. By grounding LLM inference in verified ingested documents via a tailored RAG pipeline and providing a transparent human-in-the-loop review interface, the platform reduces preparation time from hours to minutes while maintaining citation-backed credibility.

---

## 3. Project Objectives & Scope

### 3.1 Primary Objectives
- **Automated Intelligence Gathering:** Build autonomous agent workflows capable of gathering and organizing company intelligence.
- **Grounded Retrieval-Augmented Generation (RAG):** Enable sales teams to upload internal case studies, whitepapers, and annual reports into a vector database to generate answers strictly grounded in cited source material.
- **Structured Strategy Formulation:** Automatically synthesize research into standard B2B frameworks (pain points, target personas, MEDDPICC qualification, value proposition, and outreach hooks).
- **Human-in-the-Loop Quality Control:** Offer an evaluation dashboard allowing users to inspect citation confidence, flag discrepancies, and edit generated strategies before export.

### 3.2 Scope for Phase 1 (35% Milestone)
The agreed scope for Review 1 encompasses the foundational architectural tier:
- [x] Complete domain analysis and system requirements specification.
- [x] Database schema design and ORM entity mapping (Users, Companies, Research Tasks, Account Plans, Evaluations).
- [x] Secure authentication engine (JWT authentication, role handling, password hashing).
- [x] Vector store infrastructure setup with ChromaDB and OpenAI embeddings.
- [x] Document ingestion, text extraction, and recursive character chunking engine.
- [x] Frontend application skeleton with React, TypeScript, Vite, Tailwind CSS, and protected route handlers.
- [x] Core backend API routing architecture using FastAPI with interactive Swagger/OpenAPI documentation.

---

## 4. Literature Survey & Comparative Analysis

| Feature / Solution | Manual SDR Research | Generic AI (ChatGPT / Claude) | Commercial Tools (ZoomInfo / Apollo) | **CompanyIQ (Proposed System)** |
| :--- | :--- | :--- | :--- | :--- |
| **Time per Account** | 3 to 6 Hours | 15 to 30 Minutes | 1 to 2 Hours | **< 3 Minutes** |
| **Citation & Provenance** | Manual bookmarks | Poor / Prone to Hallucinations | Database attributes only | **Direct text-chunk citations with confidence scores** |
| **Custom Document Context** | High (manual reading) | Low (limited context window) | None | **Integrated RAG with ChromaDB vector store** |
| **B2B Framework Alignment** | Depends on rep skill | Requires complex prompt crafting | Fixed contact database | **Built-in MEDDPICC, Persona & Value Proposition generators** |
| **Human-in-the-loop Editing** | Fully manual | Chat prompt iteration | Not applicable | **Interactive web dashboard with editable drafts** |

---

## 5. System Architecture & High-Level Design

The system follows a modern, decoupled microservice-ready architecture comprising four integrated layers:

```
+-------------------------------------------------------------------------+
|                       Presentation Layer (Frontend)                     |
|         React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons       |
|    [Auth / Login]  <--->  [Dashboard]  <--->  [Company / Research / Plans]  |
+------------------------------------+------------------------------------+
                                     |  REST API / JSON (Axios)
                                     v
+-------------------------------------------------------------------------+
|                        API & Orchestration Layer                        |
|                    FastAPI (Asynchronous Python 3.11+)                  |
|  - JWT Auth Middleware      - Validation (Pydantic v2)                  |
|  - Company Profiling API    - Research & Agent Endpoints                |
|  - Document Upload API      - Account Plan & Evaluation Service         |
+-------------------+--------------------------------+--------------------+
                    |                                |
                    v                                v
+-----------------------------------+  +----------------------------------+
|      RAG & Intelligence Layer     |  |       Persistence Layer          |
|  - Document Ingestion & Chunking  |  |  - Relational: SQLite / Postgre- |
|  - OpenAI text-embedding-3-small  |  |    SQL via SQLAlchemy ORM        |
|  - ChromaDB Vector Store          |  |  - File Upload Storage           |
|  - Retrieval & Prompt Synthesis   |  |  - Session & Token Management    |
+-----------------------------------+  +----------------------------------+
```

---

## 6. Work Completed So Far (Phase 1 — 35% Completion Breakdown)

### 6.1 Database Schema & Entity Modeling
I designed normalized relational schemas managed through SQLAlchemy ORM, supported by strict Pydantic models for request/response serialization:
- **User Model:** `id`, `email`, `hashed_password`, `full_name`, `role`, `is_active`, `created_at`.
- **Company Model:** `id`, `name`, `domain`, `industry`, `size`, `description`, `revenue_range`, `headquarters`, `tech_stack`, `created_at`.
- **ResearchTask Model:** `id`, `company_id`, `status` (pending, in-progress, completed, failed), `research_depth`, `extracted_data`, `error_message`.
- **AccountPlan Model:** `id`, `company_id`, `user_id`, `executive_summary`, `pain_points`, `target_personas`, `meddpicc_analysis`, `outreach_strategy`.
- **Feedback & Evaluation Model:** `id`, `plan_id`, `faithfulness_score`, `relevance_score`, `hallucination_flag`, `user_notes`.

### 6.2 Authentication & Security Infrastructure
- Implemented stateless **OAuth2 password bearer** flow using JSON Web Tokens (`python-jose`).
- Secured credentials using **bcrypt** with automated salt generation.
- Built reusable FastAPI dependency injection guards (`get_current_user`, `get_current_active_user`) ensuring protected access across all sensitive endpoints.
- Configured CORS middleware with fine-grained origin whitelisting.

### 6.3 Document Processing & Vector Store (RAG Backbone)
- Established the vector storage pipeline using **ChromaDB**.
- Integrated an automated chunking utility with sliding overlap windows (1000 character chunks with 200 character overlap) to preserve semantic coherence across boundaries.
- Integrated OpenAI's `text-embedding-3-small` model (1536-dimensional embeddings), yielding high retrieval precision at minimal latency and operational cost.
- Created persistent collections indexed by company identifier, enabling tenant/company-isolated retrieval.

### 6.4 Backend REST API Scaffolding
Built modular FastAPI routers across distinct domain concerns:
- `/api/auth`: Registration, login, profile inspection, token refresh.
- `/api/companies`: Company creation, listing, detail lookup, and metadata updates.
- `/api/research`: Research task initialization, status querying, and raw intelligence retrieval.
- `/api/account-plans`: Account plan generation trigger, persistence, and retrieval.
- `/api/evaluation`: Feedback logging and metric verification endpoints.

### 6.5 Frontend Foundation & UI Architecture
- Initialized the single-page application using **Vite + React 18 with TypeScript**.
- Built a cohesive design system using **Tailwind CSS**, featuring dark/light aesthetic support, glassmorphism cards, and intuitive navigation sidebars.
- Implemented client-side routing via `react-router-dom` with a **ProtectedRoute** component that validates JWT token presence and expiry before granting access to dashboard views.
- Created responsive views for:
  - `LoginPage.tsx` (clean credential entry and validation feedback).
  - `DashboardPage.tsx` (overview metric cards, quick action buttons, and recent activity).
  - `CompaniesPage.tsx` (search and account overview).
  - Modular layouts including header, navigation drawer, and status banners.

### 6.6 Code Repository & Version Control
- Structured the project into modular `backend/` and `frontend/` roots with environment variable separation (`.env.example` vs `.env`).
- Configured `.gitignore` to prevent secret leakage and binary clutter.
- Successfully committed and pushed the codebase to GitHub: [https://github.com/CodeWithHari-7/Coe_Sem5_Project.git](https://github.com/CodeWithHari-7/Coe_Sem5_Project.git).

---

## 7. Technology Stack Justification

| Technology | Role | Justification |
| :--- | :--- | :--- |
| **Python 3.11+ / FastAPI** | Backend Framework | Native asynchronous concurrency (`async`/`await`), automatic OpenAPI docs, and rich ecosystem for LLM/RAG libraries. |
| **SQLAlchemy + Pydantic v2** | ORM & Data Validation | Clean decoupling between database entities and API data contracts with fast C-extension parsing. |
| **ChromaDB** | Vector Database | Lightweight, embeddable, low latency, and easily migrated to cloud clusters without heavy infrastructure overhead. |
| **React 18 + TypeScript** | Frontend UI | Component reusability, compile-time type safety preventing runtime crashes, and fast development turnaround. |
| **Tailwind CSS** | Styling & UI | Utility-first styling enabling rapid creation of modern, responsive, and aesthetically pleasing enterprise dashboards. |
| **Vite** | Build Tool | Instant hot module replacement (HMR) and optimized build times compared to legacy Webpack. |

---

## 8. Challenges Encountered & Solutions in Phase 1

1. **Context Window vs. Chunk Boundary Loss:**
   * *Problem:* Arbitrary character splitting broke sentences and split vital financial facts across different chunks.
   * *Solution:* Adopted recursive character splitting with a 20% sliding window overlap and newline prioritisation, preserving sentence structures.

2. **Secure Token Handling across Frontend and Backend:**
   * *Problem:* Managing authentication state across page reloads without exposing tokens to XSS risks.
   * *Solution:* Structured standardized Axios request interceptors that inject the bearer token dynamically from protected memory/secure storage, accompanied by immediate redirect guards upon receiving HTTP 401 Unauthorized responses.

3. **Multi-Tenant Document Isolation:**
   * *Problem:* Preventing queries for Company A from retrieving embedded vector chunks belonging to Company B.
   * *Solution:* Implemented scoped ChromaDB collections and metadata filtering where every document chunk is tagged with `company_id`, enforcing strict tenant boundaries during similarity search.

---

## 9. Work-in-Progress & Phase 2 Roadmap (Target: 70% Completion)

With Phase 1 completed, the focus for **Review 2 (Phase 2)** is the implementation of autonomous research agents and intelligence generation:

```
[Phase 1: 35%]  ===> [Phase 2: 70%]                       ===> [Phase 3: 100%]
Foundational Infra   Agent Workflows & Intelligence Synthesis  Evaluation & Polish
- DB Schemas & Auth  - Multi-source Web Scraping Engine       - Hallucination Scoring
- RAG Vector Store   - LangChain Research Agent                - PDF/Docx Export
- React Skeleton     - MEDDPICC & Strategy Generator           - End-to-End Testing
- Base CRUD APIs     - Live Context Grounding & Citations      - Final Documentation
```

### Key Milestones for Review 2:
1. **Multi-Source Scraping & Intelligence Aggregator:** Connect live scraping utilities (HTML parsing, news feeds, search APIs) to populate company profiles dynamically.
2. **Autonomous Research Agent Execution:** Implement LangChain/OpenAI tool-calling agents that parse objectives, query web search and internal vectors, and synthesize structured company profiles.
3. **Automated Account Plan Synthesis:** Build generative prompts that format raw context into sales-ready artifacts: executive summaries, pain point matrices, competitive differentiation, and MEDDPICC frameworks.
4. **Citation Engine:** Return exact source chunk IDs and text highlights alongside every generated claim.

---

## 10. Project Timeline & Phase-Wise Progress

| Phase | Milestone | Scope / Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Review 1 (35%)** | Problem definition, system architecture, database schema, JWT auth, ChromaDB vector store, RAG chunking pipeline, React/TS UI foundation, initial API scaffolding. | **Completed (100%)** |
| **Phase 2** | **Review 2 (70%)** | Web search scraping tools, autonomous multi-step research agent, MEDDPICC account plan generation, citation linking, interactive plan editing. | **In Progress** |
| **Phase 3** | **Review 3 (100%)** | Automated hallucination evaluation framework, export to PDF/DOCX, performance benchmarking, user acceptance testing, final report and presentation. | **Scheduled** |

---

## 11. Conclusion

Phase 1 of **CompanyIQ** has concluded with all planned 35% milestone deliverables fully realized and verified. The system boasts a robust architectural foundation: an asynchronous FastAPI backend, a clean and responsive React/TypeScript frontend, a secure authentication subsystem, and an operational ChromaDB vector pipeline. The codebase has been organized under version control and pushed to GitHub. The project is on schedule to enter Phase 2, which will focus on deploying the autonomous research agents and MEDDPICC generation workflows.

---
*Report Prepared by: Hariharan*  
*Department of Computer Science & Engineering (COE Semester 5)*  
*GitHub: [https://github.com/CodeWithHari-7/Coe_Sem5_Project.git](https://github.com/CodeWithHari-7/Coe_Sem5_Project.git)*
