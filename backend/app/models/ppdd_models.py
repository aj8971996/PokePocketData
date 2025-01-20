from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from uuid import UUID

# Base Models
class Ability(BaseModel):
    """Base model for all abilities"""
    ability_id: UUID
    name: str

class PokemonAbility(BaseModel):
    """Model for Pokemon-specific abilities"""
    ability_ref: UUID  # References ability_id from Ability
    energy_cost: dict
    ability_effect: str
    damage: Optional[int] = Field(ge=0)  # Ensure damage is non-negative

class SupportAbility(BaseModel):
    """Model for Support card abilities"""
    ability_ref: UUID  # References ability_id from Ability
    support_type: Literal['Trainer', 'Item']
    effect_description: str

# Card Models
class Card(BaseModel):
    """Base model for all cards"""
    card_id: UUID
    name: str
    set_name: str
    collection_number: str
    rarity: Literal['1 Diamond', '2 Diamond', '3 Diamond', 
                    '4 Diamond', '1 Star', '2 Star', '3 Star', 
                    'Crown']
    image_url: Optional[str]

class PokemonCard(BaseModel):
    """Model for Pokemon cards"""
    card_ref: UUID  # References card_id from Card
    hp: int = Field(gt=0)  # HP must be positive
    type: str  # Consider making this a Literal with valid Pokémon types
    stage: Literal['Basic', 'Stage 1', 'Stage 2']
    evolves_from: Optional[str]
    abilities: List[PokemonAbility]
    weakness: Optional[dict]
    retreat_cost: int = Field(ge=0)  # Retreat cost can't be negative

class TrainerCard(BaseModel):
    """Model for Trainer cards"""
    card_ref: UUID  # References card_id from Card
    abilities: List[SupportAbility]

# Deck Model
class Deck(BaseModel):
    """Model for a deck of cards"""
    deck_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    owner_id: UUID
    cards: List[UUID]  # List of card_id references
    description: Optional[str]
    is_active: bool

    @validator('cards')
    def validate_deck_size(cls, cards):
        if len(cards) != 20:
            raise ValueError('Deck must contain exactly 20 cards')
        return cards
    
    @validator('updated_at')
    def validate_updated_at(cls, updated_at, values):
        if 'created_at' in values and updated_at < values['created_at']:
            raise ValueError('updated_at cannot be earlier than created_at')
        return updated_at

# Game Models
class GameDetails(BaseModel):
    """Model for storing detailed game information"""
    game_details_id: UUID
    opponents_points: int = Field(ge=0)  # Points can't be negative
    player_points: int = Field(ge=0)
    date_played: datetime
    turns_played: int = Field(gt=0)  # Must have at least 1 turn
    player_deck_used: UUID  # References deck_id
    opponent_name: str
    opponent_deck_type: Optional[str]
    notes: Optional[str]

    @root_validator
    def validate_points(cls, values):
        if 'opponents_points' in values and 'player_points' in values:
            if values['opponents_points'] + values['player_points'] > 6:  # Maximum prize cards
                raise ValueError('Total points cannot exceed 6')
        return values

class GameRecord(BaseModel):
    """Model for tracking game outcomes"""
    game_record_id: UUID
    player_id: UUID
    game_details_ref: UUID  # References game_details_id
    outcome: Literal['win', 'loss', 'draw']
    ranking_change: Optional[int]

    class Config:
        """Configuration for model behaviors"""
        allow_population_by_field_name = True
        arbitrary_types_allowed = True