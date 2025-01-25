import pytest
from fastapi.testclient import TestClient
from datetime import datetime, UTC
from uuid import uuid4
from .test_integration import client, test_db, test_config, test_db_setup

# Test data
VALID_USER_DATA = {
    "email": "test@example.com",
    "full_name": "Test User",
    "google_id": str(uuid4()),
    "picture": "https://example.com/picture.jpg"
}

def test_create_user(client: TestClient):
    response = client.post("/api/users/", json=VALID_USER_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == VALID_USER_DATA["email"]
    assert "user_id" in data

def test_duplicate_user(client: TestClient):
    # First creation
    client.post("/api/users/", json=VALID_USER_DATA)
    
    # Attempt duplicate
    response = client.post("/api/users/", json=VALID_USER_DATA)
    assert response.status_code == 409

def test_invalid_user_data(client: TestClient):
    invalid_data = VALID_USER_DATA.copy()
    invalid_data.pop("email")
    response = client.post("/api/users/", json=invalid_data)
    assert response.status_code == 422

def test_get_user(client: TestClient):
    # Create user first
    create_response = client.post("/api/users/", json=VALID_USER_DATA)
    user_id = create_response.json()["user_id"]
    
    # Get user
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == VALID_USER_DATA["email"]

def test_update_user(client: TestClient):
    # Create user
    create_response = client.post("/api/users/", json=VALID_USER_DATA)
    user_id = create_response.json()["user_id"]
    
    # Update user
    update_data = {"full_name": "Updated Name"}
    response = client.patch(f"/api/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])