from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import logging

from ..database import get_db
from ..models.pydantic_models import (
    Card, PokemonCard, TrainerCard, Deck, GameDetails, GameRecord,
    DeckCard, PokemonAbility, SupportAbility
)
from ..models.schemas import (
    CardCreate, CardUpdate, PokemonCardCreate, TrainerCardCreate,
    DeckCreate, DeckUpdate, GameDetailsCreate, GameRecordCreate
)

# Set up logger
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

@router.post("/cards/pokemon", response_model=PokemonCard)
async def create_pokemon_card(
    card_data: PokemonCardCreate,
    db: Session = Depends(get_db)
):
    """Create a new Pokemon card with associated base card"""
    logger.info(f"Attempting to create Pokemon card: {card_data.name}")
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
        await db.flush()
        logger.debug(f"Base card created with ID: {new_card.card_id}")

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
        logger.debug("Pokemon card details added")

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

@router.get("/cards/{card_id}", response_model=Card)
async def get_card(
    card_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific card by ID"""
    logger.info(f"Attempting to retrieve card with ID: {card_id}")
    card = await db.query(Card).filter(Card.card_id == card_id).first()
    if not card:
        logger.warning(f"Card not found with ID: {card_id}")
        raise HTTPException(status_code=404, detail="Card not found")
    logger.debug(f"Successfully retrieved card: {card.name}")
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
    logger.info("Fetching cards with filters")
    logger.debug(f"Filters - set_name: {set_name}, pack_name: {pack_name}, rarity: {rarity}, skip: {skip}, limit: {limit}")
    
    query = db.query(Card)
    
    if set_name:
        query = query.filter(Card.set_name == set_name)
    if pack_name:
        query = query.filter(Card.pack_name == pack_name)
    if rarity:
        query = query.filter(Card.rarity == rarity)
    
    try:
        cards = await query.offset(skip).limit(limit).all()
        logger.debug(f"Retrieved {len(cards)} cards")
        return cards
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching cards: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/decks/", response_model=Deck)
async def create_deck(
    deck_data: DeckCreate,
    db: Session = Depends(get_db)
):
    """Create a new deck"""
    logger.info(f"Creating new deck: {deck_data.name}")
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
        logger.debug(f"Created base deck with ID: {new_deck.deck_id}")

        # Add cards to deck
        for card_id in deck_data.cards:
            deck_card = DeckCard(
                deck_id=new_deck.deck_id,
                card_id=card_id
            )
            db.add(deck_card)
        logger.debug(f"Added {len(deck_data.cards)} cards to deck")

        await db.commit()
        logger.info(f"Successfully created deck: {deck_data.name}")
        return new_deck
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating deck: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/decks/{deck_id}", response_model=Deck)
async def get_deck(
    deck_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific deck by ID"""
    logger.info(f"Fetching deck with ID: {deck_id}")
    deck = await db.query(Deck).filter(Deck.deck_id == deck_id).first()
    if not deck:
        logger.warning(f"Deck not found with ID: {deck_id}")
        raise HTTPException(status_code=404, detail="Deck not found")
    logger.debug(f"Successfully retrieved deck: {deck.name}")
    return deck

@router.put("/decks/{deck_id}", response_model=Deck)
async def update_deck(
    deck_id: UUID,
    deck_data: DeckUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific deck"""
    logger.info(f"Updating deck with ID: {deck_id}")
    try:
        deck = await db.query(Deck).filter(Deck.deck_id == deck_id).first()
        if not deck:
            logger.warning(f"Deck not found with ID: {deck_id}")
            raise HTTPException(status_code=404, detail="Deck not found")

        # Update deck attributes
        for key, value in deck_data.dict(exclude_unset=True).items():
            setattr(deck, key, value)
        logger.debug("Updated deck attributes")

        # Update cards if provided
        if deck_data.cards:
            logger.debug(f"Removing existing cards from deck {deck_id}")
            await db.query(DeckCard).filter(DeckCard.deck_id == deck_id).delete()
            
            # Add new cards
            for card_id in deck_data.cards:
                deck_card = DeckCard(deck_id=deck_id, card_id=card_id)
                db.add(deck_card)
            logger.debug(f"Added {len(deck_data.cards)} new cards to deck")

        await db.commit()
        logger.info(f"Successfully updated deck: {deck.name}")
        return deck
    except SQLAlchemyError as e:
        logger.error(f"Database error while updating deck: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/games/", response_model=GameRecord)
async def create_game_record(
    game_data: GameDetailsCreate,
    game_record_data: GameRecordCreate,
    db: Session = Depends(get_db)
):
    """Create a new game record with details"""
    logger.info(f"Creating new game record for player: {game_record_data.player_id}")
    try:
        # Create game details
        game_details = GameDetails(**game_data.dict())
        db.add(game_details)
        await db.flush()
        logger.debug(f"Created game details with ID: {game_details.game_details_id}")

        # Create game record
        game_record = GameRecord(
            player_id=game_record_data.player_id,
            game_details_ref=game_details.game_details_id,
            outcome=game_record_data.outcome,
            ranking_change=game_record_data.ranking_change
        )
        db.add(game_record)
        
        await db.commit()
        logger.info(f"Successfully created game record with outcome: {game_record_data.outcome}")
        return game_record
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating game record: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/games/statistics/{player_id}")
async def get_player_statistics(
    player_id: UUID,
    db: Session = Depends(get_db)
):
    """Get player statistics including win/loss ratio"""
    logger.info(f"Fetching statistics for player: {player_id}")
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

        logger.debug(f"Statistics calculated - Total: {total_games}, Wins: {wins}, Losses: {losses}, Draws: {draws}")
        return {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": round(win_rate, 2)
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching player statistics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    logger.debug("Performing health check")
    try:
        # Test database connection
        await db.execute("SELECT 1")
        logger.info("Health check successful")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )