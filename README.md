# CareerMatch AI 🎯

> **A Production-Grade AI Career Intelligence & Job Matching Platform**  
> Built with FastAPI, React, TypeScript, Tailwind CSS, pgvector / dense semantic retrieval, hybrid search (BM25 + Dense RRF), multi-signal explainable ranking, grounded RAG career assistant, tool-using autonomous career agents, and reproducible IR evaluation.

---

## 🚀 Key Features

1. **Intelligent Resume Ingestion & Parsing**:
   - High-fidelity extraction from PDF and plain text.
   - Demarcation between explicitly declared qualifications and inferred skill clusters.
   - User-editable structured candidate profile schema.

2. **Real Job Ingestion Pipeline**:
   - Ingestion adapters for real job datasets, open APIs, and structured JSON/CSV imports.
   - Robust content hashing for deduplication (`SHA-256(company + title + location)`).
   - Validation against strict `JobModel` schemas with salary and remote status normalization.

3. **Hybrid Search Subsystem**:
   - **Dense Semantic Retrieval**: High-dimensional semantic embeddings via `sentence-transformers/all-MiniLM-L6-v2`.
   - **Sparse Keyword Retrieval**: BM25 / Full-Text Search with keyword stemming.
   - **Reciprocal Rank Fusion (RRF)**: Merges dense and sparse result lists for superior precision and recall.

4. **Explainable Multi-Signal Ranking**:
   - Transparent scoring combining Semantic Relevance, Skill Overlap, Experience Alignment, Education Fit, and Candidate Preferences.
   - Evidence-grounded match breakdowns: explains matched skills, partial matches, missing requirements, and preference alignment.

5. **Grounded RAG Career Assistant**:
   - Context-grounded generation backed by candidate profile and retrieved job postings.
   - Built-in defenses against prompt injection in untrusted job descriptions.
   - Evidence citations linking back to original job listings.

6. **Autonomous Tool-Using Career Agent**:
   - 14 specialized career tools (`search_jobs`, `analyze_job_match`, `identify_skill_gaps`, `generate_application_checklist`, `compare_jobs`, etc.).
   - Multi-step workflow orchestration with execution traces and guardrails against hallucinated actions.

7. **Skill Gap Intelligence & Roadmap**:
   - Categorizes skills into Demonstrated, Weak Evidence, Missing, High-Priority, and Optional.
   - Generates actionable learning roadmaps grounded in real market requirements.

8. **Application Tracker**:
   - Full lifecycle job tracking (Saved, Applied, Interview, Offer, Rejected).
   - Rich notes, application timelines, and personalized preference feedback loop.

9. **Evaluation Lab**:
   - Reproducible Information Retrieval benchmarking: Recall@K, Precision@K, MRR, NDCG@K across Keyword, Dense, Hybrid, and Reranked modes.
   - RAG groundedness metrics & Agent task completion evaluation.

---

## 🛠️ Architecture & Quickstart

See [ARCHITECTURE.md](file:///Users/gnanesh/.gemini/antigravity/scratch/careermatch-ai/ARCHITECTURE.md) for deep technical design and [DEVELOPMENT.md](file:///Users/gnanesh/.gemini/antigravity/scratch/careermatch-ai/DEVELOPMENT.md) for local run instructions.

```bash
# Run backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Run frontend
cd frontend
npm run dev
```
