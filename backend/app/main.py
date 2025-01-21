# app/main.py
import sys
from pathlib import Path
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Get the absolute path of the current file's directory
current_dir = Path(__file__).resolve().parent

# Get the project root directory (one level up from current file)
project_root = current_dir.parent

# Add paths to Python path
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'backend'))

# Import our modules
from app.database.base import init_database, verify_connection
from app.routers import ppdd_router, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PokePocketData API",
    description="API for managing Pokemon card game data",
    version="1.0.0"
)

# Configure CORS
origins = [
    # Dev domains
    "http://localhost:4200",  # Angular default dev server
    "http://localhost:8000",  # FastAPI server
    # Prod domains would go below
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(ppdd_router.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database and verify connection on startup"""
    try:
        logger.info("Initializing database...")
        init_database()
        
        logger.info("Verifying database connection...")
        if not verify_connection():
            raise Exception("Database connection failed")
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint for API status check"""
    return {
        "status": "online",
        "app_name": "PokePocketData API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if verify_connection():
        return {"status": "healthy", "database": "connected"}
    return JSONResponse(
        status_code=503,
        content={"status": "unhealthy", "database": "disconnected"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )