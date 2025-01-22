import sys
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

# Get the absolute path of the current file's directory
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent

# Add paths to Python path
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'backend'))

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

# Define base class for SQLAlchemy models
class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

Base = declarative_base(cls=CustomBase)

# Import our config instance
from app.database.db_config import db_config

def init_database():
    """Initialize database if it doesn't exist"""
    try:
        logger.info(f"Checking if database {db_config.DATABASE} exists...")
        
        # Get engine without database specified
        engine = db_config._get_engine(with_database=False)
        
        with engine.connect() as connection:
            # Check if database exists
            result = connection.execute(text(
                f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                f"WHERE SCHEMA_NAME = '{db_config.DATABASE}'"
            ))
            exists = result.fetchone() is not None
            
            if not exists:
                logger.info(f"Creating database {db_config.DATABASE}...")
                # Create database with proper character set
                connection.execute(text(
                    f"CREATE DATABASE {db_config.DATABASE} "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                ))
                logger.info(f"Created database: {db_config.DATABASE}")
            else:
                logger.info(f"Database {db_config.DATABASE} already exists")

        return True
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        return False

def verify_connection():
    """Verify database connection and privileges"""
    try:
        logger.info("Verifying database connection...")
        engine = db_config._get_engine()
        with engine.connect() as connection:
            # Test basic connectivity
            connection.execute(text("SELECT 1"))
            
            # Check necessary privileges
            result = connection.execute(text("SHOW GRANTS"))
            privileges = result.fetchall()
            
            logger.info("Current privileges:")
            for privilege in privileges:
                logger.info(privilege[0])
            
            return True
    except Exception as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False

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
        
        # Get the engine from db_config
        engine = db_config._get_engine()
        
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
        
        # Verify tables after creation
        inspector = inspect(engine)
        tables_after = set(inspector.get_table_names())
        new_tables = tables_after - tables_before
        
        # Log table creation results
        if new_tables:
            logger.info(f"Newly created tables: {new_tables}")
        else:
            logger.info("No new tables were created")
        
        # Verify expected tables
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
        
        # Log schema details
        logger.info("Table schemas:")
        for table_name in tables_after:
            columns = inspector.get_columns(table_name)
            logger.info(f"\nSchema for {table_name}:")
            for column in columns:
                logger.info(f"  {column['name']}: {column['type']}")
        
        logger.info("Successfully completed table creation process")
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e.__dict__)}")
        raise

# Create session factory using engine from db_config
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=db_config._get_engine()
)

def get_db():
    """Dependency for FastAPI to get database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # Initialize database using db_config
        if db_config.create_database():
            # Verify connection
            if db_config.verify_connection():
                # Create tables
                init_tables()
                logger.info("Database initialization completed successfully")
            else:
                logger.error("Failed to verify database connection")
                sys.exit(1)
        else:
            logger.error("Failed to create database")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)