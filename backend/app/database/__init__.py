# app/database/__init__.py
from .base import Base, get_db, init_tables, SessionLocal
from .db_config import (
    db_config, 
    DatabaseConfig,
    DatabaseEnvironment,
    DBCredentials
)
from .sql_models import (
    User, Card, PokemonCard, TrainerCard, 
    Deck, GameDetails, GameRecord, DeckCard, 
    Ability, PokemonAbility, SupportAbility,
    # Also export enums for external use
    PokemonType, SetName, PackName, Rarity, 
    Stage, SupportType, GameOutcome
)

__all__ = [
    # Base classes and utilities
    'Base',
    'get_db',
    'init_tables',
    'SessionLocal',
    
    # Configuration
    'db_config',
    'DatabaseConfig',
    'DatabaseEnvironment',
    'DBCredentials',
    
    # Models
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
    
    # Enums
    'PokemonType',
    'SetName',
    'PackName',
    'Rarity',
    'Stage',
    'SupportType',
    'GameOutcome'
]