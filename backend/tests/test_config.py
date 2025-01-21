# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.db_config import db_config
from app.main import app
from fastapi.testclient import TestClient

# Test database URL
TEST_DATABASE_URL = db_config.DATABASE_URL + "_test"

@pytest.fixture(scope="session")
def engine():
    """Create engine for test database"""
    engine = create_engine(TEST_DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    """Create session factory for test database"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

@pytest.fixture
def db(TestingSessionLocal):
    """Get database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)