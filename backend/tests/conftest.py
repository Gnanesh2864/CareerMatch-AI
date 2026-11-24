import pytest
from fastapi.testclient import TestClient
from app.main import app, initialize_database_data
from app.database import SessionLocal

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    initialize_database_data()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
