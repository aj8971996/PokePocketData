import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
import logging
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, UTC
from sqlalchemy import select
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.main import app
from app.database.async_session import get_async_db
from app.database.sql_models import *
from app.database.db_config import db_config

# Configure logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def managed_transaction(session):
    """Context manager for transaction management"""
    try:
        yield
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise

@pytest_asyncio.fixture(scope="function")
async def async_test_app():
    """Fixture to handle event loop setup/teardown"""
    yield app

@pytest_asyncio.fixture(scope="function")
async def async_client(async_test_app):
    async with AsyncClient(
        transport=ASGITransport(app=async_test_app), 
        base_url="http://testserver",
        timeout=30.0  # Increased timeout
    ) as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    """Create async database session for testing"""
    async_session_maker = db_config.get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


async def cleanup_test_data(async_db_session):
    """Clean up test data with detailed error logging"""
    try:
        async with managed_transaction(async_db_session):
            for model in [GameRecord, GameDetails, DeckCard, Deck,
                         PokemonAbility, SupportAbility, PokemonCard,
                         TrainerCard, Card, Ability, User]:
                try:
                    await async_db_session.execute(delete(model))
                    await async_db_session.flush()
                    logger.debug(f"Cleaned up {model.__name__}")
                except Exception as e:
                    logger.error(f"Error cleaning up {model.__name__}: {str(e)}")
                    raise
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise
@pytest.mark.asyncio
async def test_complete_user_journey(async_client, async_db_session):
    try:
        # Create user through API
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "google_id": str(uuid4()),
            "picture": "https://example.com/pic.jpg"
        }
        user_response = await async_client.post("/api/v1/users", json=user_data)
        assert user_response.status_code == 201
        user_id = user_response.json()["user_id"]

        # Create ability
        ability_id = uuid4()
        ability = Ability(ability_id=ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        # Create 15 unique Pokemon cards
        pokemon_cards = []
        for i in range(15):
            pokemon_data = {
                "name": f"Test Pokemon {i}",
                "set_name": "Genetic Apex (A1)",
                "pack_name": "(A1) Pikachu",
                "collection_number": f"{i+1:03d}",
                "rarity": "1 Diamond",
                "hp": 60,
                "type": "Electric",
                "stage": "Basic",
                "weakness": "Fighting",
                "retreat_cost": 1,
                "evolves_from": None,
                "abilities": [{
                    "ability_ref": str(ability_id),
                    "energy_cost": {"Electric": 1},
                    "ability_effect": f"Test Effect {i}",
                    "damage": 20
                }]
            }
            response = await async_client.post("/api/v1/cards/pokemon", json=pokemon_data)
            assert response.status_code == 200
            pokemon_cards.append(response.json()["card_id"])

        # Create 5 unique Trainer cards
        trainer_cards = []
        for i in range(5):
            trainer_data = {
                "name": f"Test Trainer {i}",
                "set_name": "Genetic Apex (A1)",
                "pack_name": "(A1) Pikachu",
                "collection_number": f"{i+16:03d}",  # Continue numbering from Pokemon cards
                "rarity": "1 Diamond",
                "abilities": [{
                    "ability_ref": str(ability_id),
                    "support_type": "Trainer",
                    "effect_description": f"Test Effect {i}"
                }]
            }
            response = await async_client.post("/api/v1/cards/trainer", json=trainer_data)
            assert response.status_code == 200
            trainer_cards.append(response.json()["card_id"])

        # Create deck with unique cards
        deck_data = {
            "name": "Test Deck",
            "owner_id": str(user_id),
            "description": "Test Description",
            "cards": pokemon_cards + trainer_cards  # 15 Pokemon + 5 Trainer = 20 unique cards
        }
        
        # Create deck with cards
        deck_response = await async_client.post("/api/v1/decks/", json=deck_data)
        assert deck_response.status_code == 200
        deck_id = deck_response.json()["deck_id"]

        # Modified game creation
        game_data = {
            "opponents_points": 2,
            "player_points": 3,
            "date_played": datetime.now(UTC).isoformat(),
            "turns_played": 10,
            "player_deck_used": str(deck_id),
            "opponent_name": "Test Opponent",
            "opponent_deck_type": "control"
        }

        game_record_data = {
            "player_id": str(user_id),
            "outcome": "WIN",  # Changed to uppercase to match enum
            "ranking_change": 10
        }

        game_response = await async_client.post(
            "/api/v1/games/",
            json={
                "game_data": game_data,
                "game_record_data": game_record_data
            }
        )
        assert game_response.status_code == 200

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_deck_validation_journey(async_client, async_db_session):
    try:
        # Create test user
        async with managed_transaction(async_db_session):
            test_user = User(
                user_id=uuid4(),
                email="test2@example.com",
                full_name="Test User 2",
                picture="https://example.com/pic2.jpg",
                google_id="test456",
                is_active=True,
                created_at=datetime.now(UTC),
                last_login=datetime.now(UTC)
            )
            async_db_session.add(test_user)
        await asyncio.sleep(0.1)
        await async_db_session.commit()

        ability_id = uuid4()
        ability = Ability(ability_id=ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        card_ids = []
        for i in range(20):
            pokemon_data = {
                "name": f"Test Pokemon {i}",
                "set_name": "Genetic Apex (A1)",
                "pack_name": "(A1) Pikachu",
                "collection_number": f"{i+1:03d}",
                "rarity": "1 Diamond",
                "hp": 60,
                "type": "Electric",
                "stage": "Basic",
                "weakness": "Fighting",
                "retreat_cost": 1,
                "evolves_from": None,
                "abilities": [{
                    "ability_ref": str(ability_id),
                    "energy_cost": {"Electric": 1},
                    "ability_effect": f"Test Effect {i}",
                    "damage": 20
                }]
            }
            response = await async_client.post("/api/v1/cards/pokemon", json=pokemon_data)
            assert response.status_code == 200, f"Failed to create card {i}: {response.text}"
            card_ids.append(response.json()["card_id"])
            await asyncio.sleep(0.1)

        valid_deck_data = {
            "name": "Valid Deck",
            "owner_id": str(test_user.user_id),
            "description": "Test Description",
            "cards": card_ids
        }

        logger.info(f"Creating deck: {valid_deck_data}")
        deck_response = await async_client.post("/api/v1/decks/", json=valid_deck_data)
        logger.info(f"Deck response: {deck_response.text}")
        assert deck_response.status_code == 200, f"Failed to create deck: {deck_response.text}"

        deck_id = deck_response.json()["deck_id"]
        result = await async_db_session.execute(
            select(Deck).filter(Deck.deck_id == deck_id)
        )
        created_deck = result.scalar_one_or_none()
        assert created_deck is not None

    except Exception as e:
        logger.error("Test failed: %s", str(e), exc_info=True)
        raise
    finally:
        await cleanup_test_data(async_db_session)
        await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_game_recording_validation(async_client, async_db_session):
    """Test game recording with validation rules"""
    try:
        # Setup basic test data
        user = User(
            user_id=uuid4(),
            email="test3@example.com",
            full_name="Test User 3",
            picture="https://example.com/pic3.jpg",
            google_id="test789"
        )
        async_db_session.add(user)
        await async_db_session.commit()

        # Test invalid points total
        game_data = {
            "opponents_points": 4,
            "player_points": 3,
            "date_played": datetime.now(UTC).isoformat(),
            "turns_played": 10,
            "player_deck_used": str(uuid4()),
            "opponent_name": "Test Opponent",
            "opponent_deck_type": "control"
        }

        game_record_data = {
            "player_id": str(user.user_id),
            "outcome": "win",
            "ranking_change": 10
        }

        response = await async_client.post(
            "/api/v1/games/",
            json={
                "game_data": game_data,
                "game_record_data": game_record_data
            }
        )
        assert response.status_code == 422  # Validation error

    finally:
        await cleanup_test_data(async_db_session)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])