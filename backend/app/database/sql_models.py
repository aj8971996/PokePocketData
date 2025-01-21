from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, Enum, TypeDecorator
from sqlalchemy.types import CHAR, TypeDecorator
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base
import enum

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses MySQL's CHAR(36) as the base type.
    """
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'mysql':
            return str(value)
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return str(value)

# Enum classes for constraints
class PokemonType(str, enum.Enum):
    FIRE = 'Fire'
    WATER = 'Water'
    GRASS = 'Grass'
    METAL = 'Metal'
    ELECTRIC = 'Electric'
    COLORLESS = 'Colorless'
    DRAGON = 'Dragon'
    FIGHTING = 'Fighting'
    PSYCHIC = 'Psychic'
    DARKNESS = 'Darkness'
    NONE = 'None'

class SetName(str, enum.Enum):
    GENETIC_APEX = 'Genetic Apex (A1)'
    MYTHICAL_ISLAND = 'Mythical Island (A1a)'

class PackName(str, enum.Enum):
    CHARIZARD = '(A1) Charizard'
    PIKACHU = '(A1) Pikachu'
    MEWTWO = '(A1) Mewtwo'
    MEW = '(A1a) Mew'

class Rarity(str, enum.Enum):
    DIAMOND_1 = '1 Diamond'
    DIAMOND_2 = '2 Diamond'
    DIAMOND_3 = '3 Diamond'
    DIAMOND_4 = '4 Diamond'
    STAR_1 = '1 Star'
    STAR_2 = '2 Star'
    STAR_3 = '3 Star'
    CROWN = 'Crown'
    PROMO = 'Promo'

class Stage(str, enum.Enum):
    BASIC = 'Basic'
    STAGE_1 = 'Stage 1'
    STAGE_2 = 'Stage 2'

# Base Models
class Ability(Base):
    __tablename__ = 'abilities'

    ability_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(250), nullable=False)

class PokemonAbility(Base):
    __tablename__ = 'pokemon_abilities'

    ability_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    pokemon_card_ref = Column(GUID(), ForeignKey('pokemon_cards.card_ref'))
    ability_ref = Column(GUID(), ForeignKey('abilities.ability_id'))
    energy_cost = Column(JSON, nullable=False)
    ability_effect = Column(String(500), nullable=False)
    damage = Column(Integer)

    # Relationships
    ability = relationship("Ability")
    pokemon_card = relationship("PokemonCard", back_populates="abilities")

class SupportAbility(Base):
    __tablename__ = 'support_abilities'

    ability_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    trainer_card_ref = Column(GUID(), ForeignKey('trainer_cards.card_ref'))
    ability_ref = Column(GUID(), ForeignKey('abilities.ability_id'))
    support_type = Column(Enum('Trainer', 'Item'), nullable=False)
    effect_description = Column(String(500), nullable=False)

    # Relationships
    ability = relationship("Ability")
    trainer_card = relationship("TrainerCard", back_populates="abilities")

# Card Models
class Card(Base):
    __tablename__ = "cards"
    
    card_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    set_name = Column(Enum(SetName), nullable=False)
    pack_name = Column(Enum(PackName), nullable=False)
    collection_number = Column(String(20), nullable=False)
    rarity = Column(Enum(Rarity), nullable=False)
    image_url = Column(String(255))
    
    # Relationships
    pokemon_card = relationship("PokemonCard", back_populates="card", uselist=False)
    trainer_card = relationship("TrainerCard", back_populates="card", uselist=False)

class PokemonCard(Base):
    __tablename__ = "pokemon_cards"
    
    card_ref = Column(GUID(), ForeignKey('cards.card_id'), primary_key=True)
    hp = Column(Integer, nullable=False)
    type = Column(Enum(PokemonType), nullable=False)
    stage = Column(Enum(Stage), nullable=False)
    evolves_from = Column(String(255))
    weakness = Column(Enum(PokemonType), nullable=False)
    retreat_cost = Column(Integer, nullable=False)
    
    # Relationships
    card = relationship("Card", back_populates="pokemon_card")
    abilities = relationship("PokemonAbility", back_populates="pokemon_card")

class TrainerCard(Base):
    __tablename__ = "trainer_cards"

    card_ref = Column(GUID(), ForeignKey('cards.card_id'), primary_key=True)
    
    # Relationships
    card = relationship("Card", back_populates="trainer_card")
    abilities = relationship("SupportAbility", back_populates="trainer_card")

# Deck Models
class Deck(Base):
    __tablename__ = "decks"

    deck_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(GUID(), nullable=False)
    description = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    deck_cards = relationship("DeckCard", back_populates="deck")

class DeckCard(Base):
    __tablename__ = "deck_cards"

    deck_id = Column(GUID(), ForeignKey('decks.deck_id'), primary_key=True)
    card_id = Column(GUID(), ForeignKey('cards.card_id'), primary_key=True)
    
    # Relationships
    deck = relationship("Deck", back_populates="deck_cards")
    card = relationship("Card")

# Game Models
class GameDetails(Base):
    __tablename__ = "game_details"

    game_details_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    opponents_points = Column(Integer, nullable=False)
    player_points = Column(Integer, nullable=False)
    date_played = Column(DateTime, nullable=False)
    turns_played = Column(Integer, nullable=False)
    player_deck_used = Column(GUID(), ForeignKey('decks.deck_id'))
    opponent_name = Column(String(255), nullable=False)
    opponent_deck_type = Column(String(255))
    notes = Column(String(1000))

    # Relationships
    game_record = relationship("GameRecord", back_populates="game_details", uselist=False)
    deck = relationship("Deck")

class GameRecord(Base):
    __tablename__ = "game_records"

    game_record_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    player_id = Column(GUID(), nullable=False)
    game_details_ref = Column(GUID(), ForeignKey('game_details.game_details_id'))
    outcome = Column(Enum('win', 'loss', 'draw'), nullable=False)
    ranking_change = Column(Integer)

    # Relationships
    game_details = relationship("GameDetails", back_populates="game_record")