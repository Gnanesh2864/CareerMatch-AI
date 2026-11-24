import hashlib
import re
from typing import Dict, Any, List, Optional

# Standard technical skill taxonomy for normalization
SKILL_TAXONOMY = {
    # Languages
    "python": ["python", "py", "python3"],
    "typescript": ["typescript", "ts"],
    "javascript": ["javascript", "js", "ecmascript"],
    "go": ["golang", "go"],
    "rust": ["rust"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "sql": ["sql", "postgresql", "postgres", "mysql"],

    # AI & ML
    "machine learning": ["machine learning", "ml", "statistical learning"],
    "deep learning": ["deep learning", "dl", "neural networks"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    "nlp": ["nlp", "natural language processing", "llm", "large language models", "transformers"],
    "rag": ["rag", "retrieval augmented generation", "vector search", "pgvector"],
    "computer vision": ["computer vision", "cv", "opencv"],
    "langchain": ["langchain", "llamaindex"],

    # Backend & Distributed Systems
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "node.js": ["node", "nodejs", "node.js", "express"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "s3", "ec2"],
    "gcp": ["gcp", "google cloud"],
    "redis": ["redis", "caching"],
    "graphql": ["graphql"],
    "rest api": ["rest", "restful", "rest api", "microservices"],

    # Frontend
    "react": ["react", "reactjs", "react.js"],
    "next.js": ["nextjs", "next.js"],
    "tailwind css": ["tailwind", "tailwindcss"],
    "vue": ["vue", "vuejs"],

    # Data Engineering
    "spark": ["spark", "pyspark", "apache spark"],
    "kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
}

def compute_job_hash(company: str, title: str, location: str) -> str:
    raw = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Strip HTML tags if present
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills_from_text(text: str) -> List[str]:
    lower_text = " " + text.lower() + " "
    matched_skills = set()

    for canonical_name, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            # Word boundary pattern
            pattern = r'(?<![a-zA-Z0-9_#+])' + re.escape(alias) + r'(?![a-zA-Z0-9_#+])'
            if re.search(pattern, lower_text):
                matched_skills.add(canonical_name)
                break

    return sorted(list(matched_skills))

def normalize_experience_level(title: str, text: str) -> str:
    combined = (title + " " + text).lower()
    if any(k in combined for k in ["intern", "internship"]):
        return "internship"
    if any(k in combined for k in ["junior", "entry level", "new grad", "associate", "0-2 years", "entry"]):
        return "entry"
    if any(k in combined for k in ["staff", "principal", "director", "head of", "vp"]):
        return "lead"
    if any(k in combined for k in ["senior", "sr.", "sr ", "lead", "5+ years", "6+ years", "7+ years"]):
        return "senior"
    return "mid"

def normalize_remote_status(location: str, description: str) -> str:
    combined = (location + " " + description[:300]).lower()
    if "remote" in combined or "anywhere" in combined or "work from home" in combined:
        return "remote"
    if "hybrid" in combined or "flexible" in combined:
        return "hybrid"
    return "on-site"
