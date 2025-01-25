import logging
import pytest

@pytest.fixture(autouse=True)
def suppress_logger():
    # Get root logger
    root_logger = logging.getLogger()
    # Store original level
    original_level = root_logger.level
    # Set level to suppress info messages
    root_logger.setLevel(logging.WARNING)
    
    yield
    # Restore original logging level after test
    root_logger.setLevel(original_level)

# Optional: Configure specific loggers
@pytest.fixture(autouse=True)
def configure_specific_loggers():
    # Example: Suppress specific logger
    specific_logger = logging.getLogger('module_name')
    original_level = specific_logger.level
    specific_logger.setLevel(logging.ERROR)
    
    yield
    
    specific_logger.setLevel(original_level)