# CareerMatch AI — Development Guide

## Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+ (tested on Node 26)
- **Docker & Docker Compose** (optional for containerized deployment with PostgreSQL + pgvector)

## Local Quickstart

### 1. Backend Setup
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The React SPA will be available at: `http://localhost:5173`

### 3. Docker Deployment
```bash
docker compose up --build
```
This spins up:
- PostgreSQL 16 with pgvector extension enabled on port 5432
- FastAPI backend on port 8000
- React frontend (served via Nginx) on port 3000

## Environment Variables
See `.env.example` in the project root for configuration options:
- `DATABASE_URL`: PostgreSQL connection string (defaults to SQLite fallback if Postgres is absent)
- `JWT_SECRET_KEY`: Secret string for token signing
- `EMBEDDING_MODEL_NAME`: HuggingFace embedding model (`all-MiniLM-L6-v2`)
- `GEMINI_API_KEY`: Optional Google Gemini API key for external LLM generation
- `OPENAI_API_KEY`: Optional OpenAI API key

## Running Tests
```bash
# Backend unit & integration tests
cd backend
source .venv/bin/activate
pytest tests/ -v

# Frontend build & type check
cd frontend
npm run build
```
