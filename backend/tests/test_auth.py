import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, UTC
from uuid import uuid4
from pathlib import Path
import logging
from email_validator import validate_email
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.main import app
from app.database.sql_models import User
from app.database.db_config import db_config
from sqlalchemy import delete



project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)

VALID_USER_DATA = {
    "email": "test@example.com",
    "full_name": "Test User",
    "google_id": str(uuid4()),
    "picture": "https://example.com/picture.jpg"
}

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        timeout=30.0
    ) as client:
        yield client

@pytest_asyncio.fixture
async def async_db_session():
    async_session_maker = db_config.get_async_session_maker()
    async with async_session_maker() as session:
        yield session
        await session.rollback()
        await session.close()

async def cleanup_tables(session):
    await session.execute(delete(User))
    await session.commit()

@pytest.mark.asyncio
async def test_create_user(async_client, async_db_session):
    try:
        response = await async_client.post("/api/v1/users", json=VALID_USER_DATA)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == VALID_USER_DATA["email"]
        assert "user_id" in data
        assert "created_at" in data
        assert "last_login" in data
    finally:
        await cleanup_tables(async_db_session)

@pytest.mark.asyncio
async def test_duplicate_user(async_client, async_db_session):
    try:
        await async_client.post("/api/v1/users", json=VALID_USER_DATA)
        response = await async_client.post("/api/v1/users", json=VALID_USER_DATA)
        assert response.status_code == 409
    finally:
        await cleanup_tables(async_db_session)

@pytest.mark.asyncio
async def test_invalid_user_data(async_client, async_db_session):
    try:
        invalid_data = VALID_USER_DATA.copy()
        invalid_data.pop("email")
        response = await async_client.post("/api/v1/users", json=invalid_data)
        assert response.status_code == 422
    finally:
        await cleanup_tables(async_db_session)

@pytest.mark.asyncio
async def test_get_user(async_client, async_db_session):
    try:
        create_response = await async_client.post("/api/v1/users", json=VALID_USER_DATA)
        user_id = create_response.json()["user_id"]
        response = await async_client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == VALID_USER_DATA["email"]
    finally:
        await cleanup_tables(async_db_session)

@pytest.mark.asyncio
async def test_update_user(async_client, async_db_session):
    try:
        create_response = await async_client.post("/api/v1/users", json=VALID_USER_DATA)
        print(f"Create Response Status: {create_response.status_code}")
        print(f"Create Response Body: {create_response.text}")
        user_id = create_response.json()["user_id"]
        update_data = {"full_name": "Updated Name"}
        response = await async_client.patch(f"/api/v1/users/{user_id}", json=update_data)
        print(f"Response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
    finally:
        await cleanup_tables(async_db_session)

if __name__ == "__main__":
    pytest.main(["-v", "-s"])