# backend/app/database/config.py
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

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