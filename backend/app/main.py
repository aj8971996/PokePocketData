import sys
from pathlib import Path
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import uvicorn
from typing import Union

# Get the absolute path of the current file's directory
current_dir = Path(__file__).resolve().parent

# Get the project root directory (two levels up from current file)
project_root = current_dir.parent.parent

# Add paths to Python path
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'backend'))

# Import our modules
from app.database.base import init_database, verify_connection, init_tables
from app.routers import ppdd_router, auth
from app.database.db_config import db_config, DatabaseEnvironment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'logs' / 'app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PokéPocketData API",
    description="""
    A comprehensive API for managing Pokémon card game data, including:
    - Card management (Pokémon and Trainer cards)
    - Deck building and management
    - Game record tracking
    - Player statistics
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
origins = [
    "http://localhost:4200",  # Angular default dev server
    "http://localhost:8000",  # FastAPI server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="PokéPocketData API",
        version="1.0.0",
        description="A comprehensive API for managing Pokémon card game data",
        routes=app.routes,
    )

    # Custom documentation settings
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error",
            "status_code": exc.status_code
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "server_error"
        }
    )

# Include routers with versioned prefixes
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["authentication"]
)
app.include_router(
    ppdd_router.router,
    prefix="/api/v1",
    tags=["pokemon-card-game"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and verify connection on startup"""
    try:
        logger.info("Starting application initialization...")
        
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Verify connection
        logger.info("Verifying database connection...")
        if not verify_connection():
            raise Exception("Database connection failed")
        
        # Initialize tables
        logger.info("Initializing database tables...")
        init_tables()
        
        # Log configuration details
        logger.info(f"Environment: {db_config.env}")
        logger.info(f"Database Host: {db_config.credentials.host}")
        logger.info(f"Database Name: {db_config.DATABASE}")
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint for API status check"""
    return {
        "status": "online",
        "app_name": "PokéPocketData API",
        "version": "1.0.0",
        "environment": db_config.env.value
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = verify_connection()
    
    response = {
        "status": "healthy" if db_status else "unhealthy",
        "database": {
            "connected": db_status,
            "environment": db_config.env.value,
            "host": db_config.credentials.host
        },
        "api_version": "1.0.0"
    }
    
    if not db_status:
        return JSONResponse(
            status_code=503,
            content=response
        )
    
    return response

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"]
            }
        }
    )