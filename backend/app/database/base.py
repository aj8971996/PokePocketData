# backend/app/database/base.py
import sys
from pathlib import Path
import logging

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

try:
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy_utils import database_exists, create_database
except ImportError:
    raise ImportError(
        "Required packages are not installed. Please install them using: "
        "pip install sqlalchemy sqlalchemy-utils"
    )

from app.database.config import db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create engine without database specified
engine_no_db = create_engine(db_config.DATABASE_URL_NO_DB)

# Create database if it doesn't exist
def init_database():
    if not database_exists(db_config.DATABASE_URL):
        try:
            create_database(db_config.DATABASE_URL)
            logger.info(f"Created database: {db_config.DATABASE}")
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise

# Create engine with database specified
engine = create_engine(db_config.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Create all tables
def init_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created all tables")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

# Optional: Helper function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()