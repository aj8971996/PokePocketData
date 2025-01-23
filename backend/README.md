# PokéPocketData Backend API

## Overview

PokéPocketData is a FastAPI-based API for managing Pokémon card game data, featuring card management, deck building, and game statistics tracking.

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL with async SQLAlchemy
- **Validation**: Pydantic
- **Testing**: Pytest
- **Authentication**: OAuth2 with Google

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Virtual environment tool (venv/conda)

### Installation

1. Clone and setup environment:
```bash
git clone https://github.com/yourusername/pokepocketdata.git
cd pokepocketdata/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
# Create .env file in backend/app/database
cp .env.example .env

# Configure these variables in .env:
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pokepocketdata
```

3. Initialize database:
```bash
python -m app.database.base
```

4. Start server:
```bash
uvicorn app.main:app --reload --port 8000
```

Access API docs at: http://localhost:8000/api/docs

## Development

### Project Structure
```
backend/
├── app/
│   ├── database/         # Database models and config
│   ├── models/          # Pydantic models
│   ├── routers/         # API endpoints
│   └── main.py         # Application entry
├── tests/              # Test suite
└── requirements.txt    # Dependencies
```

### Database Migrations

The project uses SQLAlchemy for schema management:

1. Create new tables:
```python
# Add models to sql_models.py
# Run initialization:
python -m app.database.base
```

2. Reset database:
```bash
python -m app.database.base --reset
```

### Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_integration.py

# With coverage
pytest --cov=app tests/
```

## API Documentation

### Card Management

Create Pokémon cards with abilities, types, and stats:
```python
POST /api/v1/cards/pokemon
{
    "name": "Pikachu",
    "set_name": "Genetic Apex (A1)",
    "pack_name": "(A1) Pikachu",
    "collection_number": "001",
    "rarity": "1 Diamond",
    "hp": 60,
    "type": "Electric",
    "abilities": [...]
}
```

### Deck Management

Create 20-card decks with validation:
```python
POST /api/v1/decks/
{
    "name": "Electric Deck",
    "owner_id": "uuid",
    "cards": ["card_uuid1", ...]  # Exactly 20 cards required
}
```

### Game Records

Track game outcomes and player statistics:
```python
POST /api/v1/games/
{
    "game_data": {
        "opponents_points": 2,
        "player_points": 3,
        "turns_played": 10,
        ...
    },
    "game_record_data": {
        "player_id": "uuid",
        "outcome": "win"
    }
}
```

## Deployment

### Docker Setup

1. Build image:
```bash
docker build -t pokepocketdata-api .
```

2. Run container:
```bash
docker run -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_USER=user \
  -e DB_PASSWORD=pass \
  pokepocketdata-api
```

### Production Considerations

- Use proper connection pooling settings
- Enable CORS for production domains
- Configure logging and monitoring
- Set up health checks
- Use secure session management