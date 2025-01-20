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
    set_name: Literal['Genetic Apex (A1)', 'Mythical Island (A1a)']
    pack_name: Literal['(A1) Charizard', '(A1) Pikachu', '(A1) Mewtwo', '(A1a) Mew']
    collection_number: str
    rarity: Literal['1 Diamond', '2 Diamond', '3 Diamond', 
                    '4 Diamond', '1 Star', '2 Star', '3 Star', 
                    'Crown', 'Promo']
    image_url: Optional[str]

    @root_validator
    def validate_set_and_pack_names(cls, values):
        if 'set_name' in values and 'pack_name' in values:
            set_name = values['set_name']
            pack_name = values['pack_name']
            
            # Check if A1a or A1 for set_name
            is_a1a = 'A1a' in set_name
            
            # Check if pack_name matches the set designation
            if is_a1a and '(A1a)' not in pack_name:
                raise ValueError('Pack must be from A1a set if set_name is Mythical Island (A1a)')
            elif not is_a1a and '(A1)' not in pack_name:
                raise ValueError('Pack must be from A1 set if set_name is Genetic Apex (A1)')
        
        return values

class PokemonCard(BaseModel):
    """Model for Pokemon cards"""
    card_ref: UUID  # References card_id from Card
    hp: int = Field(gt=0)  # HP must be positive
    type: Literal['Fire', 'Water', 'Grass', 'Metal',
                  'Electric', 'Colorless', 'Dragon',
                  'Fighting', 'Psychic', 'Darkness']
    stage: Literal['Basic', 'Stage 1', 'Stage 2']
    evolves_from: Optional[str]
    abilities: List[PokemonAbility]
    weakness: Literal['Fire', 'Water', 'Grass', 'Metal',
                  'Electric', 'Colorless', 'Dragon',
                  'Fighting', 'Psychic', 'Darkness', 'None']
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