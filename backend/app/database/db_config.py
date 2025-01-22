from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import database_exists as sqlalchemy_database_exists
from sqlalchemy_utils import create_database as sqlalchemy_create_database
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseEnvironment(str, Enum):
    """Database environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class DBCredentials:
    """Database credentials container"""
    user: str
    password: str
    host: str
    port: str
    database: str
    encoded_password: str

    @classmethod
    def from_env(cls, env_prefix: str = "DB", env_type: DatabaseEnvironment = DatabaseEnvironment.DEVELOPMENT) -> 'DBCredentials':
        """Create credentials from environment variables"""
        # Get environment variables with fallbacks
        user = os.getenv(f"{env_prefix}_USER")
        password = os.getenv(f"{env_prefix}_PASSWORD")
        host = os.getenv(f"{env_prefix}_HOST")
        port = os.getenv(f"{env_prefix}_PORT")
        
        # Check for required variables
        if not all([user, password, host, port]):
            missing_vars = []
            if not user: missing_vars.append(f"{env_prefix}_USER")
            if not password: missing_vars.append(f"{env_prefix}_PASSWORD")
            if not host: missing_vars.append(f"{env_prefix}_HOST")
            if not port: missing_vars.append(f"{env_prefix}_PORT")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Get database name with environment-specific suffix for testing
        if env_type == DatabaseEnvironment.TESTING:
            database = os.getenv(f"{env_prefix}_NAME_TEST", "pokepocketdata_test")
        else:
            database = os.getenv(f"{env_prefix}_NAME", "pokepocketdata")
        
        # Clean and encode password
        password = password.strip('"').strip("'")
        encoded_password = quote_plus(password)
        
        return cls(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            encoded_password=encoded_password
        )

class DatabaseConfig:
    """Database configuration using environment variables"""
    
    def __init__(self, env: DatabaseEnvironment = DatabaseEnvironment.DEVELOPMENT):
        """Initialize database configuration"""
        self.env = env
        self._engine = None
        self._load_env_file()
        self.credentials = DBCredentials.from_env(env_type=env)
        self._setup_urls()
        self._log_config()

    def _find_env_file(self) -> Optional[Path]:
        """Find the .env file by searching up the directory tree"""
        # First, try the known location in the database directory
        known_location = Path(__file__).resolve().parent / '.env'
        if known_location.exists():
            return known_location
            
        # If not found, try common locations
        search_paths = [
            Path(__file__).resolve().parent,  # Current directory
            Path(__file__).resolve().parent.parent,  # app directory
            Path(__file__).resolve().parent.parent.parent,  # backend directory
            Path.cwd(),  # Working directory
        ]
        
        for base_path in search_paths:
            logger.debug(f"Searching for .env in: {base_path}")
            env_file = base_path / '.env'
            if env_file.exists():
                return env_file
        
        return None

    def _load_env_file(self) -> None:
        """Load environment variables from .env file"""
        env_file = self._find_env_file()
        if env_file:
            logger.info(f"Loading environment from: {env_file}")
            load_dotenv(dotenv_path=env_file)
            if not os.getenv('DB_USER'):
                logger.warning("Environment loaded but DB_USER not found!")
        else:
            logger.warning("No .env file found in search paths!")
            self._log_search_paths()

    def _log_search_paths(self) -> None:
        """Log paths searched for .env file"""
        logger.info("Searched for .env in:")
        logger.info(f"- Database directory: {Path(__file__).resolve().parent}")
        logger.info(f"- App directory: {Path(__file__).resolve().parent.parent}")
        logger.info(f"- Backend directory: {Path(__file__).resolve().parent.parent.parent}")
        logger.info(f"- Working directory: {Path.cwd()}")

    def _log_config(self) -> None:
        """Log configuration values"""
        logger.info("Database Configuration:")
        logger.info(f"Environment: {self.env.value}")
        logger.info(f"User: {self.credentials.user}")
        logger.info(f"Host: {self.credentials.host}")
        logger.info(f"Port: {self.credentials.port}")
        logger.info(f"Database: {self.credentials.database}")
        logger.info(f"Password status: {'[SET]' if self.credentials.password else '[NOT SET]'}")

    def _setup_urls(self) -> None:
        """Set up database URLs"""
        base_url = (
            f"mysql+mysqlconnector://{self.credentials.user}:"
            f"{self.credentials.encoded_password}@{self.credentials.host}:"
            f"{self.credentials.port}"
        )
        
        self.BASE_URL = base_url
        self.DATABASE_URL = f"{base_url}/{self.credentials.database}"
        self.DATABASE_URL_NO_DB = base_url

    def _get_engine(self, with_database: bool = True) -> Any:
        """Get or create SQLAlchemy engine"""
        if not self._engine or not with_database:
            url = self.DATABASE_URL if with_database else self.DATABASE_URL_NO_DB
            self._engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600
            )
        return self._engine

    def database_exists(self) -> bool:
        """Check if the database exists"""
        try:
            return sqlalchemy_database_exists(self.DATABASE_URL)
        except Exception as e:
            logger.error(f"Error checking database existence: {str(e)}")
            return False

    def create_database(self) -> bool:
        """Create the database if it doesn't exist"""
        try:
            if not self.database_exists():
                logger.info(f"Creating database: {self.credentials.database}")
                sqlalchemy_create_database(self.DATABASE_URL)
                logger.info("Database created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            return False

    def verify_connection(self) -> bool:
        """Verify database connection is working"""
        try:
            engine = self._get_engine()
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("Database connection verified successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection verification failed: {str(e)}")
            return False

    def get_connection_args(self) -> Dict[str, Any]:
        """Get connection arguments as a dictionary"""
        return {
            'user': self.credentials.user,
            'password': self.credentials.password,
            'host': self.credentials.host,
            'port': int(self.credentials.port),
            'database': self.credentials.database,
        }
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on environment"""
        return self.DATABASE_URL

    def get_masked_url(self) -> str:
        """Get the database URL with password masked"""
        return self.get_database_url().replace(self.credentials.encoded_password, "********")
    
    def _get_async_engine(self, with_database: bool = True) -> AsyncEngine:
        """Get or create async SQLAlchemy engine"""
        # Convert sync URL to async URL
        url = (self.DATABASE_URL if with_database else self.DATABASE_URL_NO_DB).replace(
            'mysql+mysqlconnector://', 
            'mysql+aiomysql://'
        )
        
        return create_async_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            echo=self.env == DatabaseEnvironment.DEVELOPMENT
        )

    def get_async_session_maker(self) -> Any:
        """Create an async session maker"""
        async_engine = self._get_async_engine()
        return async_sessionmaker(
            async_engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )

# Create default config instance
db_config = DatabaseConfig()

if __name__ == "__main__":
    # Test the configuration
    config = DatabaseConfig()
    print("\nDatabase Configuration:")
    print(f"Environment: {config.env.value}")
    print(f"Database: {config.credentials.database}")
    print(f"URL: {config.get_masked_url()}")
    
    # Test database operations
    if config.create_database():
        print("Database setup successful")
        if config.verify_connection():
            print("Connection verified successfully")