# PokéPocketData Backend API

## Overview

PokéPocketData is a comprehensive FastAPI-based backend service for managing Pokémon Trading Card Game (TCG) data. The system provides robust APIs for card management, deck building, game record tracking, and player statistics.

## Core Features

- **Card Management**: Full CRUD operations for Pokémon and Trainer cards with detailed attributes
- **Deck Building**: Create and manage 20-card decks with validation rules
- **Game Records**: Track game outcomes, statistics, and player rankings
- **User Management**: OAuth2 authentication with Google
- **Data Validation**: Comprehensive validation using Pydantic models
- **Async Support**: Full async/await pattern implementation
- **Database Migration**: Built-in database initialization and table management
- **Comprehensive Testing**: Unit, integration, and validation testing suite

## Tech Stack

- **Framework**: FastAPI 0.100+
- **Database**: MySQL 8.0+ with async SQLAlchemy 2.0
- **Authentication**: OAuth2 with Google
- **Validation**: Pydantic v2
- **Testing**: pytest with async support
- **Documentation**: OpenAPI (Swagger) and ReDoc

## Project Structure

```
backend/
├── app/
│   ├── database/          # Database models and configuration
│   │   ├── migrations/    # Database migrations
│   │   ├── async_session.py
│   │   ├── base.py       # SQLAlchemy base setup
│   │   ├── db_config.py  # Database configuration
│   │   └── sql_models.py # SQLAlchemy models
│   ├── models/           # Data models
│   │   ├── pydantic_models.py
│   │   └── schemas.py
│   ├── routers/          # API endpoints
│   │   ├── auth.py      # Authentication routes
│   │   └── ppdd_router.py # Main application routes
│   └── main.py          # Application entry point
├── tests/               # Test suite
└── requirements.txt
```

## Installation

1. Clone the repository and set up the environment:
```bash
git clone <repository-url>
cd pokepocketdata/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Create .env file in backend/app/database
cp .env.example .env

# Required variables:
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pokepocketdata
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret
```

3. Initialize the database:
```bash
python -m app.database.base
```

4. Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

### Authentication

```http
POST /api/v1/auth/google/callback
```
Handles Google OAuth2 authentication and returns JWT token.

### Card Management

#### Create Pokémon Card
```http
POST /api/v1/cards/pokemon

{
    "name": "Pikachu",
    "set_name": "Genetic Apex (A1)",
    "pack_name": "(A1) Pikachu",
    "collection_number": "001",
    "rarity": "1 Diamond",
    "hp": 60,
    "type": "Electric",
    "stage": "Basic",
    "weakness": "Fighting",
    "retreat_cost": 1,
    "abilities": [
        {
            "ability_ref": "uuid",
            "energy_cost": {"Electric": 1},
            "ability_effect": "Thunder Shock",
            "damage": 20
        }
    ]
}
```

#### Create Trainer Card
```http
POST /api/v1/cards/trainer

{
    "name": "Potion",
    "set_name": "Genetic Apex (A1)",
    "pack_name": "(A1) Pikachu",
    "collection_number": "020",
    "rarity": "1 Star",
    "abilities": [
        {
            "ability_ref": "uuid",
            "support_type": "Item",
            "effect_description": "Heal 30 damage from one of your Pokémon"
        }
    ]
}
```

### Deck Management

#### Create Deck
```http
POST /api/v1/decks/

{
    "name": "Electric Deck",
    "owner_id": "user_uuid",
    "description": "Competitive electric deck",
    "cards": ["card_uuid1", "card_uuid2", ...]  // Exactly 20 cards required
}
```

### Game Records

#### Record Game
```http
POST /api/v1/games/

{
    "game_data": {
        "opponents_points": 2,
        "player_points": 3,
        "date_played": "2024-01-25T12:00:00Z",
        "turns_played": 10,
        "player_deck_used": "deck_uuid",
        "opponent_name": "Player2",
        "opponent_deck_type": "Fire"
    },
    "game_record_data": {
        "player_id": "user_uuid",
        "outcome": "WIN",
        "ranking_change": 10
    }
}
```

## Data Validation Rules

- **Deck Construction**: 
  - Exactly 20 cards per deck
  - Maximum 2 copies of any single card
  - Cards must exist in the database

- **Game Records**:
  - Total points cannot exceed 6
  - Valid outcomes: WIN, LOSS, DRAW
  - Turns played must be greater than 0

- **Cards**:
  - Collection numbers must be unique within a set
  - Stage 1 and 2 Pokémon must specify evolves_from
  - HP must be greater than 0
  - Pack name must match set name (A1/A1a)

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_integration.py

# Run with coverage
pytest --cov=app tests/
```

## Development Guidelines

1. **Database Migrations**:
   - Add new models to sql_models.py
   - Run initialization: `python -m app.database.base`

2. **Error Handling**:
   - Use appropriate HTTP status codes
   - Include detailed error messages in responses
   - Log errors with proper logging levels

3. **Authentication**:
   - All endpoints except health check require authentication
   - Use JWT tokens for session management
   - Implement proper token refresh mechanism

4. **API Versioning**:
   - All endpoints are prefixed with /api/v1
   - Maintain backward compatibility within versions

### Production Considerations

1. **Security**:
   - Enable CORS for production domains only
   - Use secure session configuration
   - Implement rate limiting
   - Enable HTTPS

2. **Performance**:
   - Configure appropriate connection pool settings
   - Implement caching where appropriate
   - Monitor database query performance

3. **Monitoring**:
   - Set up comprehensive logging
   - Implement health checks
   - Monitor system metrics

4. **Backup**:
   - Regular database backups
   - Implement disaster recovery procedures

## License

This project is licensed under the MIT License - see the LICENSE file for details.