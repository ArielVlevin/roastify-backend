"""
Configuration settings for the Coffee Roaster API.
"""
import os
import logging
# Import from pydantic-settings instead of pydantic for Pydantic 2.x
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Extra

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("coffee_roaster.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings."""
    
    # API configuration
    APP_NAME: str = "Coffee Roaster API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Roast configuration
    DEFAULT_TEMPERATURE: float = 24.0  # Starting room temperature in C
    
    # Phidget configuration
    SIMULATION_MODE: bool = True
    PHIDGET_SERIAL_NUMBER: int = 0  # Set to your device serial number
    HUB_PORT: int = 0  # hub0000_0
    TEMP_CHANNEL: int = 0  # tmp1101_0
    HEATER_PORT: int = 1
    HEATER_CHANNEL: int = 0
    
    # Storage configuration
    LOGS_DIRECTORY: str = "roast_logs"
    
    # Advanced settings
    TEMPERATURE_UPDATE_INTERVAL: float = 0.2  # Seconds between temperature updates
    
    # Pydantic 2.x uses model_config instead of Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields to avoid issues with environment variables
    )

# Create instance of settings
settings = Settings()

# Ensure logs directory exists
os.makedirs(settings.LOGS_DIRECTORY, exist_ok=True)