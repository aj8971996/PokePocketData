import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from sqlalchemy import delete  # Add this import
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sys
from pathlib import Path
import logging  # Add this import for logger

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.main import app
from app.database.async_session import get_async_db
from app.database.sql_models import (
    Card,  # Use these names exactly as they appear in sql_models.py
    PokemonCard, 
    Ability, 
    PokemonAbility
)
from app.database.db_config import db_config

# Add a logger
logger = logging.getLogger(__name__)

@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://testserver"
    ) as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    """Create an async database session for testing"""
    async_session_maker = db_config.get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

async def cleanup_test_data(async_db_session):
    """Helper function to remove test data after each test"""
    try:
        # Delete records using delete with filter
        await async_db_session.execute(delete(PokemonAbility))
        await async_db_session.execute(delete(PokemonCard))
        await async_db_session.execute(delete(Card))
        await async_db_session.execute(delete(Ability))
        await async_db_session.commit()
    except Exception as e:
        await async_db_session.rollback()
        logger.error(f"Error in cleanup: {e}")

@pytest.mark.asyncio
async def test_create_valid_pokemon_card(async_client, async_db_session):
    """Test creating a valid Pokemon card"""
    try:
        # Prepare test ability
        test_ability_id = str(uuid4())
        ability = Ability(ability_id=test_ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        # Prepare card data
        card_data = {
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
            # Add evolves_from, using None or an empty string
            "evolves_from": None,  # or "" if the model expects a string
            "abilities": [
                {
                    "ability_ref": test_ability_id,
                    "energy_cost": {"Electric": 1},
                    "ability_effect": "Test Thunder Shock",
                    "damage": 20
                }
            ]
        }
        
        # Send POST request
        response = await async_client.post("/api/v1/cards/pokemon", json=card_data)
        
        # Print response for debugging
        print(response.text)
        
        # Assert successful creation
        assert response.status_code == 200, f"Response: {response.text}"
        response_data = response.json()
        assert response_data["name"] == "Test Pikachu"
        
        # Verify data in database
        created_card_query = await async_db_session.execute(
            select(Card).filter_by(name="Test Pikachu")
        )
        created_card = created_card_query.scalar_one_or_none()
        assert created_card is not None
        
        pokemon_card_query = await async_db_session.execute(
            select(PokemonCard).filter_by(card_ref=created_card.card_id)
        )
        pokemon_card = pokemon_card_query.scalar_one_or_none()
        assert pokemon_card is not None
        assert pokemon_card.hp == 60
        
    finally:
        # Always clean up test data
        await cleanup_test_data(async_db_session)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])