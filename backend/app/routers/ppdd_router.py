# app/routers/ppdd_router.py
import sys
from pathlib import Path
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, UTC
from sqlalchemy import delete, select

# Get the absolute path of the current file's directory
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'backend'))

from app.database import get_db
from app.database.async_session import get_async_db
from app.database.sql_models import (
    Card as SQLCard,
    Ability as SQLAbility,
    PokemonCard as SQLPokemonCard,
    TrainerCard as SQLTrainerCard,
    Deck as SQLDeck,
    GameDetails as SQLGameDetails,
    GameRecord as SQLGameRecord,
    DeckCard as SQLDeckCard,
    PokemonAbility as SQLPokemonAbility,
    SupportAbility as SQLSupportAbility,
    GameOutcome,
    User as SQLUser
)
from app.models.pydantic_models import (
    # Create/Update Models
    CardCreate, CardUpdate, 
    PokemonCardCreate, TrainerCardCreate,
    DeckCreate, DeckUpdate, UserCreate,
    GameDetailsCreate, GameRecordCreate,
    # Response Models
    CardResponse, PokemonCardResponse, TrainerCardResponse,
    DeckResponse, GameDetailsResponse, GameRecordResponse,
    SupportAbility, UserResponse
)

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

# Card Endpoints
@router.post("/cards/pokemon", response_model=PokemonCardResponse)
async def create_pokemon_card(
    card_data: PokemonCardCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new Pokemon card with associated base card"""
    logger.info(f"Attempting to create Pokemon card: {card_data.name}")
    try:
        # Create base card first
        new_card = SQLCard(
            name=card_data.name,
            set_name=card_data.set_name,
            pack_name=card_data.pack_name,
            collection_number=card_data.collection_number,
            rarity=card_data.rarity,
            image_url=card_data.image_url
        )
        db.add(new_card)
        await db.flush()

        # Create Pokemon card
        pokemon_card = SQLPokemonCard(
            card_ref=new_card.card_id,
            hp=card_data.hp,
            type=card_data.type,
            stage=card_data.stage,
            evolves_from=card_data.evolves_from,
            weakness=card_data.weakness,
            retreat_cost=card_data.retreat_cost
        )
        db.add(pokemon_card)

        # Add abilities 
        pokemon_abilities = []
        for ability_data in card_data.abilities:
            # Fetch the ability to verify its existence
            ability_query = await db.execute(
                select(SQLAbility).filter(SQLAbility.ability_id == ability_data.ability_ref)
            )
            existing_ability = ability_query.scalar_one_or_none()
            
            if not existing_ability:
                raise HTTPException(status_code=400, detail=f"Ability {ability_data.ability_ref} not found")

            ability = SQLPokemonAbility(
                pokemon_card_ref=pokemon_card.card_ref,
                ability_ref=ability_data.ability_ref,
                ability_id=str(uuid4()),  # Generate a new UUID for the pokemon ability
                energy_cost=ability_data.energy_cost,
                ability_effect=ability_data.ability_effect,
                damage=ability_data.damage
            )
            db.add(ability)
            pokemon_abilities.append(ability)
            
        await db.commit()

        # Log debug information
        logger.debug(f"Created Pokemon card: {new_card.name}")
        logger.debug(f"Number of abilities: {len(pokemon_abilities)}")

        # Explicitly construct the response
        response = PokemonCardResponse(
            card_id=new_card.card_id,
            name=new_card.name,
            set_name=new_card.set_name,
            pack_name=new_card.pack_name,
            collection_number=new_card.collection_number,
            rarity=new_card.rarity,
            image_url=new_card.image_url,
            hp=pokemon_card.hp,
            type=pokemon_card.type,
            stage=pokemon_card.stage,
            evolves_from=pokemon_card.evolves_from,
            weakness=pokemon_card.weakness,
            retreat_cost=pokemon_card.retreat_cost,
            abilities=[
                SQLPokemonAbility(
                    ability_id=ability.ability_id,
                    ability_ref=ability.ability_ref,
                    energy_cost=ability.energy_cost,
                    ability_effect=ability.ability_effect,
                    damage=ability.damage
                ) for ability in pokemon_abilities
            ]
        )

        logger.debug(f"Response abilities: {response.abilities}")
        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error while creating Pokemon card: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while creating Pokemon card: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/cards/trainer", response_model=TrainerCardResponse)
async def create_trainer_card(
    card_data: TrainerCardCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new Trainer card"""
    logger.info(f"Attempting to create Trainer card: {card_data.name}")
    try:
        existing_card_query = await db.execute(
            select(SQLCard).filter(
                SQLCard.collection_number == card_data.collection_number,
                SQLCard.set_name == card_data.set_name
            )
        )
        if existing_card_query.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Card with collection number {card_data.collection_number} already exists in set {card_data.set_name}"
            )

        new_card = SQLCard(
            name=card_data.name,
            set_name=card_data.set_name,
            pack_name=card_data.pack_name,
            collection_number=card_data.collection_number,
            rarity=card_data.rarity,
            image_url=card_data.image_url
        )
        db.add(new_card)
        await db.flush()

        trainer_card = SQLTrainerCard(
            card_ref=new_card.card_id
        )
        db.add(trainer_card)
        await db.flush()
        
        support_abilities = []
        for ability_data in card_data.abilities:
            ability_query = await db.execute(
                select(SQLAbility).filter(SQLAbility.ability_id == ability_data.ability_ref)
            )
            if not ability_query.scalar_one_or_none():
                await db.rollback()
                raise HTTPException(status_code=400, detail=f"Ability {ability_data.ability_ref} not found")
                
            support_ability = SQLSupportAbility(
                trainer_card_ref=trainer_card.card_ref,
                ability_ref=ability_data.ability_ref,
                support_type=ability_data.support_type,
                effect_description=ability_data.effect_description
            )
            db.add(support_ability)
            support_abilities.append(SupportAbility(
                ability_ref=ability_data.ability_ref,
                support_type=ability_data.support_type,
                effect_description=ability_data.effect_description
            ))

        await db.commit()
        
        return TrainerCardResponse(
            card_id=new_card.card_id,
            name=new_card.name,
            set_name=new_card.set_name,
            pack_name=new_card.pack_name,
            collection_number=new_card.collection_number,
            rarity=new_card.rarity,
            image_url=new_card.image_url,
            abilities=support_abilities
        )
        
    except HTTPException as e:
        await db.rollback()
        raise e
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating trainer card: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while creating trainer card: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cards/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific card by ID"""
    try:
        card = await db.query(SQLCard).filter(SQLCard.card_id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        return card
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching card: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cards/", response_model=List[CardResponse])
async def list_cards(
    set_name: Optional[str] = None,
    pack_name: Optional[str] = None,
    rarity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List cards with optional filtering"""
    try:
        query = db.query(SQLCard)
        
        if set_name:
            query = query.filter(SQLCard.set_name == set_name)
        if pack_name:
            query = query.filter(SQLCard.pack_name == pack_name)
        if rarity:
            query = query.filter(SQLCard.rarity == rarity)
        
        cards = await query.offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(cards)} cards")
        return cards
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching cards: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/decks/", response_model=DeckResponse)
async def create_deck(
    deck_data: DeckCreate,
    db: AsyncSession = Depends(get_async_db)
):
    try:
        for card_id in deck_data.cards:
            result = await db.execute(
                select(SQLCard).filter(SQLCard.card_id == card_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail=f"Card {card_id} not found")

        new_deck = SQLDeck(
            name=deck_data.name,
            owner_id=deck_data.owner_id,
            description=deck_data.description,
            is_active=True
        )
        db.add(new_deck)
        await db.flush()

        deck_cards = [SQLDeckCard(deck_id=new_deck.deck_id, card_id=card_id) 
                     for card_id in deck_data.cards]
        db.add_all(deck_cards)
        
        # Load cards before committing
        card_query = await db.execute(
            select(SQLCard).filter(SQLCard.card_id.in_([dc.card_id for dc in deck_cards]))
        )
        cards = card_query.scalars().all()
        cards_by_id = {str(card.card_id): card for card in cards}
        
        await db.commit()

        # Return response using loaded cards
        return {
            "deck_id": new_deck.deck_id,
            "name": new_deck.name,
            "created_at": new_deck.created_at,
            "updated_at": new_deck.updated_at,
            "owner_id": new_deck.owner_id,
            "description": new_deck.description,
            "is_active": new_deck.is_active,
            "cards": [{
                "card_id": str(dc.card_id),
                "name": cards_by_id[str(dc.card_id)].name,
                "set_name": cards_by_id[str(dc.card_id)].set_name.value,
                "pack_name": cards_by_id[str(dc.card_id)].pack_name.value,
                "collection_number": cards_by_id[str(dc.card_id)].collection_number,
                "rarity": cards_by_id[str(dc.card_id)].rarity.value,
                "image_url": cards_by_id[str(dc.card_id)].image_url
            } for dc in deck_cards]
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/decks/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: UUID,
    deck_data: DeckUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific deck"""
    try:
        result = await db.execute(select(SQLDeck).filter(SQLDeck.deck_id == deck_id))
        deck = result.scalar_one_or_none()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        for key, value in deck_data.dict(exclude_unset=True).items():
            setattr(deck, key, value)

        if deck_data.cards:
            query = delete(SQLDeckCard).where(SQLDeckCard.deck_id == deck_id)
            await db.execute(query)
            for card_id in deck_data.cards:
                deck_card = SQLDeckCard(deck_id=deck_id, card_id=card_id)
                db.add(deck_card)

        await db.commit()
        return deck

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/decks/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific deck by ID"""
    result = await db.execute(select(SQLDeck).filter(SQLDeck.deck_id == deck_id))
    deck = result.scalar_one_or_none()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

# Game Record Endpoints
@router.post("/games/", response_model=GameRecordResponse)
async def create_game_record(
    game_data: GameDetailsCreate,
    game_record_data: GameRecordCreate,
    db: AsyncSession = Depends(get_async_db)
):
    try:
        game_details = SQLGameDetails(**game_data.model_dump())
        db.add(game_details)
        await db.flush()

        # Store the original outcome value
        outcome_value = game_record_data.outcome

        game_record = SQLGameRecord(
            player_id=game_record_data.player_id,
            game_details_ref=game_details.game_details_id,
            outcome=getattr(GameOutcome, outcome_value),
            ranking_change=game_record_data.ranking_change
        )
        db.add(game_record)
        await db.commit()
        
        # Return response without refresh
        return {
            "game_record_id": game_record.game_record_id,
            "player_id": game_record.player_id,
            "game_details_ref": game_record.game_details_ref,
            "outcome": outcome_value,
            "ranking_change": game_record.ranking_change,
            "game_details": game_details
        }
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/games/statistics/{player_id}")
async def get_player_statistics(
    player_id: UUID,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get player statistics including win/loss ratio"""
    try:
        stats = await db.query(
            SQLGameRecord.outcome,
            db.func.count(SQLGameRecord.outcome)
        ).filter(
            SQLGameRecord.player_id == player_id
        ).group_by(
            SQLGameRecord.outcome
        ).all()

        wins = next((count for outcome, count in stats if outcome == 'win'), 0)
        losses = next((count for outcome, count in stats if outcome == 'loss'), 0)
        draws = next((count for outcome, count in stats if outcome == 'draw'), 0)
        
        total_games = wins + losses + draws
        win_rate = (wins / total_games * 100) if total_games > 0 else 0

        return {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": round(win_rate, 2)
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    
# User Endpoints

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    try:
        result = await db.execute(
            select(SQLUser).filter(SQLUser.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        now = datetime.now(UTC)
        new_user = SQLUser(
            user_id=uuid4(),
            email=user_data.email,
            full_name=user_data.full_name,
            google_id=user_data.google_id,
            picture=user_data.picture,
            created_at=now,
            last_login=now
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(SQLUser).filter(SQLUser.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: dict,
    db: AsyncSession = Depends(get_async_db)
):
    try:
        result = await db.execute(
            select(SQLUser).filter(SQLUser.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        allowed_fields = {"full_name", "picture"}
        update_data = {k: v for k, v in user_update.items() if k in allowed_fields}
        
        for key, value in update_data.items():
            setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))