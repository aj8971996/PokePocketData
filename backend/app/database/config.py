# backend/app/database/config.py
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv(Path(root_dir) / '.env')
except ImportError:
    raise ImportError(
        "python-dotenv is not installed. Please install it using: pip install python-dotenv"
    )

class DatabaseConfig:
    USER: str = os.getenv("DB_USER", "root")
    PASSWORD: str = os.getenv("DB_PASSWORD", "")
    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: str = os.getenv("DB_PORT", "3306")
    DATABASE: str = os.getenv("DB_NAME", "pokepocketdata")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+mysqlconnector://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"
    
    @property
    def DATABASE_URL_NO_DB(self) -> str:
        return f"mysql+mysqlconnector://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}"

db_config = DatabaseConfig()