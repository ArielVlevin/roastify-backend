"""
Base functionality for storage services.
"""
import os
from app.config import settings, logger

def ensure_logs_directory() -> None:
    """Ensure the logs directory exists."""
    os.makedirs(settings.LOGS_DIRECTORY, exist_ok=True)
    logger.debug(f"Ensured logs directory exists: {settings.LOGS_DIRECTORY}")

def get_full_filepath(filename: str) -> str:
    """
    Get the full filepath for a log file.
    
    Args:
        filename: Name of the log file
        
    Returns:
        str: Full path to the file
    """
    if not filename.endswith('.json'):
        filename += '.json'
    
    return os.path.join(settings.LOGS_DIRECTORY, filename)