"""
Storage service for the Coffee Roaster API.
Manages saving and retrieving roast logs.
"""
from typing import List, Dict, Any, Optional, Union

from app.core.models.roast_log import SaveRoastRequest
from app.core.storage.base import ensure_logs_directory
from app.core.storage.save import save_roast_data
from app.core.storage.retrieve import get_roast_logs, get_roast_log, format_log_for_api
from app.core.storage.delete import delete_roast_log

# Re-export main functions
__all__ = [
    'ensure_logs_directory',
    'save_roast_data',
    'get_roast_logs',
    'get_roast_log',
    'format_log_for_api',
    'delete_roast_log'
]