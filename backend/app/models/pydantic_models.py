from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator, EmailStr
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

    @model_validator(mode='after')
    def validate_set_and_pack_names(self) -> 'Card':
        set_name = self.set_name
        pack_name = self.pack_name
            
        # Check if A1a or A1 for set_name
        is_a1a = 'A1a' in set_name
            
        # Check if pack_name matches the set designation
        if is_a1a and '(A1a)' not in pack_name:
            raise ValueError('Pack must be from A1a set if set_name is Mythical Island (A1a)')
        elif not is_a1a and '(A1)' not in pack_name:
            raise ValueError('Pack must be from A1 set if set_name is Genetic Apex (A1)')
        
        return self

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

# Deck Models
class DeckCard(BaseModel):
    """Model for cards in a deck"""
    deck_id: UUID
    card_id: UUID

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

    @model_validator(mode='after')
    def validate_deck_size(self) -> 'Deck':
        if len(self.cards) != 20:
            raise ValueError('Deck must contain exactly 20 cards')
        return self
    
    @model_validator(mode='after')
    def validate_updated_at(self) -> 'Deck':
        if self.updated_at < self.created_at:
            raise ValueError('updated_at cannot be earlier than created_at')
        return self

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

    @model_validator(mode='after')
    def validate_points(self) -> 'GameDetails':
        if self.opponents_points + self.player_points > 6:  # Maximum prize cards
            raise ValueError('Total points cannot exceed 6')
        return self

class GameRecord(BaseModel):
    """Model for tracking game outcomes"""
    game_record_id: UUID
    player_id: UUID
    game_details_ref: UUID  # References game_details_id
    outcome: Literal['win', 'loss', 'draw']
    ranking_change: Optional[int]

    class Config:
        """Configuration for model behaviors"""
        arbitrary_types_allowed = True


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    picture: Optional[str] = None

class UserCreate(UserBase):
    google_id: str

class UserResponse(UserBase):
    user_id: UUID
    is_active: bool
    created_at: datetime
    last_login: datetime

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"