import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session
from app.models.job import Job
from app.retrieval.bm25 import BM25Retriever
from app.embeddings.embedder import embedding_service

logger = logging.getLogger(__name__)

class HybridRetriever:
    def __init__(self, db: Session):
        self.db = db

    def retrieve(
        self,
        query_text: str,
        query_embedding: Optional[List[float]] = None,
        alpha: float = 0.6,
        top_k: int = 15,
        remote_status: Optional[str] = None,
        experience_level: Optional[str] = None,
        location: Optional[str] = None,
        min_salary: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid retrieval combining dense vector similarity and BM25 sparse matching.
        alpha = 1.0 (pure semantic), alpha = 0.0 (pure keyword), alpha = 0.5 (balanced hybrid).
        """
        # 1. Fetch filtered candidate jobs from database
        query_builder = self.db.query(Job)
        if remote_status and remote_status != "all":
            query_builder = query_builder.filter(Job.remote_status == remote_status.lower())
        if experience_level and experience_level != "all":
            query_builder = query_builder.filter(Job.experience_level == experience_level.lower())
        if min_salary:
            query_builder = query_builder.filter((Job.max_salary >= min_salary) | (Job.min_salary >= min_salary))

        jobs: List[Job] = query_builder.all()
        if not jobs:
            return []

        # If location filter provided, filter in-memory with case-insensitive matching
        if location and location.lower() != "all":
            loc_lower = location.lower()
            jobs = [j for j in jobs if loc_lower in j.location.lower() or loc_lower in j.remote_status.lower()]

        if not jobs:
            return []

        # 2. Compute Dense Vector Scores
        if query_embedding is None and query_text:
            query_embedding = embedding_service.embed_text(query_text)

        dense_scores: Dict[int, float] = {}
        if query_embedding is not None:
            for job in jobs:
                if job.embedding_json:
                    try:
                        job_vec = json.loads(job.embedding_json)
                        sim = embedding_service.cosine_similarity(query_embedding, job_vec)
                        # Cosine similarity is in [-1, 1], normalize to [0, 1]
                        dense_scores[job.id] = max(0.0, float((sim + 1.0) / 2.0))
                    except Exception:
                        dense_scores[job.id] = 0.0
                else:
                    dense_scores[job.id] = 0.0
        else:
            for job in jobs:
                dense_scores[job.id] = 0.0

        # 3. Compute Sparse BM25 Scores
        sparse_scores: Dict[int, float] = {}
        if query_text:
            job_dicts = []
            for j in jobs:
                skills_list = json.loads(j.skills_json) if j.skills_json else []
                job_dicts.append({
                    "id": j.id,
                    "title": j.title,
                    "company": j.company,
                    "description": j.description,
                    "skills": " ".join(skills_list),
                    "location": j.location,
                })
            
            bm25 = BM25Retriever()
            bm25.index_documents(job_dicts, text_fields=["title", "company", "description", "skills", "location"])
            raw_bm25 = bm25.score(query_text)
            
            # Normalize BM25 scores to [0, 1]
            max_bm25 = max([s for _, s in raw_bm25], default=1.0)
            if max_bm25 <= 0.0:
                max_bm25 = 1.0
            for idx, raw_score in raw_bm25:
                job_id = job_dicts[idx]["id"]
                sparse_scores[job_id] = float(raw_score / max_bm25)
        else:
            for job in jobs:
                sparse_scores[job.id] = 0.0

        # 4. Score Fusion (Linear Combination + Reciprocal Rank Fusion)
        results = []
        for job in jobs:
            s_dense = dense_scores.get(job.id, 0.0)
            s_sparse = sparse_scores.get(job.id, 0.0)

            # Combined hybrid score
            hybrid_score = (alpha * s_dense) + ((1.0 - alpha) * s_sparse)

            results.append({
                "job": job,
                "dense_score": s_dense,
                "sparse_score": s_sparse,
                "hybrid_score": hybrid_score,
            })

        # Sort descending by hybrid_score
        results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return results[:top_k]
