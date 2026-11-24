from typing import List, Dict, Any

# Curated, reproducible evaluation dataset with explicit ground truth relevance labels
BENCHMARK_DATASET = [
    {
        "query_id": "q1",
        "query_text": "Remote machine learning jobs using PyTorch and NLP",
        "target_titles": ["Machine Learning Engineer — NLP & Retrieval", "Senior AI Systems Engineer"],
        "graded_relevance": {
            "Machine Learning Engineer — NLP & Retrieval": 3,
            "Senior AI Systems Engineer": 3,
            "AI Application Engineer (Agent Workflows & RAG)": 2,
            "AI Research Scientist — Computer Vision & Multimodal": 1,
        }
    },
    {
        "query_id": "q2",
        "query_text": "Backend software engineer FastAPI PostgreSQL distributed systems",
        "target_titles": ["Backend Software Engineer (FastAPI / Distributed Systems)", "Senior AI Systems Engineer"],
        "graded_relevance": {
            "Backend Software Engineer (FastAPI / Distributed Systems)": 3,
            "Senior AI Systems Engineer": 2,
            "Junior Full Stack Engineer (React & Python)": 1,
        }
    },
    {
        "query_id": "q3",
        "query_text": "Junior entry level full stack engineer React Python",
        "target_titles": ["Junior Full Stack Engineer (React & Python)"],
        "graded_relevance": {
            "Junior Full Stack Engineer (React & Python)": 3,
            "Lead Frontend Architect (React / TypeScript)": 1,
            "Machine Learning Intern — Summer 2026": 1,
        }
    },
    {
        "query_id": "q4",
        "query_text": "DevOps Kubernetes Docker infrastructure cloud platform",
        "target_titles": ["DevOps & MLOps Platform Engineer"],
        "graded_relevance": {
            "DevOps & MLOps Platform Engineer": 3,
            "Backend Software Engineer (FastAPI / Distributed Systems)": 2,
            "Senior AI Systems Engineer": 1,
        }
    },
    {
        "query_id": "q5",
        "query_text": "Computer vision research scientist multimodal deep learning",
        "target_titles": ["AI Research Scientist — Computer Vision & Multimodal"],
        "graded_relevance": {
            "AI Research Scientist — Computer Vision & Multimodal": 3,
            "Machine Learning Intern — Summer 2026": 2,
            "Senior AI Systems Engineer": 1,
        }
    }
]
