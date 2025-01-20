from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..models.ppdd_models import (
    Card, PokemonCard, TrainerCard, Deck, GameDetails, GameRecord,
    DeckCard, PokemonAbility, SupportAbility
)
from ..models.schemas import (
    CardCreate, CardUpdate, PokemonCardCreate, TrainerCardCreate,
    DeckCreate, DeckUpdate, GameDetailsCreate, GameRecordCreate
)

router = APIRouter()

# Card Endpoints
@router.post("/cards/pokemon", response_model=PokemonCard)
async def create_pokemon_card(
    card_data: PokemonCardCreate,
    db: Session = Depends(get_db)
):
    """Create a new Pokemon card with associated base card"""
    try:
        # Create base card first
        new_card = Card(
            name=card_data.name,
            set_name=card_data.set_name,
            pack_name=card_data.pack_name,
            collection_number=card_data.collection_number,
            rarity=card_data.rarity,
            image_url=card_data.image_url
        )
        db.add(new_card)
        await db.flush()  # Get the card_id

        # Create Pokemon card
        pokemon_card = PokemonCard(
            card_ref=new_card.card_id,
            hp=card_data.hp,
            type=card_data.type,
            stage=card_data.stage,
            evolves_from=card_data.evolves_from,
            weakness=card_data.weakness,
            retreat_cost=card_data.retreat_cost
        )
        db.add(pokemon_card)

        # Add abilities if provided
        for ability_data in card_data.abilities:
            ability = PokemonAbility(
                pokemon_card_ref=pokemon_card.card_ref,
                ability_ref=ability_data.ability_ref,
                energy_cost=ability_data.energy_cost,
                ability_effect=ability_data.ability_effect,
                damage=ability_data.damage
            )
            db.add(ability)

        await db.commit()
        return pokemon_card
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cards/{card_id}", response_model=Card)
async def get_card(
    card_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific card by ID"""
    card = await db.query(Card).filter(Card.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.get("/cards/", response_model=List[Card])
async def list_cards(
    set_name: Optional[str] = None,
    pack_name: Optional[str] = None,
    rarity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List cards with optional filtering"""
    query = db.query(Card)
    
    if set_name:
        query = query.filter(Card.set_name == set_name)
    if pack_name:
        query = query.filter(Card.pack_name == pack_name)
    if rarity:
        query = query.filter(Card.rarity == rarity)
    
    return await query.offset(skip).limit(limit).all()

# Deck Endpoints
@router.post("/decks/", response_model=Deck)
async def create_deck(
    deck_data: DeckCreate,
    db: Session = Depends(get_db)
):
    """Create a new deck"""
    try:
        # Create deck
        new_deck = Deck(
            name=deck_data.name,
            owner_id=deck_data.owner_id,
            description=deck_data.description,
            is_active=True
        )
        db.add(new_deck)
        await db.flush()

        # Add cards to deck
        for card_id in deck_data.cards:
            deck_card = DeckCard(
                deck_id=new_deck.deck_id,
                card_id=card_id
            )
            db.add(deck_card)

        await db.commit()
        return new_deck
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/decks/{deck_id}", response_model=Deck)
async def get_deck(
    deck_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific deck by ID"""
    deck = await db.query(Deck).filter(Deck.deck_id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

@router.put("/decks/{deck_id}", response_model=Deck)
async def update_deck(
    deck_id: UUID,
    deck_data: DeckUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific deck"""
    try:
        deck = await db.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        # Update deck attributes
        for key, value in deck_data.dict(exclude_unset=True).items():
            setattr(deck, key, value)

        # Update cards if provided
        if deck_data.cards:
            # Remove existing cards
            await db.query(DeckCard).filter(DeckCard.deck_id == deck_id).delete()
            
            # Add new cards
            for card_id in deck_data.cards:
                deck_card = DeckCard(deck_id=deck_id, card_id=card_id)
                db.add(deck_card)

        await db.commit()
        return deck
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Game Record Endpoints
@router.post("/games/", response_model=GameRecord)
async def create_game_record(
    game_data: GameDetailsCreate,
    game_record_data: GameRecordCreate,
    db: Session = Depends(get_db)
):
    """Create a new game record with details"""
    try:
        # Create game details
        game_details = GameDetails(**game_data.dict())
        db.add(game_details)
        await db.flush()

        # Create game record
        game_record = GameRecord(
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
):
    """Get player statistics including win/loss ratio"""
    try:
        stats = await db.query(
            GameRecord.outcome,
            db.func.count(GameRecord.outcome)
        ).filter(
            GameRecord.player_id == player_id
        ).group_by(
            GameRecord.outcome
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

# Health Check Endpoint
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )