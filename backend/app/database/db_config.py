from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

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
        """
        Create credentials from environment variables
        
        Args:
            env_prefix: Prefix for environment variables (default: "DB")
            env_type: Type of environment (development/testing/production)
        
        Returns:
            DBCredentials object with database connection information
        
        Raises:
            ValueError: If required environment variables are missing
        """
        # Get environment variables with fallbacks
        user = os.getenv(f"{env_prefix}_USER", "ppdd_api_user")
        password = os.getenv(f"{env_prefix}_PASSWORD")
        host = os.getenv(f"{env_prefix}_HOST", "localhost")
        port = os.getenv(f"{env_prefix}_PORT", "3306")
        
        # Get database name with environment-specific suffix for testing
        base_db_name = os.getenv(f"{env_prefix}_NAME", "pokepocketdata")
        database = f"{base_db_name}_test" if env_type == DatabaseEnvironment.TESTING else base_db_name
        
        if not password:
            raise ValueError(f"Database password not found in environment variables ({env_prefix}_PASSWORD)")
        
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
        """
        Initialize database configuration
        
        Args:
            env: Database environment type (development/testing/production)
        """
        self.env = env
        self._load_env_file()
        self.credentials = DBCredentials.from_env(env_type=env)
        self._setup_urls()
        self._log_config()

    def _load_env_file(self) -> None:
        """Load environment variables from .env file"""
        env_file = self._find_env_file()
        if env_file:
            logger.info(f"Loading environment from: {env_file}")
            load_dotenv(dotenv_path=env_file)
        else:
            logger.warning("No .env file found")
            self._log_search_paths()

    def _find_env_file(self) -> Optional[Path]:
        """
        Find the .env file by searching up the directory tree and in common locations
        
        Returns:
            Path to .env file if found, None otherwise
        """
        search_paths = [
            Path(__file__).resolve().parent,  # Current directory
            Path.cwd(),                       # Working directory
            Path.home(),                      # Home directory
        ]
        
        # Search each path and its parents
        for base_path in search_paths:
            current_path = base_path
            for _ in range(4):  # Search up to 3 levels up
                env_file = current_path / '.env'
                if env_file.exists():
                    return env_file
                current_path = current_path.parent
        
        return None

    def _log_search_paths(self) -> None:
        """Log paths searched for .env file"""
        logger.info("Searched for .env in:")
        logger.info(f"- Current directory: {Path(__file__).resolve().parent}")
        logger.info(f"- Working directory: {Path.cwd()}")
        logger.info(f"- Home directory: {Path.home()}")

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

    def _log_config(self) -> None:
        """Log configuration values"""
        logger.info("Database Configuration:")
        logger.info(f"Environment: {self.env.value}")
        logger.info(f"User: {self.credentials.user}")
        logger.info(f"Host: {self.credentials.host}")
        logger.info(f"Port: {self.credentials.port}")
        logger.info(f"Database: {self.credentials.database}")
        logger.info(f"Password status: {'[SET]' if self.credentials.password else '[NOT SET]'}")

    def get_connection_args(self) -> Dict[str, Any]:
        """
        Get connection arguments as a dictionary
        
        Returns:
            Dictionary with database connection parameters
        """
        return {
            'user': self.credentials.user,
            'password': self.credentials.password,
            'host': self.credentials.host,
            'port': int(self.credentials.port),
            'database': self.credentials.database,
        }
    
    def get_database_url(self) -> str:
        """
        Get the appropriate database URL based on environment
        
        Returns:
            Database URL string
        """
        return self.DATABASE_URL

    def get_masked_url(self) -> str:
        """
        Get the database URL with password masked
        
        Returns:
            Database URL with password replaced by asterisks
        """
        return self.get_database_url().replace(self.credentials.encoded_password, "********")

# Create default config instance
db_config = DatabaseConfig()

if __name__ == "__main__":
    print("\nDatabase Configuration:")
    print(f"Environment: {db_config.env.value}")
    print(f"Host: {db_config.credentials.host}")
    print(f"Port: {db_config.credentials.port}")
    print(f"Database: {db_config.credentials.database}")
    print(f"User: {db_config.credentials.user}")
    print(f"URL: {db_config.get_masked_url()}")