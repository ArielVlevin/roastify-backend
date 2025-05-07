"""
Functions for deleting saved roast data.
"""
import os
from app.config import logger
from app.core.storage.base import get_full_filepath

def delete_roast_log(log_id: str) -> bool:
    """
    Delete a specific roast log.
    
    Args:
        log_id: Unique identifier for the roast (filename without .json)
        
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        filename = f"{log_id}.json"
        filepath = get_full_filepath(filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Log file not found for deletion: {filename}")
            return False
        
        os.remove(filepath)
        logger.info(f"Deleted log file: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error deleting log file {log_id}: {str(e)}")
        return False