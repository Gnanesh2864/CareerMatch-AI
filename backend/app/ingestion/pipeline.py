import datetime
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.job import Job
from app.ingestion.normalizer import (
    normalize_text,
    compute_job_hash,
    extract_skills_from_text,
    normalize_experience_level,
    normalize_remote_status,
)
from app.ingestion.sources import RealCuratedTechJobsSource, ArbeitnowJobSource
from app.embeddings.embedder import embedding_service

logger = logging.getLogger(__name__)

class JobIngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.sources = [
            RealCuratedTechJobsSource(),
            ArbeitnowJobSource(),
        ]

    def run(self) -> Dict[str, Any]:
        """Runs the complete ingestion pipeline across all configured sources."""
        stats = {
            "fetched": 0,
            "inserted": 0,
            "duplicates_skipped": 0,
            "errors": 0,
        }

        all_raw_jobs: List[Dict[str, Any]] = []
        for src in self.sources:
            try:
                jobs = src.fetch_jobs()
                all_raw_jobs.extend(jobs)
                stats["fetched"] += len(jobs)
            except Exception as e:
                logger.error(f"Error fetching from {src.__class__.__name__}: {e}")
                stats["errors"] += 1

        for raw in all_raw_jobs:
            try:
                res = self.ingest_single_job(raw)
                if res == "inserted":
                    stats["inserted"] += 1
                elif res == "skipped":
                    stats["duplicates_skipped"] += 1
            except Exception as e:
                logger.error(f"Error ingesting job {raw.get('title')}: {e}")
                stats["errors"] += 1

        return stats

    def ingest_single_job(self, data: Dict[str, Any]) -> str:
        """Processes, validates, embeds, and stores a single job listing."""
        title = normalize_text(data.get("title", ""))
        company = normalize_text(data.get("company", ""))
        location = normalize_text(data.get("location", "Remote"))
        if not title or not company:
            return "error"

        content_hash = compute_job_hash(company, title, location)

        # Check for existing duplicate
        existing = self.db.query(Job).filter(Job.content_hash == content_hash).first()
        if existing:
            return "skipped"

        desc = normalize_text(data.get("description", ""))
        skills = data.get("skills") or extract_skills_from_text(desc + " " + title)
        exp_level = data.get("experience_level") or normalize_experience_level(title, desc)
        remote_status = data.get("remote_status") or normalize_remote_status(location, desc)

        # Prepare text representation for dense embedding
        embed_text = f"{title} at {company}. {location}. {exp_level} level. Skills: {', '.join(skills)}. {desc[:500]}"
        embedding_vector = embedding_service.embed_text(embed_text)

        new_job = Job(
            title=title,
            company=company,
            description=desc,
            responsibilities_json=json.dumps(data.get("responsibilities", [])),
            required_qualifications_json=json.dumps(data.get("required_qualifications", [])),
            preferred_qualifications_json=json.dumps(data.get("preferred_qualifications", [])),
            skills_json=json.dumps(skills),
            experience_level=exp_level,
            employment_type=data.get("employment_type", "full-time"),
            min_salary=data.get("min_salary"),
            max_salary=data.get("max_salary"),
            currency=data.get("currency", "USD"),
            location=location,
            remote_status=remote_status,
            application_url=data.get("application_url"),
            source=data.get("source", "ingestion_pipeline"),
            posting_date=datetime.datetime.utcnow(),
            content_hash=content_hash,
            embedding_json=json.dumps(embedding_vector),
        )

        self.db.add(new_job)
        self.db.commit()
        return "inserted"
