import sys
from pathlib import Path
import pytest
from datetime import datetime, UTC
from uuid import uuid4
import logging
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.database import User, DatabaseConfig, DatabaseEnvironment, Base
from app.main import app
from app.database.base import SessionLocal

# Test data constants
TEST_USER_DATA = {
    "email": "test@example.com",
    "full_name": "Test User",
    "google_id": "test123",
    "picture": "https://example.com/picture.jpg",
}

class TestDatabaseManager:
    @staticmethod
    def clear_tables(session: Session) -> None:
        """Clear all tables in reverse order"""
        try:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error clearing tables: {str(e)}")
            session.rollback()

@pytest.fixture(scope="session")
def test_config() -> DatabaseConfig:
    """Create test database configuration"""
    config = DatabaseConfig(env=DatabaseEnvironment.TESTING)
    logger.info(f"Initialized test config with URL: {config.get_masked_url()}")
    return config

@pytest.fixture(scope="session")
def test_db_setup(test_config: DatabaseConfig) -> Generator[None, None, None]:
    """Setup test database before tests and cleanup after"""
    try:
        # Create database
        if not test_config.create_database():
            pytest.fail("Failed to create test database")
        
        # Create tables
        engine = test_config._get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Created all tables in test database")
        
        # Verify connection
        if not test_config.verify_connection():
            pytest.fail("Failed to verify database connection")
            
        yield
        
    except SQLAlchemyError as e:
        logger.error(f"Test database setup failed: {str(e)}")
        pytest.fail(str(e))
    finally:
        # Cleanup
        try:
            engine = test_config._get_engine(with_database=False)
            with engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS {test_config.credentials.database}"))
            logger.info("Test database cleanup completed")
        except SQLAlchemyError as e:
            logger.error(f"Failed to cleanup test database: {str(e)}")

@pytest.fixture
def test_db(test_db_setup, test_config: DatabaseConfig) -> Generator[Session, None, None]:
    """Provide test database session with automatic cleanup"""
    engine = test_config._get_engine()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # Ensure any failed transaction is rolled back
        TestDatabaseManager.clear_tables(session)
        session.close()

@pytest.fixture
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with a clean database session."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[SessionLocal] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_health_check(client: TestClient) -> None:
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert json_response["database"] == "connected"

def test_invalid_token(client: TestClient) -> None:
    """Test invalid authentication token handling"""
    response = client.post(
        "/api/auth/google/callback",  # Updated path
        json={"token": "invalid_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_user_model(test_db: Session) -> None:
    """Test User model CRUD operations"""
    try:
        # Create test user with all required fields
        test_user = User(
            user_id=uuid4(),
            email=TEST_USER_DATA["email"],  # Ensure email is provided
            full_name=TEST_USER_DATA["full_name"],
            google_id=TEST_USER_DATA["google_id"],
            picture=TEST_USER_DATA["picture"],
            is_active=True,
            created_at=datetime.now(UTC),
            last_login=datetime.now(UTC)
        )
        
        test_db.add(test_user)
        test_db.commit()
        test_db.refresh(test_user)
        
        # Query and verify
        queried_user = test_db.query(User).filter(User.email == TEST_USER_DATA["email"]).first()
        assert queried_user is not None
        assert queried_user.email == TEST_USER_DATA["email"]
        assert queried_user.full_name == TEST_USER_DATA["full_name"]
        assert queried_user.google_id == TEST_USER_DATA["google_id"]
        assert queried_user.is_active is True
        
    except IntegrityError as e:
        test_db.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        pytest.fail(str(e))
    except SQLAlchemyError as e:
        test_db.rollback()
        logger.error(f"Database error: {str(e)}")
        pytest.fail(str(e))

def test_user_model_validation(test_db: Session) -> None:
    """Test User model validation rules"""
    try:
        with pytest.raises(IntegrityError):
            invalid_user = User(
                user_id=uuid4(),
                # email intentionally omitted to test validation
                full_name=TEST_USER_DATA["full_name"],
                google_id=TEST_USER_DATA["google_id"],
                is_active=True,
                created_at=datetime.now(UTC),
                last_login=datetime.now(UTC)
            )
            test_db.add(invalid_user)
            test_db.commit()
    finally:
        test_db.rollback()  # Ensure cleanup after expected failure

if __name__ == "__main__":
    pytest.main([__file__, "-v"])