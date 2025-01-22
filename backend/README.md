# PokéPocketData Backend API

## Project Overview

PokéPocketData is a comprehensive API for managing Pokémon card game data, including card management, deck building, and game record tracking.

## Technology Stack

- Framework: FastAPI
- ORM: SQLAlchemy (Async)
- Database: MySQL
- Validation: Pydantic
- Testing: Pytest

## Key Features

- Pokémon Card Management
- Trainer Card Creation
- Deck Building
- Game Record Tracking
- Player Statistics

## API Endpoints

### Card Management

#### Create Pokémon Card
- **Method:** POST
- **Endpoint:** `/api/v1/cards/pokemon`
- **Request Model:** `PokemonCardCreate`
- **Response Model:** `PokemonCardResponse`

#### Create Trainer Card
- **Method:** POST
- **Endpoint:** `/api/v1/cards/trainer`
- **Request Model:** `TrainerCardCreate`
- **Response Model:** `TrainerCardResponse`

#### Get Card Details
- **Method:** GET
- **Endpoint:** `/api/v1/cards/{card_id}`
- **Response Model:** `CardResponse`

#### List Cards
- **Method:** GET
- **Endpoint:** `/api/v1/cards/`
- **Query Parameters:**
  - `set_name`
  - `pack_name`
  - `rarity`
  - `skip`
  - `limit`

### Deck Management

#### Create Deck
- **Method:** POST
- **Endpoint:** `/api/v1/decks/`
- **Request Model:** `DeckCreate`
- **Response Model:** `DeckResponse`

#### Get Deck
- **Method:** GET
- **Endpoint:** `/api/v1/decks/{deck_id}`
- **Response Model:** `DeckResponse`

#### Update Deck
- **Method:** PUT
- **Endpoint:** `/api/v1/decks/{deck_id}`
- **Request Model:** `DeckUpdate`
- **Response Model:** `DeckResponse`

### Game Record Management

#### Create Game Record
- **Method:** POST
- **Endpoint:** `/api/v1/games/`
- **Request Models:** 
  - `GameDetailsCreate`
  - `GameRecordCreate`
- **Response Model:** `GameRecordResponse`

#### Get Player Statistics
- **Method:** GET
- **Endpoint:** `/api/v1/games/statistics/{player_id}`
- **Returns:** Player game statistics

## Validation Rules

### Card Creation
- Set and pack names must correspond
- Pokémon cards require specific type and stage
- Abilities must have valid references

### Deck Creation
- Must contain exactly 20 cards

### Game Records
- Total game points cannot exceed 6
- Supports win/loss/draw outcomes

## Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Configure database in `.env`
5. Run database migrations
6. Start the server: `uvicorn app.main:app --reload`

## Testing

Run tests using pytest:
```bash
pytest backend/tests/
```

