# app/routers/ppdd_router.py
import sys
from pathlib import Path
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# Get the absolute path of the current file's directory
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'backend'))

from app.database import get_db
from app.database.sql_models import (
    Card as SQLCard,
    PokemonCard as SQLPokemonCard,
    TrainerCard as SQLTrainerCard,
    Deck as SQLDeck,
    GameDetails as SQLGameDetails,
    GameRecord as SQLGameRecord,
    DeckCard as SQLDeckCard,
    PokemonAbility as SQLPokemonAbility,
    SupportAbility as SQLSupportAbility
)
from app.models.pydantic_models import (
    # Create/Update Models
    CardCreate, CardUpdate, 
    PokemonCardCreate, TrainerCardCreate,
    DeckCreate, DeckUpdate, 
    GameDetailsCreate, GameRecordCreate,
    # Response Models
    CardResponse, PokemonCardResponse, TrainerCardResponse,
    DeckResponse, GameDetailsResponse, GameRecordResponse
)

# Define the router
router = APIRouter()
logger = logging.getLogger(__name__)

# Card Endpoints
@router.post("/cards/pokemon", response_model=PokemonCardResponse)
async def create_pokemon_card(
    card_data: PokemonCardCreate,
    db: Session = Depends(get_db)
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
        logger.debug(f"Base card created with ID: {new_card.card_id}")

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
        logger.debug("Pokemon card details added")

        # Add abilities if provided
        for ability_data in card_data.abilities:
            ability = SQLPokemonAbility(
                pokemon_card_ref=pokemon_card.card_ref,
                ability_ref=ability_data.ability_ref,
                energy_cost=ability_data.energy_cost,
                ability_effect=ability_data.ability_effect,
                damage=ability_data.damage
            )
            db.add(ability)
        logger.debug(f"Added {len(card_data.abilities)} abilities to the card")

        await db.commit()
        logger.info(f"Successfully created Pokemon card: {card_data.name}")
        return pokemon_card
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating Pokemon card: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error while creating Pokemon card: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cards/trainer", response_model=TrainerCardResponse)
async def create_trainer_card(
    card_data: TrainerCardCreate,
    db: Session = Depends(get_db)
):
    """Create a new Trainer card"""
    logger.info(f"Attempting to create Trainer card: {card_data.name}")
    try:
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
        
        for ability_data in card_data.abilities:
            ability = SQLSupportAbility(
                trainer_card_ref=trainer_card.card_ref,
                ability_ref=ability_data.ability_ref,
                support_type=ability_data.support_type,
                effect_description=ability_data.effect_description
            )
            db.add(ability)

        await db.commit()
        return trainer_card
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

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

# Deck Endpoints
@router.post("/decks/", response_model=DeckResponse)
async def create_deck(
    deck_data: DeckCreate,
    db: Session = Depends(get_db)
):
    """Create a new deck"""
    logger.info(f"Creating new deck: {deck_data.name}")
    try:
        new_deck = SQLDeck(
            name=deck_data.name,
            owner_id=deck_data.owner_id,
            description=deck_data.description,
            is_active=True
        )
        db.add(new_deck)
        await db.flush()

        for card_id in deck_data.cards:
            deck_card = SQLDeckCard(
                deck_id=new_deck.deck_id,
                card_id=card_id
            )
            db.add(deck_card)

        await db.commit()
        return new_deck
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/decks/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific deck by ID"""
    deck = await db.query(SQLDeck).filter(SQLDeck.deck_id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

@router.put("/decks/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: UUID,
    deck_data: DeckUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific deck"""
    try:
        deck = await db.query(SQLDeck).filter(SQLDeck.deck_id == deck_id).first()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        # Update deck attributes
        for key, value in deck_data.dict(exclude_unset=True).items():
            setattr(deck, key, value)

        if deck_data.cards:
            await db.query(SQLDeckCard).filter(SQLDeckCard.deck_id == deck_id).delete()
            for card_id in deck_data.cards:
                deck_card = SQLDeckCard(deck_id=deck_id, card_id=card_id)
                db.add(deck_card)

        await db.commit()
        return deck
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Game Record Endpoints
@router.post("/games/", response_model=GameRecordResponse)
async def create_game_record(
    game_data: GameDetailsCreate,
    game_record_data: GameRecordCreate,
    db: Session = Depends(get_db)
):
    """Create a new game record with details"""
    try:
        game_details = SQLGameDetails(**game_data.dict())
        db.add(game_details)
        await db.flush()

        game_record = SQLGameRecord(
            player_id=game_record_data.player_id,
            game_details_ref=game_details.game_details_id,
            outcome=game_record_data.outcome,
            ranking_change=game_record_data.ranking_change
        )
        db.add(game_record)
        
        await db.commit()
        return game_record
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