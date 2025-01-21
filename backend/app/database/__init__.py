# app/database/__init__.py
from .base import Base, get_db, init_database, verify_connection
from .db_config import db_config
from .sql_models import (
    User, Card, PokemonCard, TrainerCard, 
    Deck, GameDetails, GameRecord, DeckCard, 
    Ability, PokemonAbility, SupportAbility
)

__all__ = [
    'Base',
    'get_db',
    'init_database',
    'verify_connection',
    'db_config',
    'User',
    'Card',
    'PokemonCard',
    'TrainerCard',
    'Deck',
    'GameDetails',
    'GameRecord',
    'DeckCard',
    'Ability',
    'PokemonAbility',
    'SupportAbility',
]