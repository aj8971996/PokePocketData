import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
import sys
import os
from pathlib import Path
import logging
from contextlib import asynccontextmanager

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
    """Test complete user journey: Create cards -> Build deck -> Record game"""
    try:
        # Create test user
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "picture": "https://example.com/pic.jpg",
            "google_id": "test123"
        }
        test_user = User(**user_data, user_id=uuid4())
        async_db_session.add(test_user)
        await async_db_session.commit()

        # Create ability for cards
        ability_id = uuid4()
        ability = Ability(ability_id=ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        # Create Pokemon card
        pokemon_data = {
            "name": "Test Pikachu",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "001",
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
                "ability_effect": "Test Effect",
                "damage": 20
            }]
        }
        pokemon_response = await async_client.post("/api/v1/cards/pokemon", json=pokemon_data)
        assert pokemon_response.status_code == 200
        pokemon_card_id = pokemon_response.json()["card_id"]

        # Create Trainer card
        trainer_data = {
            "name": "Test Trainer",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "002",
            "rarity": "1 Diamond",
            "abilities": [{
                "ability_ref": str(ability_id),
                "support_type": "Trainer",
                "effect_description": "Test Effect"
            }]
        }
        trainer_response = await async_client.post("/api/v1/cards/trainer", json=trainer_data)
        assert trainer_response.status_code == 200
        trainer_card_id = trainer_response.json()["card_id"]

        # Create deck with both cards
        deck_data = {
            "name": "Test Deck",
            "owner_id": str(test_user.user_id),
            "description": "Test Description",
            "cards": [str(pokemon_card_id)] * 15 + [str(trainer_card_id)] * 5  # 15 Pokemon, 5 Trainer
        }
        deck_response = await async_client.post("/api/v1/decks/", json=deck_data)
        assert deck_response.status_code == 200
        deck_id = deck_response.json()["deck_id"]

        # Record a game
        game_details = {
            "opponents_points": 2,
            "player_points": 3,
            "date_played": datetime.now(UTC).isoformat(),
            "turns_played": 10,
            "player_deck_used": str(deck_id),
            "opponent_name": "Test Opponent",
            "opponent_deck_type": "Aggro"
        }
        game_record = {
            "player_id": str(test_user.user_id),
            "outcome": "win",
            "ranking_change": 10
        }
        game_response = await async_client.post(
            "/api/v1/games/",
            json={"game_data": game_details, "game_record_data": game_record}
        )
        assert game_response.status_code == 200

        # Verify game statistics
        stats_response = await async_client.get(f"/api/v1/games/statistics/{test_user.user_id}")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_games"] == 1
        assert stats["wins"] == 1
        assert stats["win_rate"] == 100.0

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_deck_validation_journey(async_client, async_db_session):
    """Test deck building with validation rules"""
    try:
        # Setup user and basic cards
        user_data = {
            "email": "test2@example.com",
            "full_name": "Test User 2",
            "picture": "https://example.com/pic2.jpg",
            "google_id": "test456"
        }
        test_user = User(**user_data, user_id=uuid4())
        async_db_session.add(test_user)
        await async_db_session.commit()

        ability_id = uuid4()
        ability = Ability(ability_id=ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        # Create single Pokemon card
        pokemon_data = {
            "name": "Test Pikachu",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "001",
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
                "ability_effect": "Test Effect",
                "damage": 20
            }]
        }
        pokemon_response = await async_client.post("/api/v1/cards/pokemon", json=pokemon_data)
        assert pokemon_response.status_code == 200
        pokemon_card_id = pokemon_response.json()["card_id"]

        # Test invalid deck size (too few cards)
        invalid_deck_data = {
            "name": "Invalid Deck",
            "owner_id": str(test_user.user_id),
            "description": "Test Description",
            "cards": [str(pokemon_card_id)] * 10  # Only 10 cards
        }
        invalid_response = await async_client.post("/api/v1/decks/", json=invalid_deck_data)
        assert invalid_response.status_code == 422  # Validation error

        # Test deck update validation
        valid_deck_data = {
            "name": "Valid Deck",
            "owner_id": str(test_user.user_id),
            "description": "Test Description",
            "cards": [str(pokemon_card_id)] * 20  # Correct size
        }
        deck_response = await async_client.post("/api/v1/decks/", json=valid_deck_data)
        assert deck_response.status_code == 200
        deck_id = deck_response.json()["deck_id"]

        # Try invalid update
        invalid_update = {
            "cards": [str(pokemon_card_id)] * 10  # Too few cards
        }
        update_response = await async_client.put(f"/api/v1/decks/{deck_id}", json=invalid_update)
        assert update_response.status_code == 422

    finally:
        await cleanup_test_data(async_db_session)

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
        game_details = {
            "opponents_points": 4,
            "player_points": 3,  # Total > 6
            "date_played": datetime.now(UTC).isoformat(),
            "turns_played": 10,
            "player_deck_used": str(uuid4()),
            "opponent_name": "Test Opponent"
        }
        game_record = {
            "player_id": str(user.user_id),
            "outcome": "win",
            "ranking_change": 10
        }
        response = await async_client.post(
            "/api/v1/games/",
            json={"game_data": game_details, "game_record_data": game_record}
        )
        assert response.status_code == 422  # Validation error

    finally:
        await cleanup_test_data(async_db_session)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])