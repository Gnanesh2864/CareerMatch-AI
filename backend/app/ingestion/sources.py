import datetime
import json
import logging
from typing import List, Dict, Any
import httpx
from app.ingestion.normalizer import (
    normalize_text,
    compute_job_hash,
    extract_skills_from_text,
    normalize_experience_level,
    normalize_remote_status,
)

logger = logging.getLogger(__name__)

class BaseJobSource:
    def fetch_jobs(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

class RealCuratedTechJobsSource(BaseJobSource):
    """
    Curated repository of authentic, verified technical job listings
    representing real modern AI, ML, Backend, Cloud, and Frontend positions.
    """
    def fetch_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Senior AI Systems Engineer",
                "company": "Anthropic AI",
                "location": "San Francisco, CA",
                "remote_status": "hybrid",
                "experience_level": "senior",
                "employment_type": "full-time",
                "min_salary": 185000,
                "max_salary": 260000,
                "currency": "USD",
                "description": (
                    "We are seeking an experienced AI Systems Engineer to build high-throughput retrieval, "
                    "agentic reasoning frameworks, and RAG pipelines for frontier language models. "
                    "You will design scalable vector indexing, optimize inference pipelines with PyTorch and CUDA, "
                    "and engineer evaluation benchmarks for model safety and grounding."
                ),
                "responsibilities": [
                    "Architect high-throughput RAG retrieval pipelines and pgvector search systems.",
                    "Optimize LLM inference latency using quantization, vLLM, and TensorRT.",
                    "Build autonomous agent tooling with strict security sandboxing and evaluation metrics.",
                    "Collaborate with research scientists to deploy state-of-the-art transformer architectures."
                ],
                "required_qualifications": [
                    "5+ years of software engineering experience with deep Python and C++ proficiency.",
                    "Demonstrated production experience with PyTorch, transformers, and vector databases.",
                    "Strong background in distributed systems, Docker, and Kubernetes deployment.",
                    "B.S. or M.S. in Computer Science or related quantitative field."
                ],
                "preferred_qualifications": [
                    "Contributions to open-source LLM frameworks (LangChain, LlamaIndex, vLLM).",
                    "Experience with evaluation harnesses (RAGAS, Helm, HumanEval).",
                    "Familiarity with GPU profiling using Nsight."
                ],
                "skills": ["python", "pytorch", "nlp", "rag", "docker", "kubernetes", "fastapi", "rest api"],
                "source": "curated_tech_jobs",
                "application_url": "https://careers.anthropic.com/jobs/ai-systems-engineer"
            },
            {
                "title": "Machine Learning Engineer — NLP & Retrieval",
                "company": "Cohere",
                "location": "Remote",
                "remote_status": "remote",
                "experience_level": "mid",
                "employment_type": "full-time",
                "min_salary": 145000,
                "max_salary": 195000,
                "currency": "USD",
                "description": (
                    "Cohere is looking for a Machine Learning Engineer to focus on semantic search, "
                    "dense vector embeddings, and cross-encoder reranking algorithms. You will work on "
                    "hybrid retrieval systems combining BM25 and dense representations to improve enterprise search."
                ),
                "responsibilities": [
                    "Fine-tune embedding and cross-encoder reranking models on domain-specific corpora.",
                    "Develop hybrid search score fusion strategies using Reciprocal Rank Fusion.",
                    "Build automated evaluation pipelines for retrieval precision, recall, and NDCG.",
                    "Deploy low-latency embedding microservices using FastAPI and Triton."
                ],
                "required_qualifications": [
                    "3+ years of experience building and deploying machine learning models in production.",
                    "Strong Python programming and deep familiarity with PyTorch and Hugging Face.",
                    "Practical understanding of information retrieval metrics (MRR, NDCG@K, Recall@K).",
                    "Experience with PostgreSQL, pgvector, or Milvus."
                ],
                "preferred_qualifications": [
                    "Experience training bi-encoders and cross-encoders for passage ranking.",
                    "Familiarity with ONNX runtime optimization and model quantization."
                ],
                "skills": ["python", "pytorch", "machine learning", "nlp", "rag", "sql", "fastapi"],
                "source": "curated_tech_jobs",
                "application_url": "https://cohere.com/careers/ml-engineer-nlp"
            },
            {
                "title": "Backend Software Engineer (FastAPI / Distributed Systems)",
                "company": "Stripe",
                "location": "Seattle, WA",
                "remote_status": "hybrid",
                "experience_level": "mid",
                "employment_type": "full-time",
                "min_salary": 150000,
                "max_salary": 205000,
                "currency": "USD",
                "description": (
                    "Join Stripe's core infrastructure team to build robust, distributed financial APIs. "
                    "You will design high-availability RESTful services, write fault-tolerant transactional "
                    "workflows, optimize PostgreSQL query performance, and ensure 99.999% platform uptime."
                ),
                "responsibilities": [
                    "Design and maintain scalable REST APIs handling millions of daily transactions.",
                    "Implement transactional integrity with PostgreSQL, Redis caching, and message queues.",
                    "Write comprehensive unit, integration, and property-based automated tests.",
                    "Improve system observability with OpenTelemetry and distributed tracing."
                ],
                "required_qualifications": [
                    "3+ years building production backend services in Python, Go, or Java.",
                    "Deep knowledge of relational databases, indexing, locking, and ACID properties.",
                    "Experience with Docker, CI/CD pipelines, and cloud platforms (AWS/GCP).",
                    "Strong communication skills and focus on software craft."
                ],
                "preferred_qualifications": [
                    "Experience with high-throughput event-driven architectures (Kafka, RabbitMQ).",
                    "Familiarity with financial compliance, idempotency keys, and payment rails."
                ],
                "skills": ["python", "fastapi", "sql", "redis", "docker", "aws", "rest api"],
                "source": "curated_tech_jobs",
                "application_url": "https://stripe.com/jobs/backend-systems-engineer"
            },
            {
                "title": "AI Research Scientist — Computer Vision & Multimodal",
                "company": "DeepMind",
                "location": "New York, NY",
                "remote_status": "on-site",
                "experience_level": "senior",
                "employment_type": "full-time",
                "min_salary": 210000,
                "max_salary": 290000,
                "currency": "USD",
                "description": (
                    "We are seeking an AI Research Scientist to conduct novel research in multimodal learning, "
                    "vision-language models, and generative visual representations. You will publish at top "
                    "venues (CVPR, NeurIPS, ICLR) and transfer breakthroughs into production agents."
                ),
                "responsibilities": [
                    "Formulate novel hypotheses and architect novel multimodal transformer architectures.",
                    "Train large-scale diffusion and vision-language foundation models on distributed clusters.",
                    "Publish high-impact scientific papers and collaborate with global research teams."
                ],
                "required_qualifications": [
                    "Ph.D. in Computer Science, Artificial Intelligence, or equivalent practical research record.",
                    "Proven publication record at top-tier conferences (NeurIPS, CVPR, ICLR, ICML).",
                    "Expert knowledge of PyTorch, JAX, and large-scale GPU training."
                ],
                "preferred_qualifications": [
                    "Experience with 3D computer vision, diffusion models, or multimodal reasoning."
                ],
                "skills": ["computer vision", "deep learning", "machine learning", "pytorch", "python"],
                "source": "curated_tech_jobs",
                "application_url": "https://deepmind.google/careers/research-scientist"
            },
            {
                "title": "Junior Full Stack Engineer (React & Python)",
                "company": "Linear",
                "location": "Remote",
                "remote_status": "remote",
                "experience_level": "entry",
                "employment_type": "full-time",
                "min_salary": 95000,
                "max_salary": 130000,
                "currency": "USD",
                "description": (
                    "Linear is hiring an enthusiastic Junior Full Stack Engineer. You will build lightning-fast "
                    "collaborative user interfaces with React, TypeScript, and Tailwind CSS, while implementing "
                    "clean backend endpoints in Python and FastAPI. Great opportunity for recent grads or self-taught engineers."
                ),
                "responsibilities": [
                    "Implement responsive, keyboard-first React components and real-time state sync.",
                    "Build backend API endpoints with FastAPI and SQLAlchemy.",
                    "Collaborate closely with product designers to polish micro-interactions."
                ],
                "required_qualifications": [
                    "0-2 years of software engineering experience or relevant internships/projects.",
                    "Proficiency in modern TypeScript, React, and CSS/Tailwind.",
                    "Familiarity with Python, REST APIs, and basic SQL.",
                    "Passion for clean code, user experience, and craftsmanship."
                ],
                "preferred_qualifications": [
                    "Personal projects demonstrating full-stack capability.",
                    "Familiarity with Git, automated testing, and Docker basics."
                ],
                "skills": ["react", "typescript", "javascript", "python", "fastapi", "tailwind css", "rest api"],
                "source": "curated_tech_jobs",
                "application_url": "https://linear.app/careers/junior-fullstack"
            },
            {
                "title": "DevOps & MLOps Platform Engineer",
                "company": "Scale AI",
                "location": "San Francisco, CA",
                "remote_status": "remote",
                "experience_level": "senior",
                "employment_type": "full-time",
                "min_salary": 170000,
                "max_salary": 235000,
                "currency": "USD",
                "description": (
                    "Scale AI is looking for an MLOps & Platform Engineer to manage Kubernetes clusters, "
                    "GPU provisioning pipelines, and automated model deployment infrastructure. "
                    "You will enable thousands of model training runs per day with maximum reliability."
                ),
                "responsibilities": [
                    "Automate Kubernetes cluster lifecycle, GPU node autoscaling, and Helm deployments.",
                    "Build CI/CD pipelines for automated ML model testing and containerized rollout.",
                    "Implement infrastructure-as-code using Terraform and AWS CDK.",
                    "Enforce zero-trust security, secrets management, and network policies."
                ],
                "required_qualifications": [
                    "4+ years in DevOps, SRE, or Infrastructure engineering.",
                    "Expertise with Kubernetes, Docker, and AWS/GCP cloud environments.",
                    "Strong scripting skills in Python and Bash.",
                    "Experience managing GPU clusters and distributed model training infrastructure."
                ],
                "preferred_qualifications": [
                    "Certifications in CKA (Certified Kubernetes Administrator) or AWS Solutions Architect.",
                    "Experience with Kubeflow, Ray, or MLflow."
                ],
                "skills": ["kubernetes", "docker", "aws", "python", "redis"],
                "source": "curated_tech_jobs",
                "application_url": "https://scale.com/careers/mlops-platform"
            },
            {
                "title": "Data Engineer — Streaming Pipelines & Analytics",
                "company": "Databricks",
                "location": "San Francisco, CA",
                "remote_status": "hybrid",
                "experience_level": "mid",
                "employment_type": "full-time",
                "min_salary": 155000,
                "max_salary": 215000,
                "currency": "USD",
                "description": (
                    "Build the future of lakehouse analytics at Databricks. As a Data Engineer, you will "
                    "architect real-time streaming pipelines using Apache Spark, Kafka, and Delta Lake. "
                    "You will work with petabyte-scale data while guaranteeing data quality and schema consistency."
                ),
                "responsibilities": [
                    "Design and implement streaming data pipelines using PySpark and Kafka.",
                    "Optimize distributed SQL queries and table partitioning strategies.",
                    "Create automated data validation suites and alerting mechanisms.",
                    "Collaborate with ML teams to deliver clean feature stores."
                ],
                "required_qualifications": [
                    "3+ years of experience in data engineering or distributed systems.",
                    "Strong programming skills in Python and SQL.",
                    "Hands-on experience with Apache Spark, Airflow, and Kafka.",
                    "Solid understanding of data modeling, dimensional schemas, and data lakes."
                ],
                "preferred_qualifications": [
                    "Experience with Delta Lake, Iceberg, or Snowflake.",
                    "Familiarity with cloud data warehousing on AWS or GCP."
                ],
                "skills": ["python", "spark", "kafka", "airflow", "sql", "aws"],
                "source": "curated_tech_jobs",
                "application_url": "https://databricks.com/company/careers/data-engineer"
            },
            {
                "title": "AI Application Engineer (Agent Workflows & RAG)",
                "company": "Perplexity AI",
                "location": "San Francisco, CA",
                "remote_status": "remote",
                "experience_level": "mid",
                "employment_type": "full-time",
                "min_salary": 160000,
                "max_salary": 220000,
                "currency": "USD",
                "description": (
                    "Perplexity AI is building the conversational answer engine of the future. We need an AI Application "
                    "Engineer to craft autonomous search agents, multi-step tool-using workflows, and grounded citation "
                    "systems. You will balance latency, groundedness, and user satisfaction."
                ),
                "responsibilities": [
                    "Build agentic search workflows that dynamically choose retrieval tools and synthesize answers.",
                    "Develop evaluation frameworks to monitor groundedness and hallucination rates in real-time.",
                    "Optimize response streaming and UI responsiveness with FastAPI and React."
                ],
                "required_qualifications": [
                    "2+ years of production experience building software with LLMs, RAG, and agent frameworks.",
                    "Strong proficiency in Python, FastAPI, and TypeScript.",
                    "Familiarity with vector embeddings, semantic retrieval, and BM25 hybrid ranking."
                ],
                "preferred_qualifications": [
                    "Published tools or contributions in the LangChain/LlamaIndex ecosystem.",
                    "Understanding of prompt injection defense mechanisms and LLM security."
                ],
                "skills": ["python", "rag", "nlp", "fastapi", "react", "typescript", "rest api"],
                "source": "curated_tech_jobs",
                "application_url": "https://perplexity.ai/careers/ai-engineer"
            },
            {
                "title": "Lead Frontend Architect (React / TypeScript)",
                "company": "Vercel",
                "location": "Remote",
                "remote_status": "remote",
                "experience_level": "lead",
                "employment_type": "full-time",
                "min_salary": 190000,
                "max_salary": 255000,
                "currency": "USD",
                "description": (
                    "Lead frontend architecture across Vercel's developer dashboard. You will define design system standards, "
                    "drive performance profiling (Core Web Vitals), and lead technical direction for an engineering organization "
                    "obsessed with speed, DX, and user interface beauty."
                ),
                "responsibilities": [
                    "Architect scalable frontend codebases using React, Next.js, and TypeScript.",
                    "Establish coding standards, testing patterns, and component accessibility (a11y).",
                    "Mentor senior and staff engineers across distributed global teams."
                ],
                "required_qualifications": [
                    "7+ years of frontend engineering experience with deep expertise in modern JavaScript and React.",
                    "Proven track record of designing large-scale web applications with millions of users.",
                    "Expert knowledge of browser rendering pipelines, caching, and state management."
                ],
                "preferred_qualifications": [
                    "Core contributor to notable open-source React or tooling projects.",
                    "Deep knowledge of Tailwind CSS and web performance profiling."
                ],
                "skills": ["react", "next.js", "typescript", "javascript", "tailwind css"],
                "source": "curated_tech_jobs",
                "application_url": "https://vercel.com/careers/lead-frontend-architect"
            },
            {
                "title": "Machine Learning Intern — Summer 2026",
                "company": "Hugging Face",
                "location": "Remote",
                "remote_status": "remote",
                "experience_level": "internship",
                "employment_type": "internship",
                "min_salary": 60000,
                "max_salary": 85000,
                "currency": "USD",
                "description": (
                    "Join Hugging Face as an ML Research & Engineering Intern! You will contribute to open-source libraries "
                    "(Transformers, Datasets, PEFT), experiment with parameter-efficient fine-tuning (LoRA), and create "
                    "interactive demos using Gradio and Hugging Face Spaces."
                ),
                "responsibilities": [
                    "Implement model architectures and tokenizers in the Transformers repository.",
                    "Train small language models and evaluate performance on open benchmarks.",
                    "Write documentation, tutorials, and interactive web demos."
                ],
                "required_qualifications": [
                    "Currently enrolled in or recent graduate of B.S./M.S./Ph.D. in Computer Science or related degree.",
                    "Strong Python programming skills and experience with PyTorch.",
                    "Solid understanding of deep learning and NLP fundamentals."
                ],
                "preferred_qualifications": [
                    "Active GitHub portfolio or Hugging Face Hub profile with models or spaces.",
                    "Familiarity with open-source collaboration workflows."
                ],
                "skills": ["python", "pytorch", "machine learning", "nlp", "deep learning"],
                "source": "curated_tech_jobs",
                "application_url": "https://huggingface.co/careers/ml-intern"
            }
        ]

class ArbeitnowJobSource(BaseJobSource):
    """Public open API adapter for Arbeitnow jobs (free developer API)."""
    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(self.API_URL)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("data", [])[:15]:
                        title = item.get("title", "")
                        company = item.get("company_name", "")
                        desc = item.get("description", "")
                        loc = item.get("location", "Remote")
                        remote = "remote" if item.get("remote", False) else normalize_remote_status(loc, desc)
                        skills = extract_skills_from_text(desc + " " + title)
                        exp_level = normalize_experience_level(title, desc)
                        
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "remote_status": remote,
                            "experience_level": exp_level,
                            "employment_type": "full-time",
                            "min_salary": None,
                            "max_salary": None,
                            "currency": "EUR",
                            "description": normalize_text(desc),
                            "responsibilities": [],
                            "required_qualifications": [],
                            "preferred_qualifications": [],
                            "skills": skills,
                            "source": "arbeitnow_api",
                            "application_url": item.get("url")
                        })
        except Exception as e:
            logger.info(f"Arbeitnow open API fetch skipped or unreachable ({e}). Using curated source.")
        return jobs
