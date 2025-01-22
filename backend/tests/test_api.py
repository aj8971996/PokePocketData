import pytest
from fastapi.testclient import TestClient
import logging
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.main import app
from app.database import DatabaseConfig, DatabaseEnvironment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    """Test the root endpoint returns correct API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app_name"] == "PokéPocketData API"
    assert "version" in data
    assert "environment" in data

def test_health_check(client):
    """Test health check endpoint returns correct structure"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    # Check structure matches main.py implementation
    assert "status" in data
    assert "database" in data
    assert isinstance(data["database"], dict)
    assert "connected" in data["database"]
    assert "environment" in data["database"]
    assert "host" in data["database"]
    assert "api_version" in data

def test_api_documentation_endpoints(client):
    """Test that API documentation endpoints are accessible"""
    # OpenAPI JSON
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    
    # Swagger UI
    response = client.get("/api/docs")
    assert response.status_code == 200
    
    # ReDoc
    response = client.get("/api/redoc")
    assert response.status_code == 200

def test_cors_headers(client):
    """Test CORS headers are properly set"""
    response = client.options("/", headers={
        "origin": "http://localhost:4200",
        "access-control-request-method": "GET",
        "access-control-request-headers": "content-type"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers.keys()
    assert "access-control-allow-methods" in response.headers.keys()
    
    # Log headers for debugging
    logger.info("Response headers: %s", dict(response.headers))
    
    # Check allowed origins
    assert response.headers["access-control-allow-origin"] == "http://localhost:4200"
    
    # Check allowed methods (should contain at least GET)
    allowed_methods = response.headers["access-control-allow-methods"]
    assert "GET" in allowed_methods

def test_error_handling(client):
    """Test global error handling"""
    # Test 404 handling
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Test invalid method handling
    response = client.post("/health")  # Health endpoint only accepts GET
    assert response.status_code in [405, 404]
    assert "detail" in response.json()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])