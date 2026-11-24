import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_auth_login(client: TestClient):
    resp = client.post("/api/v1/auth/login", json={
        "email": "demo@careermatch.ai",
        "password": "DemoPassword123!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "demo@careermatch.ai"

def test_list_jobs(client: TestClient):
    resp = client.get("/api/v1/jobs")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) >= 10
    assert "title" in jobs[0]
    assert "company" in jobs[0]
    assert "skills" in jobs[0]

def test_get_job_detail(client: TestClient):
    resp = client.get("/api/v1/jobs/1")
    assert resp.status_code == 200
    job = resp.json()
    assert job["id"] == 1
    assert "responsibilities" in job

def test_candidate_profile(client: TestClient):
    resp = client.get("/api/v1/resume/profile")
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["full_name"] == "Alex Chen"
    assert len(profile["skills"]) > 0

def test_hybrid_search(client: TestClient):
    # Search with hybrid fusion
    resp = client.post("/api/v1/search/hybrid", json={
        "query_text": "PyTorch NLP machine learning",
        "alpha": 0.6,
        "top_k": 5,
        "rerank": True
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_matches"] > 0
    top_result = data["results"][0]
    assert "job" in top_result
    assert "match" in top_result
    assert top_result["match"]["composite_score"] > 0
    assert len(top_result["match"]["matched_skills"]) > 0

def test_match_breakdown(client: TestClient):
    resp = client.get("/api/v1/search/match/1")
    assert resp.status_code == 200
    match = resp.json()
    assert "composite_score" in match
    assert "matched_skills" in match
    assert "explanation_summary" in match

def test_rag_assistant_chat(client: TestClient):
    resp = client.post("/api/v1/agent/chat", json={
        "message": "Why is this job relevant to me and what are the main skill gaps?",
        "context_job_id": 1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) > 0

def test_agent_multistep_workflow(client: TestClient):
    resp = client.post("/api/v1/agent/run", json={
        "message": "Find the top jobs for my profile and rank them"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["steps"]) >= 2
    assert "retrieve_candidate_profile" in data["tools_used"]
    assert "search_jobs" in data["tools_used"]
    assert len(data["response"]) > 50

def test_skill_gap_analysis(client: TestClient):
    resp = client.get("/api/v1/skills/gap-analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert "demonstrated_skills" in data
    assert "high_priority_gaps" in data
    assert "roadmap" in data
    assert len(data["roadmap"]) > 0

def test_tracker_save_and_update(client: TestClient):
    # 1. Save job 2
    save_resp = client.post("/api/v1/tracker/2?status=saved")
    assert save_resp.status_code == 200

    # 2. Update status to applied
    up_resp = client.put("/api/v1/tracker/2/status", json={
        "status": "applied",
        "notes": "Applied via referral"
    })
    assert up_resp.status_code == 200

    # 3. Check analytics
    analytics_resp = client.get("/api/v1/tracker/analytics")
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert analytics["total_tracked"] >= 1
    assert analytics["status_funnel"]["applied"] >= 1

def test_evaluation_lab_benchmark(client: TestClient):
    resp = client.post("/api/v1/evaluation/run?k=3")
    assert resp.status_code == 200
    report = resp.json()
    assert "retrieval_comparison" in report
    assert "rag_metrics" in report
    assert "agent_metrics" in report
    assert report["retrieval_comparison"]["hybrid_rerank"]["ndcg_at_k"] > 0
