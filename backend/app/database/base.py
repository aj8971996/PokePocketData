import sys
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import os

# Get the absolute path of the current file's directory
current_dir = Path(__file__).resolve().parent

# Get the project root directory (two levels up from current file)
project_root = current_dir.parent.parent

# Add both the project root and the backend directory to Python path
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'backend'))

# Now we can import our local modules
try:
    from sqlalchemy import create_engine, MetaData, event, text, inspect
    from sqlalchemy.orm import declarative_base, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy_utils import database_exists, create_database
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    raise ImportError(
        "Required packages are not installed. Please install them using: "
        "pip install sqlalchemy sqlalchemy-utils mysql-connector-python python-dotenv"
    )

# In base.py
from sqlalchemy.orm import declarative_base, declared_attr

class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

Base = declarative_base(cls=CustomBase)

# Import our config instance
from app.database.db_config import db_config
# At the top of sql_models.py, remove any existing Base import and add:
from app.database.base import Base

# Configure logging
def setup_logging():
    """Configure logging with both file and console handlers"""
    # Create logs directory if it doesn't exist
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler (rotating log files)
    file_handler = RotatingFileHandler(
        log_dir / 'database.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

def create_db_engine(url, **kwargs):
    """Create database engine with connection pooling and logging"""
    try:
        # Use the masked URL for logging
        masked_url = db_config.get_masked_url() if url == db_config.DATABASE_URL else url.replace(db_config.ENCODED_PASSWORD, "********")
        logger.info(f"Creating engine with URL: {masked_url}")
        
        engine = create_engine(
            url,
            pool_pre_ping=True,  # Enable connection health checks
            pool_size=5,         # Set initial pool size
            max_overflow=10,     # Allow up to 10 connections beyond pool_size
            pool_recycle=3600,   # Recycle connections after 1 hour
            **kwargs
        )
        
        # Set up event listeners for connection monitoring
        @event.listens_for(engine, 'connect')
        def receive_connect(dbapi_connection, connection_record):
            logger.info('Database connection established')

        @event.listens_for(engine, 'checkout')
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug('Database connection checked out from pool')

        @event.listens_for(engine, 'checkin')
        def receive_checkin(dbapi_connection, connection_record):
            logger.debug('Database connection checked in to pool')

        return engine
    except Exception as e:
        logger.error(f"Error creating engine: {str(e)}")
        raise

# Initialize engines using URLs from config
try:
    # Create engine without database for initialization
    engine_no_db = create_db_engine(db_config.DATABASE_URL_NO_DB)
    
    # Create main engine with database
    engine = create_db_engine(db_config.DATABASE_URL)
except Exception as e:
    logger.error(f"Failed to create database engines: {str(e)}")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_connection():
    """Verify database connection is working"""
    try:
        logger.info("Verifying database connection...")
        session = SessionLocal()
        try:
            # Check basic connectivity
            result = session.execute(text("SELECT 1")).fetchone()
            logger.info(f"Connection test result: {result}")
            
            # Check CREATE privileges
            result = session.execute(text("SHOW GRANTS")).fetchall()
            logger.info("User privileges:")
            for grant in result:
                logger.info(grant[0])
                
            return True
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False

def init_database():
    """Initialize database if it doesn't exist"""
    try:
        logger.info(f"Checking if database {db_config.DATABASE} exists...")
        if not database_exists(db_config.DATABASE_URL):
            logger.info(f"Creating database {db_config.DATABASE}...")
            create_database(db_config.DATABASE_URL)
            logger.info(f"Created database: {db_config.DATABASE}")
        else:
            logger.info(f"Database {db_config.DATABASE} already exists")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        raise

def init_tables():
    """Initialize database tables with detailed logging"""
    try:
        logger.info("Importing SQLAlchemy models...")
        
        # Import the models module first
        from app.database import sql_models
        logger.info("Successfully imported sql_models module")
        
        # Then import individual models
        from app.database.sql_models import (
            Card, PokemonCard, TrainerCard, Deck, GameDetails,
            GameRecord, DeckCard, Ability, PokemonAbility, SupportAbility,
            PokemonType, SetName, PackName, Rarity, Stage
        )
        
        # Debug: Print all imported models and their metadata
        for model in [Card, PokemonCard, TrainerCard, Deck, GameDetails,
                     GameRecord, DeckCard, Ability, PokemonAbility, SupportAbility]:
            logger.info(f"Checking model {model.__name__}:")
            logger.info(f"  Tablename: {getattr(model, '__tablename__', None)}")
            logger.info(f"  Is it subclass of Base? {issubclass(model, Base)}")
            
        # Print metadata tables before creation
        logger.info(f"Base metadata tables before: {Base.metadata.tables.keys()}")
        
        # Force metadata binding
        Base.metadata.bind = engine
        
        # Get list of tables before creation
        inspector = inspect(engine)
        tables_before = set(inspector.get_table_names())
        logger.info(f"Tables before creation: {tables_before}")
        
        # Create tables with explicit schema creation
        logger.info("Creating tables...")
        for model in [Card, PokemonCard, TrainerCard, Deck, GameDetails,
                     GameRecord, DeckCard, Ability, PokemonAbility, SupportAbility]:
            try:
                if hasattr(model, '__table__'):
                    model.__table__.create(bind=engine, checkfirst=True)
                    logger.info(f"Created table for model: {model.__name__}")
                else:
                    logger.warning(f"Model {model.__name__} has no __table__ attribute")
            except Exception as e:
                logger.error(f"Failed to create table for {model.__name__}: {str(e)}")
        
        # Print metadata tables after creation
        logger.info(f"Base metadata tables after: {Base.metadata.tables.keys()}")
        
        # Get list of tables after creation
        inspector = inspect(engine)
        tables_after = set(inspector.get_table_names())
        logger.info(f"Tables after creation: {tables_after}")
        
        # Show new tables
        new_tables = tables_after - tables_before
        if new_tables:
            logger.info(f"Newly created tables: {new_tables}")
        else:
            logger.info("No new tables were created")
        
        # Verify each expected table exists
        expected_tables = {
            'abilities', 'pokemon_abilities', 'support_abilities', 
            'cards', 'pokemon_cards', 'trainer_cards',
            'decks', 'deck_cards', 'game_details', 'game_records'
        }
        
        for table in expected_tables:
            if table in tables_after:
                logger.info(f"Table '{table}' verified")
            else:
                logger.warning(f"Table '{table}' not found in database")
                
        # Log schema details for each table
        logger.info("Table schemas:")
        for table_name in tables_after:
            columns = inspector.get_columns(table_name)
            logger.info(f"\nSchema for {table_name}:")
            for column in columns:
                logger.info(f"  {column['name']}: {column['type']}")
        
        # Try creating all tables at once as a fallback
        if not tables_after:
            logger.info("Attempting to create all tables at once...")
            try:
                Base.metadata.create_all(bind=engine)
                logger.info("Successfully created all tables at once")
            except Exception as e:
                logger.error(f"Failed to create all tables at once: {str(e)}")
        
        logger.info("Successfully completed table creation process")
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e.__dict__)}")
        raise

def get_db():
    """Dependency for FastAPI to get database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # Initialize database
        init_database()
        
        # Verify connection
        if verify_connection():
            # Create tables
            init_tables()
            logger.info("Database initialization completed successfully")
        else:
            logger.error("Failed to verify database connection")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)