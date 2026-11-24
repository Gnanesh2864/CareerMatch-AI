# CareerMatch AI — Architecture Specification

## 1. System Overview
CareerMatch AI is an AI-powered career intelligence and job matching platform that connects candidate profiles with career opportunities through semantic retrieval, hybrid search, explainable ranking, grounded RAG Q&A, and autonomous agentic workflows.

```
+------------------------------------------------------------------------------------+
|                                    React SPA                                       |
|  (Dashboard, Semantic Search, Job Tracker, Profile Editor, Career Agent, Eval Lab) |
+------------------------------------------+-----------------------------------------+
                                           | HTTP / REST API (JWT Auth)
                                           v
+------------------------------------------------------------------------------------+
|                                FastAPI Backend Engine                              |
|                                                                                    |
|  +-------------------+  +-------------------+  +--------------------------------+  |
|  | Resume Extraction |  | Ingestion Pipeline|  | Career Agent Orchestrator      |  |
|  | - PDF / Text parse|  | - Source adapters |  | - 14 discrete tools            |  |
|  | - Pydantic schemas|  | - Deduplication   |  | - Guardrails & state tracking  |  |
|  | - Inferred vs explicit - Expiration      |  | - Multi-step workflows         |  |
|  +-------------------+  +-------------------+  +--------------------------------+  |
|                                                                                    |
|  +------------------------------------------------------------------------------+  |
|  | Retrieval & Ranking Subsystem                                                |  |
|  | - Vector Embeddings (sentence-transformers / all-MiniLM-L6-v2)               |  |
|  | - BM25 / FTS Keyword Search                                                  |  |
|  | - Reciprocal Rank Fusion (RRF) & Hybrid Score Fusion                         |  |
|  | - Multi-Signal Ranking Engine (Skills, Exp, Edu, Preferences)                 |  |
|  | - Grounded Match Explanation Generator                                       |  |
|  +------------------------------------------------------------------------------+  |
|                                                                                    |
|  +-------------------+  +-------------------+  +--------------------------------+  |
|  | RAG Engine        |  | Skill-Gap Engine  |  | Evaluation Framework           |  |
|  | - Profile + Jobs  |  | - Taxonomy compare|  | - Recall@K, NDCG@K, MRR        |  |
|  | - Evidence citation - Priority & Roadmap|  | - Retrieval vs Hybrid vs Rerank|  |
|  | - Injection guards|  | - Job evidence    |  | - RAG & Agent Benchmarks       |  |
|  +-------------------+  +-------------------+  +--------------------------------+  |
+------------------------------------------+-----------------------------------------+
                                           |
                                           v
+------------------------------------------------------------------------------------+
|                         Dual-Mode Persistence Layer                                |
|  - PostgreSQL with pgvector (Production / Docker)                                  |
|  - SQLite + NumPy Vector Index (Zero-dependency Local Development Mode)            |
+------------------------------------------------------------------------------------+
```

## 2. Key Subsystems & Design Choices

### 2.1 Ingestion & Normalization (`backend/app/ingestion`)
- **Adapters**: Modular source adapters supporting Open Job APIs, public datasets (e.g. HuggingFace tech jobs / Arbeitnow), and structured JSON/CSV imports.
- **Deduplication**: Content hashing (`SHA256(company + title + normalized_location)`) ensures duplicate listings across sources are consolidated without data bloat.
- **Schema Validation**: Every listing is strictly validated against the unified `JobModel` schema before database insertion.

### 2.2 Resume & Candidate Intelligence (`backend/app/resume`)
- **Secure File Handling**: Content-type checking, magic byte inspection, size limits (max 5MB), and sandbox text extraction using `pypdf`.
- **Extraction Separation**: Clear demarcation between explicitly stated skills (verified keywords in resume) and inferred domains (suggested by project context), marked with `is_explicit: bool`.
- **Editable Model**: The parsed candidate profile is fully editable via API before being locked into the matching vector space.

### 2.3 Hybrid Retrieval & Score Fusion (`backend/app/retrieval`)
- **Vector Search**: Embeddings generated using `all-MiniLM-L6-v2` (384-dimensional dense vectors) cached locally for lightning-fast inference without external API quota issues.
- **Keyword Search**: BM25 / PostgreSQL full-text search token matching over title, requirements, description, and tags.
- **Fusion**: Reciprocal Rank Fusion (RRF) combined with customizable linear score weighting:
  $$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{dense}} + (1 - \alpha) \cdot \text{Score}_{\text{sparse}}$$
- **Filtering**: Pre-retrieval metadata filtering on remote status, experience level, salary range, and job location.

### 2.4 Multi-Signal Explainable Ranking (`backend/app/ranking`)
- Avoids opaque "black-box" scores. The composite match score is broken down into 5 explainable components:
  1. **Semantic Relevance** (Dense profile-to-job similarity)
  2. **Skill Overlap** (Explicit required vs possessed skills)
  3. **Experience Compatibility** (Years / seniority alignment)
  4. **Education Fit** (Degree requirement compliance)
  5. **Preference Alignment** (Remote, location, job type matches)
- Generates evidence-based explanations: "Strong match: Python, FastApi", "Missing evidence: Kubernetes", "Bonus: Remote".

### 2.5 Agentic Workflows & Tools (`backend/app/agent`)
- Dedicated orchestrator with 14 approved tools:
  - `search_jobs`, `retrieve_candidate_profile`, `get_job_details`, `compare_jobs`, `analyze_job_match`, `identify_skill_gaps`, `recommend_learning_priorities`, `save_job`, `update_job_status`, `retrieve_saved_jobs`, `generate_application_checklist`, `prepare_resume_customization_suggestions`, `generate_interview_questions`, `summarize_job_search`.
- Safety: No arbitrary code execution or unvetted SQL queries. All interactions go through typed Pydantic tool contracts.
- Traceability: Agent execution produces structured step traces and final answer objects.

### 2.6 Evaluation Lab (`backend/app/evaluation`)
- Implements IR metrics: Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (NDCG@K).
- Compares Keyword vs Dense Vector vs Hybrid vs Hybrid + Reranking over a reproducible test benchmark.
- Tests RAG groundedness and citation fidelity.
- Exposes an interactive Evaluation Lab in the UI.

### 2.7 Security & Defensive Engineering
- Prompt injection protection: Job descriptions and resumes are treated as untrusted user data and enclosed in isolated XML/markdown tags with strict instructions that prevent prompt hijacking.
- Secure JWT authentication with bcrypt password hashing.
- File upload sandbox: Restricted extensions (.pdf, .txt, .docx), path traversal prevention (`secure_filename`).
