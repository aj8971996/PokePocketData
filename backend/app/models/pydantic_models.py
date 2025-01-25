from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator, EmailStr
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os
from pathlib import Path
from uuid import UUID
# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
from app.database.sql_models import Card as SQLCard

# ===============================
# Base/Common Models
# ===============================

class BaseModelConfig(BaseModel):
    """Base configuration for all models that need SQLAlchemy integration"""
    model_config = {
        "from_attributes": True
    }

class Ability(BaseModel):
    """Base model for all abilities"""
    ability_id: UUID
    name: str

class PokemonAbility(BaseModel):
    """Model for Pokemon-specific abilities"""
    ability_ref: UUID
    energy_cost: dict
    ability_effect: str
    damage: Optional[int] = Field(ge=0)

class SupportAbility(BaseModel):
    """Model for Support card abilities"""
    ability_ref: UUID
    support_type: Literal['Trainer', 'Item']
    effect_description: str

# ===============================
# Card Base Models
# ===============================

class CardBase(BaseModel):
    """Base schema for all card operations"""
    name: str
    set_name: Literal['Genetic Apex (A1)', 'Mythical Island (A1a)']
    pack_name: Literal['(A1) Charizard', '(A1) Pikachu', '(A1) Mewtwo', '(A1a) Mew']
    collection_number: str
    rarity: Literal['1 Diamond', '2 Diamond', '3 Diamond', 
                    '4 Diamond', '1 Star', '2 Star', '3 Star', 
                    'Crown', 'Promo']
    image_url: Optional[str] = None

    @model_validator(mode='after')
    def validate_set_and_pack_names(self) -> 'CardBase':
        is_a1a = 'A1a' in self.set_name
        if is_a1a and '(A1a)' not in self.pack_name:
            raise ValueError('Pack must be from A1a set if set_name is Mythical Island (A1a)')
        elif not is_a1a and '(A1)' not in self.pack_name:
            raise ValueError('Pack must be from A1 set if set_name is Genetic Apex (A1)')
        return self

# ===============================
# Create/Input Models
# ===============================

class CardCreate(CardBase):
    """Schema for creating a new card"""
    pass

class PokemonCardCreate(CardBase):
    """Schema for creating a Pokemon card"""
    hp: int = Field(gt=0)
    type: Literal['Fire', 'Water', 'Grass', 'Metal',
                  'Electric', 'Colorless', 'Dragon',
                  'Fighting', 'Psychic', 'Darkness']
    stage: Literal['Basic', 'Stage 1', 'Stage 2']
    evolves_from: Optional[str]
    abilities: List[PokemonAbility]
    weakness: Literal['Fire', 'Water', 'Grass', 'Metal',
                     'Electric', 'Colorless', 'Dragon',
                     'Fighting', 'Psychic', 'Darkness', 'None']
    retreat_cost: int = Field(ge=0)

    @model_validator(mode='after')
    def validate_evolution(self) -> 'PokemonCardCreate':
        if self.stage in ['Stage 1', 'Stage 2'] and not self.evolves_from:
            raise ValueError(f'{self.stage} Pokemon must specify evolves_from')
        if self.stage == 'Basic' and self.evolves_from:
            raise ValueError('Basic Pokemon cannot evolve from another Pokemon')
        return self

class TrainerCardCreate(CardBase):
    """Schema for creating a Trainer card"""
    abilities: List[SupportAbility]

class DeckCreate(BaseModel):
    """Schema for creating a deck"""
    name: str
    owner_id: UUID
    description: Optional[str] = None
    cards: List[UUID]

    @model_validator(mode='after')
    def validate_deck_rules(self) -> 'DeckCreate':
        if len(self.cards) != 20:
            raise ValueError('Deck must contain exactly 20 cards')

        # Get database session and query card names
        card_names = {}
        for card_id in self.cards:
            # Count occurrences by ID first
            if card_id not in card_names:
                card_names[card_id] = 1
            else:
                card_names[card_id] += 1
                if card_names[card_id] > 2:
                    raise ValueError(f'Deck cannot contain more than 2 copies of the same card')
        return self

