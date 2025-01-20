# backend/app/database/config.py
import os
import sys
from pathlib import Path
from typing import Optional

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path(root_dir) / '.env'
    if not env_path.exists():
        raise FileNotFoundError(f"'.env' file not found at {env_path}")
    load_dotenv(env_path)
except ImportError:
    raise ImportError(
        "python-dotenv is not installed. Please install it using: pip install python-dotenv"
    )

class DatabaseConfig:
    def __get_env(self, key: str, default: Optional[str] = None) -> str:
        value = os.getenv(key, default)
        if value is None or value == "":
            raise ValueError(f"Environment variable {key} is not set or is empty")
        return value

    def __init__(self):
        self.USER: str = self.__get_env("DB_USER", "ppdd_api_user")
        self.PASSWORD: str = self.__get_env("DB_PASSWORD")
        self.HOST: str = self.__get_env("DB_HOST", "localhost")
        self.PORT: str = self.__get_env("DB_PORT", "3306")
        self.DATABASE: str = self.__get_env("DB_NAME", "pokepocketdata")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+mysqlconnector://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"
    
    @property
    def DATABASE_URL_NO_DB(self) -> str:
        return f"mysql+mysqlconnector://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}"

db_config = DatabaseConfig()