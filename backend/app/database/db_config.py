from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_dotenv():
    """Find the .env file by searching up the directory tree"""
    current_path = Path(__file__).resolve().parent
    
    # Search up to 3 levels up for .env file
    for _ in range(4):
        logger.info(f"Checking for .env in: {current_path}")
        env_file = current_path / '.env'
        if env_file.exists():
            logger.info(f"Found .env file at: {env_file}")
            return env_file
        current_path = current_path.parent
    
    # Also check the current working directory
    cwd = Path.cwd()
    logger.info(f"Checking current working directory: {cwd}")
    env_file = cwd / '.env'
    if env_file.exists():
        logger.info(f"Found .env file at: {env_file}")
        return env_file
    
    return None

# Find and load .env file
env_path = find_dotenv()
if env_path:
    logger.info(f"Loading .env from: {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning("No .env file found in parent directories!")
    logger.info("Searching following paths:")
    logger.info(f"Current file location: {Path(__file__).resolve()}")
    logger.info(f"Current working directory: {Path.cwd()}")

class DatabaseConfig:
    """Database configuration using environment variables"""
    
    def __init__(self):
        # Get and log environment variables
        self.USER = os.getenv("DB_USER")
        self.PASSWORD = os.getenv("DB_PASSWORD")
        self.HOST = os.getenv("DB_HOST")
        self.PORT = os.getenv("DB_PORT")
        self.DATABASE = os.getenv("DB_NAME")
        
        # Log retrieved values (excluding password)
        logger.info("Retrieved configuration values:")
        logger.info(f"USER: {self.USER}")
        logger.info(f"HOST: {self.HOST}")
        logger.info(f"PORT: {self.PORT}")
        logger.info(f"DATABASE: {self.DATABASE}")
        logger.info(f"PASSWORD: {'[SET]' if self.PASSWORD else '[NOT SET]'}")
        
        # Set defaults if values are None
        self.USER = self.USER or "ppdd_api_user"
        self.HOST = self.HOST or "localhost"
        self.PORT = self.PORT or "3306"
        self.DATABASE = self.DATABASE or "pokepocketdata"
        
        if not self.PASSWORD:
            raise ValueError("Database password not found in environment variables")
        
        # Clean the password (remove quotes) and URL encode it
        self.PASSWORD = self.PASSWORD.strip('"').strip("'")
        self.ENCODED_PASSWORD = quote_plus(self.PASSWORD)
        
        # Construct base URL
        self.BASE_URL = f"mysql+mysqlconnector://{self.USER}:{self.ENCODED_PASSWORD}@{self.HOST}:{self.PORT}"
        
        # Construct database URLs
        self.DATABASE_URL = f"{self.BASE_URL}/{self.DATABASE}"
        self.DATABASE_URL_NO_DB = self.BASE_URL
        
    def get_connection_args(self):
        """Get connection arguments as a dictionary"""
        return {
            'user': self.USER,
            'password': self.PASSWORD,  # Use non-encoded password
            'host': self.HOST,
            'port': int(self.PORT),
            'database': self.DATABASE,
        }
    
    def get_masked_url(self):
        """Get the database URL with password masked"""
        return self.DATABASE_URL.replace(self.ENCODED_PASSWORD, "********")

# Create config instance
db_config = DatabaseConfig()

if __name__ == "__main__":
    print("\nDatabase Configuration:")
    print(f"Host: {db_config.HOST}")
    print(f"Port: {db_config.PORT}")
    print(f"Database: {db_config.DATABASE}")
    print(f"User: {db_config.USER}")
    print(f"URL: {db_config.get_masked_url()}")