class GameDetailsCreate(BaseModel):
    """Schema for creating game details"""
    opponents_points: int = Field(ge=0)
    player_points: int = Field(ge=0)
    date_played: datetime
    turns_played: int = Field(gt=0)
    player_deck_used: UUID
    opponent_name: str
    opponent_deck_type: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode='after')
    def validate_points(self) -> 'GameDetailsCreate':
        if self.opponents_points + self.player_points > 6:
            raise ValueError('Total points cannot exceed 6')
        return self

class GameRecordCreate(BaseModel):
    """Schema for creating a game record"""
    player_id: UUID
    outcome: str = Field(description="Must be one of: win, loss, draw", pattern="^(win|loss|draw)$")
    ranking_change: Optional[int] = None

class UserCreate(BaseModelConfig):
    """Schema for creating a user"""
    email: EmailStr
    full_name: str
    picture: Optional[str] = None
    google_id: str

# ===============================
# Update Models
# ===============================

class CardUpdate(BaseModel):
    """Schema for updating a card"""
    name: Optional[str] = None
    image_url: Optional[str] = None

class DeckUpdate(BaseModel):
    """Schema for updating a deck"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    cards: Optional[List[UUID]] = None

    @model_validator(mode='after')
    def validate_deck_rules(self) -> 'DeckUpdate':
        if self.cards is not None:
            if len(self.cards) != 20:
                raise ValueError('Deck must contain exactly 20 cards')

            # Check for duplicates
            card_names = {}
            for card_id in self.cards:
                if card_id not in card_names:
                    card_names[card_id] = 1
                else:
                    card_names[card_id] += 1
                    if card_names[card_id] > 2:
                        raise ValueError(f'Deck cannot contain more than 2 copies of the same card')
        return self

# ===============================
# Response Models
# ===============================

class CardResponse(CardBase, BaseModelConfig):
    """Schema for card responses"""
    card_id: UUID

class PokemonAbilityResponse(BaseModelConfig):
    """Schema for Pokemon ability responses"""
    ability_id: UUID
    ability_ref: UUID
    energy_cost: dict
    ability_effect: str
    damage: Optional[int] = None
    
class PokemonCardResponse(CardResponse):
    """Schema for Pokemon card responses"""
    hp: int
    type: Literal['Fire', 'Water', 'Grass', 'Metal',
                  'Electric', 'Colorless', 'Dragon',
                  'Fighting', 'Psychic', 'Darkness']
    stage: Literal['Basic', 'Stage 1', 'Stage 2']
    evolves_from: Optional[str]
    abilities: List[PokemonAbilityResponse]
    weakness: Literal['Fire', 'Water', 'Grass', 'Metal',
                     'Electric', 'Colorless', 'Dragon',
                     'Fighting', 'Psychic', 'Darkness', 'None']
    retreat_cost: int



class TrainerCardResponse(CardResponse):
    """Schema for Trainer card responses"""
    abilities: List[SupportAbility]

class DeckResponse(BaseModelConfig):
    """Schema for deck responses"""
    deck_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    owner_id: UUID
    cards: List[CardResponse]  # Changed from List[UUID] to include full card details
    description: Optional[str]
    is_active: bool

class GameDetailsResponse(BaseModelConfig):
    """Schema for game details responses"""
    game_details_id: UUID
    opponents_points: int
    player_points: int
    date_played: datetime
    turns_played: int
    player_deck_used: UUID
    opponent_name: str
    opponent_deck_type: Optional[str]
    notes: Optional[str]

class GameRecordResponse(BaseModelConfig):
    """Schema for game record responses"""
    game_record_id: UUID
    player_id: UUID
    game_details_ref: UUID
    outcome: Literal['win', 'loss', 'draw']
    ranking_change: Optional[int]
    game_details: GameDetailsResponse

class UserResponse(BaseModelConfig):
    """Schema for user responses"""
    user_id: UUID
    email: EmailStr
    full_name: str
    picture: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: datetime

class TokenResponse(BaseModel):
    """Schema for token responses"""
    access_token: str
    token_type: str = "bearer"