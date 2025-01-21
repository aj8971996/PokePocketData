import sys
from pathlib import Path
import pytest
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from fastapi.testclient import TestClient
from typing import Generator, Any

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import our modules
from app.database.base import Base
from app.database.db_config import DatabaseConfig, DatabaseEnvironment
from app.main import app
from app.database.sql_models import User, Card, PokemonCard, TrainerCard, Deck

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create test database config
test_db_config = DatabaseConfig(env=DatabaseEnvironment.TESTING)

def get_test_db_url() -> str:
    """Get test database URL"""
    return test_db_config.TEST_DATABASE_URL

@pytest.fixture(scope="session")
def test_engine():
    """Create engine for test database with logging"""
    test_db_url = get_test_db_url()
    
    # Create test database if it doesn't exist
    if not database_exists(test_db_url):
        create_database(test_db_url)
    
    # Create engine with logging
    engine = create_engine(
        test_db_url,
        pool_pre_ping=True,
        echo=True  # SQL logging for tests
    )
    
    # Add event listeners for debugging
    @event.listens_for(engine, 'connect')
    def receive_connect(dbapi_connection, connection_record):
        logger.info('Test database connection established')
    
    @event.listens_for(engine, 'begin')
    def receive_begin(conn):
        logger.info('Test transaction begin')
    
    # Create all tables
    logger.info("Creating test database tables...")
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up
    logger.info("Dropping test database...")
    Base.metadata.drop_all(bind=engine)
    drop_database(test_db_url)

@pytest.fixture(scope="session")
def TestingSessionLocal(test_engine):
    """Create session factory for test database"""
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
        expire_on_commit=False  # Useful for testing
    )
    return SessionLocal

@pytest.fixture
def db(TestingSessionLocal) -> Generator[Any, Any, None]:
    """Get database session for each test"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def get_test_db():
    """Database dependency override for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db) -> Generator[TestClient, Any, None]:
    """Create test client with database dependency override"""
    from app.database.base import get_db
    
    # Override the database dependency
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()

# Fixture for creating test user
@pytest.fixture
def test_user(db) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        google_id="test123",
        picture="https://example.com/picture.jpg"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Fixture for creating test card
@pytest.fixture
def test_pokemon_card(db) -> PokemonCard:
    """Create a test Pokemon card"""
    card = Card(
        name="Test Pokemon",
        set_name="Genetic Apex (A1)",
        pack_name="(A1) Charizard",
        collection_number="TEST-001",
        rarity="1 Diamond"
    )
    db.add(card)
    db.flush()
    
    pokemon_card = PokemonCard(
        card_ref=card.card_id,
        hp=100,
        type="Fire",
        stage="Basic",
        weakness="Water",
        retreat_cost=2
    )
    db.add(pokemon_card)
    db.commit()
    return pokemon_card

# Fixture for creating test deck
@pytest.fixture
def test_deck(db, test_user) -> Deck:
    """Create a test deck"""
    deck = Deck(
        name="Test Deck",
        owner_id=test_user.user_id,
        description="Test deck for testing",
        is_active=True
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck

# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_database(db):
    """Clean up database after each test"""
    yield
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()