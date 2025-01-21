# tests/test_auth.py
import pytest
from datetime import datetime, UTC
from uuid import uuid4
from app.database.sql_models import User
from fastapi.testclient import TestClient

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}

def test_invalid_token(client):
    response = client.post(
        "/api/auth/google/callback",
        json={"code": "invalid_code"}  # Changed from token to code
    )
    assert response.status_code == 401
    assert "error" in response.json()

def test_user_model(db):
    # Create test user
    test_user = User(
        user_id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        google_id="test123",
        is_active=True,
        created_at=datetime.now(UTC),  # Using timezone-aware datetime
        last_login=datetime.now(UTC)   # Using timezone-aware datetime
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Query user
    queried_user = db.query(User).filter(User.email == "test@example.com").first()
    assert queried_user is not None
    assert queried_user.email == "test@example.com"
    assert queried_user.full_name == "Test User"
    
    # Cleanup
    db.delete(test_user)
    db.commit()