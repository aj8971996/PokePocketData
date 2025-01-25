import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
import sys
from pathlib import Path
import logging

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.main import app
from app.database.async_session import get_async_db
from app.database.sql_models import User, GameRecord, GameDetails, Deck
from app.database.db_config import db_config

logger = logging.getLogger(__name__)

@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    async_session_maker = db_config.get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

async def cleanup_test_data(async_db_session):
    try:
        await async_db_session.execute(delete(GameRecord))
        await async_db_session.execute(delete(GameDetails))
        await async_db_session.execute(delete(Deck))
        await async_db_session.execute(delete(User))
        await async_db_session.commit()
    except Exception as e:
        await async_db_session.rollback()
        logger.error(f"Cleanup error: {e}")
        raise e
    


@pytest.mark.asyncio
async def test_create_game_record(async_client, async_db_session):
    try:
        # Create test user
        test_user = User(
            user_id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            google_id="test123",
            is_active=True,
            created_at=datetime.now(UTC),
            last_login=datetime.now(UTC)
        )
        async_db_session.add(test_user)
        await async_db_session.commit()

        # Create test deck
        test_deck = Deck(
            deck_id=uuid4(),
            name="Test Deck",
            owner_id=test_user.user_id,
            description="Test Description",
            is_active=True
        )
        async_db_session.add(test_deck)
        await async_db_session.commit()

        # Create game record
        game_data = {
            "opponents_points": 2,
            "player_points": 3,
            "date_played": datetime.now(UTC).isoformat(),
            "turns_played": 10,
            "player_deck_used": str(test_deck.deck_id),
            "opponent_name": "Test Opponent",
            "opponent_deck_type": "control"
        }

        game_record_data = {
            "player_id": str(test_user.user_id),
            "outcome": "WIN",  # Changed from "win" to "WIN"
            "ranking_change": 10
        }

        response = await async_client.post(
            "/api/v1/games/",
            json={
                "game_data": game_data,
                "game_record_data": game_record_data
            }
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify response data
        assert response_data["player_id"] == str(test_user.user_id)
        assert response_data["outcome"] == "WIN"
        assert response_data["game_details"]["player_deck_used"] == str(test_deck.deck_id)

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_game_outcome_validation(async_client, async_db_session):
    try:
        test_user = User(
            user_id=uuid4(),
            email="test3@example.com",
            full_name="Test User 3",
            google_id="test789",
            is_active=True,
            created_at=datetime.now(UTC),
            last_login=datetime.now(UTC)
        )
        async_db_session.add(test_user)
        
        test_deck = Deck(
            deck_id=uuid4(),
            name="Test Deck",
            owner_id=test_user.user_id,
            description="Test Description",
            is_active=True
        )
        async_db_session.add(test_deck)
        await async_db_session.commit()

        game_data = {
            "opponents_points": 2,
            "player_points": 3,
            "date_played": datetime.now(UTC).isoformat(),
            "turns_played": 10,
            "player_deck_used": str(test_deck.deck_id),
            "opponent_name": "Test Opponent",
            "opponent_deck_type": "control"
        }

        outcomes = ["WIN", "LOSS", "DRAW"]
        for outcome in outcomes:
            game_record_data = {
                "player_id": str(test_user.user_id),
                "outcome": outcome,
                "ranking_change": 10
            }

            response = await async_client.post(
                "/api/v1/games/",
                json={
                    "game_data": game_data,
                    "game_record_data": game_record_data
                }
            )
            assert response.status_code == 200
            assert response.json()["outcome"] == outcome

    finally:
        await cleanup_test_data(async_db_session)

