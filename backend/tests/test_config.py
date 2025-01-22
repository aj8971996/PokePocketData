import sys
from pathlib import Path
import pytest
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.database.db_config import DatabaseConfig, DatabaseEnvironment

def test_env_file_loading():
    """Test that the .env file can be loaded"""
    # Create config instance which should load .env
    db_config = DatabaseConfig()
    
    # Check that essential environment variables are loaded
    assert db_config.credentials.user is not None, "Database user not loaded from .env"
    assert db_config.credentials.password is not None, "Database password not loaded from .env"
    assert db_config.credentials.host is not None, "Database host not loaded from .env"
    assert db_config.credentials.port is not None, "Database port not loaded from .env"
    assert db_config.credentials.database is not None, "Database name not loaded from .env"

def test_database_url_construction():
    """Test that database URLs are constructed correctly"""
    db_config = DatabaseConfig()
    
    # Test base URL format
    assert db_config.BASE_URL.startswith("mysql+mysqlconnector://"), "Invalid base URL format"
    
    # Test that URLs contain necessary components
    assert db_config.credentials.user in db_config.DATABASE_URL, "User not in database URL"
    assert db_config.credentials.host in db_config.DATABASE_URL, "Host not in database URL"
    assert db_config.credentials.port in db_config.DATABASE_URL, "Port not in database URL"
    assert db_config.credentials.database in db_config.DATABASE_URL, "Database name not in database URL"

def test_database_connection():
    """Test that we can establish a database connection"""
    db_config = DatabaseConfig()
    
    try:
        # Use verify_connection method from DatabaseConfig
        assert db_config.verify_connection() == True, "Database connection failed"
    except SQLAlchemyError as e:
        pytest.fail(f"Database connection failed: {str(e)}")

def test_database_initialization():
    """Test database initialization process"""
    try:
        db_config = DatabaseConfig()
        
        # Test database creation
        assert db_config.create_database() == True, "Database creation failed"
        
        # Verify connection
        assert db_config.verify_connection() == True, "Database verification failed"
        
    except Exception as e:
        pytest.fail(f"Database initialization failed: {str(e)}")

def test_test_database_config():
    """Test that test database configuration works correctly"""
    test_config = DatabaseConfig(env=DatabaseEnvironment.TESTING)
    
    # Verify test database name
    assert test_config.credentials.database.endswith('_test'), \
        "Test database name should end with '_test'"
    
    # Verify test database URL
    assert test_config.get_database_url() is not None, "Test database URL not configured"
    assert '_test' in test_config.get_database_url(), "Test database URL should contain '_test'"

def test_connection_pool_settings():
    """Test that connection pool settings are applied"""
    db_config = DatabaseConfig()
    engine = db_config._get_engine()
    
    # Check pool settings
    assert engine.pool.size() == 5, "Pool size should be 5"
    assert engine.pool._max_overflow == 10, "Max overflow should be 10"
    assert engine.pool._recycle == 3600, "Pool recycle should be 3600 seconds"

def test_masked_url():
    """Test that sensitive information is masked in URLs"""
    db_config = DatabaseConfig()
    masked_url = db_config.get_masked_url()
    
    # Check that password is masked
    assert "********" in masked_url, "Password should be masked"
    assert db_config.credentials.password not in masked_url, "Original password should not be in masked URL"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])