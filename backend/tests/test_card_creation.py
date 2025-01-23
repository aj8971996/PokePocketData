import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sys
from pathlib import Path
import logging

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.main import app
from app.database.async_session import get_async_db
from app.database.sql_models import (
    Card,
    PokemonCard, 
    Ability, 
    PokemonAbility,
    TrainerCard,
    SupportAbility
)
from app.database.db_config import db_config

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
        await async_db_session.execute(delete(SupportAbility))  # Added for trainer cards
        await async_db_session.execute(delete(PokemonCard))
        await async_db_session.execute(delete(TrainerCard))  # Added for trainer cards
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
        test_ability_id = str(uuid4())
        ability = Ability(ability_id=test_ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

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
            "evolves_from": None,
            "abilities": [
                {
                    "ability_ref": test_ability_id,
                    "energy_cost": {"Electric": 1},
                    "ability_effect": "Test Thunder Shock",
                    "damage": 20
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/pokemon", json=card_data)
        print(response.text)
        
        assert response.status_code == 200, f"Response: {response.text}"
        response_data = response.json()
        assert response_data["name"] == "Test Pikachu"
        
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
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_invalid_pokemon_type(async_client, async_db_session):
    """Test Pokemon card creation with invalid type"""
    try:
        test_ability_id = str(uuid4())
        ability = Ability(ability_id=test_ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        card_data = {
            "name": "Invalid Type Pokemon",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "002",
            "rarity": "1 Diamond",
            "hp": 60,
            "type": "InvalidType",
            "stage": "Basic",
            "weakness": "Fighting",
            "retreat_cost": 1,
            "evolves_from": None,
            "abilities": [
                {
                    "ability_ref": test_ability_id,
                    "energy_cost": {"Electric": 1},
                    "ability_effect": "Test Effect",
                    "damage": 20
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/pokemon", json=card_data)
        assert response.status_code == 422

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_pokemon_hp_validation(async_client, async_db_session):
    """Test Pokemon card HP validation"""
    try:
        test_ability_id = str(uuid4())
        ability = Ability(ability_id=test_ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        card_data = {
            "name": "Invalid HP Pokemon",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "003",
            "rarity": "1 Diamond",
            "hp": 0,
            "type": "Electric",
            "stage": "Basic",
            "weakness": "Fighting",
            "retreat_cost": 1,
            "evolves_from": None,
            "abilities": [
                {
                    "ability_ref": test_ability_id,
                    "energy_cost": {"Electric": 1},
                    "ability_effect": "Test Effect",
                    "damage": 20
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/pokemon", json=card_data)
        assert response.status_code == 422

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_pokemon_multiple_abilities(async_client, async_db_session):
    """Test Pokemon card with multiple abilities"""
    try:
        ability_id1 = str(uuid4())
        ability_id2 = str(uuid4())
        
        ability1 = Ability(ability_id=ability_id1, name="Test Ability 1")
        ability2 = Ability(ability_id=ability_id2, name="Test Ability 2")
        
        async_db_session.add(ability1)
        async_db_session.add(ability2)
        await async_db_session.commit()

        card_data = {
            "name": "Multi-Ability Pokemon",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "004",
            "rarity": "1 Diamond",
            "hp": 70,
            "type": "Electric",
            "stage": "Basic",
            "weakness": "Fighting",
            "retreat_cost": 1,
            "evolves_from": None,
            "abilities": [
                {
                    "ability_ref": ability_id1,
                    "energy_cost": {"Electric": 1},
                    "ability_effect": "First Effect",
                    "damage": 20
                },
                {
                    "ability_ref": ability_id2,
                    "energy_cost": {"Electric": 2},
                    "ability_effect": "Second Effect",
                    "damage": 40
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/pokemon", json=card_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert len(response_data["abilities"]) == 2

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_pokemon_stage_evolution_validation(async_client, async_db_session):
    """Test Pokemon card stage and evolution validation"""
    try:
        test_ability_id = str(uuid4())
        ability = Ability(ability_id=test_ability_id, name="Test Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        # Test cases for stage/evolution combinations
        test_cases = [
            {
                "stage": "Basic",
                "evolves_from": None,
                "expected_status": 200
            },
            {
                "stage": "Stage 1",
                "evolves_from": None,
                "expected_status": 422
            },
            {
                "stage": "Stage 1",
                "evolves_from": "Pichu",
                "expected_status": 200
            }
        ]

        for test_case in test_cases:
            card_data = {
                "name": f"Test {test_case['stage']} Pokemon",
                "set_name": "Genetic Apex (A1)",
                "pack_name": "(A1) Pikachu",
                "collection_number": "005",
                "rarity": "1 Diamond",
                "hp": 70,
                "type": "Electric",
                "stage": test_case["stage"],
                "weakness": "Fighting",
                "retreat_cost": 1,
                "evolves_from": test_case["evolves_from"],
                "abilities": [
                    {
                        "ability_ref": test_ability_id,
                        "energy_cost": {"Electric": 1},
                        "ability_effect": "Test Effect",
                        "damage": 20
                    }
                ]
            }
            
            response = await async_client.post("/api/v1/cards/pokemon", json=card_data)
            assert response.status_code == test_case["expected_status"], \
                f"Failed for stage={test_case['stage']}, evolves_from={test_case['evolves_from']}"

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_create_valid_trainer_card(async_client, async_db_session):
    """Test creating a valid trainer card"""
    try:
        test_ability_id = str(uuid4())
        ability = Ability(ability_id=test_ability_id, name="Test Trainer Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        card_data = {
            "name": "Test Trainer",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "010",
            "rarity": "1 Diamond",
            "abilities": [
                {
                    "ability_ref": test_ability_id,
                    "support_type": "Trainer",
                    "effect_description": "Test trainer effect"
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/trainer", json=card_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["name"] == "Test Trainer"
        
        # Verify database entries
        created_card_query = await async_db_session.execute(
            select(Card).filter_by(name="Test Trainer")
        )
        created_card = created_card_query.scalar_one_or_none()
        assert created_card is not None

        trainer_card_query = await async_db_session.execute(
            select(TrainerCard).filter_by(card_ref=created_card.card_id)
        )
        trainer_card = trainer_card_query.scalar_one_or_none()
        assert trainer_card is not None

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_trainer_support_type_validation(async_client, async_db_session):
    """Test trainer card support type validation"""
    try:
        test_ability_id = str(uuid4())
        ability = Ability(ability_id=test_ability_id, name="Test Trainer Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        card_data = {
            "name": "Invalid Trainer",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "011",
            "rarity": "1 Diamond",
            "abilities": [
                {
                    "ability_ref": test_ability_id,
                    "support_type": "InvalidType",  # Invalid support type
                    "effect_description": "Test effect"
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/trainer", json=card_data)
        assert response.status_code == 422

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_trainer_multiple_abilities(async_client, async_db_session):
    """Test trainer card with multiple abilities"""
    try:
        ability_id1 = str(uuid4())
        ability_id2 = str(uuid4())
        
        ability1 = Ability(ability_id=ability_id1, name="First Trainer Ability")
        ability2 = Ability(ability_id=ability_id2, name="Second Trainer Ability")
        
        async_db_session.add(ability1)
        async_db_session.add(ability2)
        await async_db_session.commit()

        card_data = {
            "name": "Multi-Effect Trainer",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "012",
            "rarity": "1 Diamond",
            "abilities": [
                {
                    "ability_ref": ability_id1,
                    "support_type": "Trainer",
                    "effect_description": "First trainer effect"
                },
                {
                    "ability_ref": ability_id2,
                    "support_type": "Item",
                    "effect_description": "Second item effect"
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/trainer", json=card_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert len(response_data["abilities"]) == 2

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_trainer_invalid_support_type(async_client, async_db_session):
    """Test trainer card with invalid support type"""
    try:
        ability_id = str(uuid4())
        ability = Ability(ability_id=ability_id, name="Trainer Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        card_data = {
            "name": "Invalid Support Type",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "013",
            "rarity": "1 Diamond",
            "abilities": [
                {
                    "ability_ref": ability_id,
                    "support_type": "Invalid",  # Invalid type
                    "effect_description": "Test effect"
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/trainer", json=card_data)
        assert response.status_code == 422

    finally:
        await cleanup_test_data(async_db_session)

@pytest.mark.asyncio
async def test_trainer_duplicate_collection_number(async_client, async_db_session):
    """Test trainer card with duplicate collection number"""
    try:
        # Create first trainer card
        ability_id = str(uuid4())
        ability = Ability(ability_id=ability_id, name="First Ability")
        async_db_session.add(ability)
        await async_db_session.commit()

        first_card_data = {
            "name": "First Trainer",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "014",
            "rarity": "1 Diamond",
            "abilities": [
                {
                    "ability_ref": ability_id,
                    "support_type": "Trainer",
                    "effect_description": "First effect"
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/trainer", json=first_card_data)
        assert response.status_code == 200

        # Try creating second card with same collection number
        second_card_data = {
            "name": "Second Trainer",
            "set_name": "Genetic Apex (A1)",
            "pack_name": "(A1) Pikachu",
            "collection_number": "014",  # Same number
            "rarity": "1 Diamond",
            "abilities": [
                {
                    "ability_ref": ability_id,
                    "support_type": "Trainer",
                    "effect_description": "Second effect"
                }
            ]
        }
        
        response = await async_client.post("/api/v1/cards/trainer", json=second_card_data)
        assert response.status_code == 400

    finally:
        await cleanup_test_data(async_db_session)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])