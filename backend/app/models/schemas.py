from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from uuid import UUID
from datetime import datetime, UTC

# Ability Schemas
class AbilityBase(BaseModel):
    """Base schema for ability creation"""
    name: str

class PokemonAbilityCreate(BaseModel):
    """Schema for creating Pokemon abilities"""
    ability_ref: UUID
    energy_cost: dict
    ability_effect: str
    damage: Optional[int] = Field(ge=0)

class SupportAbilityCreate(BaseModel):
    """Schema for creating Support abilities"""
    ability_ref: UUID
    support_type: Literal['Trainer', 'Item']
    effect_description: str

# Card Schemas
class CardBase(BaseModel):
    """Base schema for all cards"""
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
            is_a1a = 'A1a' in set_name
            if is_a1a and '(A1a)' not in pack_name:
                raise ValueError('Pack must be from A1a set if set_name is Mythical Island (A1a)')
            elif not is_a1a and '(A1)' not in pack_name:
                raise ValueError('Pack must be from A1 set if set_name is Genetic Apex (A1)')
        return values

class CardCreate(CardBase):
    """Schema for creating a base card"""
    pass

class CardUpdate(BaseModel):
    """Schema for updating a card"""
    name: Optional[str] = None
    image_url: Optional[str] = None

class PokemonCardCreate(CardBase):
    """Schema for creating a Pokemon card"""
    hp: int = Field(gt=0)
    type: Literal['Fire', 'Water', 'Grass', 'Metal',
                  'Electric', 'Colorless', 'Dragon',
                  'Fighting', 'Psychic', 'Darkness']
    stage: Literal['Basic', 'Stage 1', 'Stage 2']
    evolves_from: Optional[str]
    abilities: List[PokemonAbilityCreate]
    weakness: Literal['Fire', 'Water', 'Grass', 'Metal',
                     'Electric', 'Colorless', 'Dragon',
                     'Fighting', 'Psychic', 'Darkness', 'None']
    retreat_cost: int = Field(ge=0)

class TrainerCardCreate(CardBase):
    """Schema for creating a Trainer card"""
    abilities: List[SupportAbilityCreate]

# Deck Schemas
class DeckBase(BaseModel):
    """Base schema for decks"""
    name: str
    description: Optional[str] = None
    is_active: bool = True

class DeckCreate(DeckBase):
    """Schema for creating a deck"""
    owner_id: UUID
    cards: List[UUID]

    @validator('cards')
    def validate_deck_size(cls, cards):
        if len(cards) != 20:
            raise ValueError('Deck must contain exactly 20 cards')
        return cards

class DeckUpdate(BaseModel):
    """Schema for updating a deck"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    cards: Optional[List[UUID]] = None

    @validator('cards')
    def validate_deck_size(cls, cards):
        if cards is not None and len(cards) != 20:
            raise ValueError('Deck must contain exactly 20 cards')
        return cards

# Game Schemas
class GameDetailsCreate(BaseModel):
    """Schema for creating game details"""
    opponents_points: int = Field(ge=0)
    player_points: int = Field(ge=0)
    date_played: datetime = Field(default_factory=lambda: datetime.now(UTC))  # Updated to use UTC
    turns_played: int = Field(gt=0)
    player_deck_used: UUID
    opponent_name: str
    opponent_deck_type: Optional[str] = None
    notes: Optional[str] = None

    @root_validator
    def validate_points(cls, values):
        if 'opponents_points' in values and 'player_points' in values:
            if values['opponents_points'] + values['player_points'] > 6:
                raise ValueError('Total points cannot exceed 6')
        return values

class GameRecordCreate(BaseModel):
    """Schema for creating a game record"""
    player_id: UUID
    outcome: Literal['win', 'loss', 'draw']
    ranking_change: Optional[int] = None

# Response Schemas
class CardResponse(CardBase):
    """Schema for card responses"""
    card_id: UUID

    class Config:
        orm_mode = True

class PokemonCardResponse(CardResponse):
    """Schema for Pokemon card responses"""
    hp: int
    type: str
    stage: str
    evolves_from: Optional[str]
    abilities: List[PokemonAbilityCreate]
    weakness: str
    retreat_cost: int

    class Config:
        orm_mode = True

class DeckResponse(DeckBase):
    """Schema for deck responses"""
    deck_id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    cards: List[CardResponse]

    class Config:
        orm_mode = True

class GameRecordResponse(BaseModel):
    """Schema for game record responses"""
    game_record_id: UUID
    player_id: UUID
    game_details: GameDetailsCreate
    outcome: str
    ranking_change: Optional[int]

    class Config:
        orm_mode = True