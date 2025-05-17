"""
Main entry point for the Coffee Roaster API application.
"""
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, logger
from app.api.router import api_router
from app.core import hardware, monitor, storage

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="API for controlling and monitoring a coffee roaster",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)

@app.get("/", tags=["status"])
async def root():
    """Root endpoint for checking API status."""
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "mode": "simulation" if settings.SIMULATION_MODE else "hardware"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services when the application starts."""
    logger.info(f"Starting {settings.APP_NAME} in {'simulation' if settings.SIMULATION_MODE else 'hardware'} mode")
    
    # Initialize the logs directory
    storage.ensure_logs_directory()
    
    # Setup hardware if not in simulation mode
    if not settings.SIMULATION_MODE:
        phidget_setup_success = hardware.init_hardware()
        if not phidget_setup_success:
            logger.error("Failed to setup Phidget devices. Forcing simulation mode.")
            settings.SIMULATION_MODE = True
    
    # Start the monitoring service
    monitor.start_monitoring()
    
    logger.info(f"{settings.APP_NAME} started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the application shuts down."""
    logger.info("Shutting down application")
    
    # Stop the monitoring service
    monitor.stop_monitoring()
    
    # Cleanup hardware resources
    hardware.cleanup_hardware()
    
    logger.info("Application shutdown complete")

def start():
    """Run the application using Uvicorn."""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    start()