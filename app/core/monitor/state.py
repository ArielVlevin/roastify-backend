"""
Global state for the temperature monitoring service.
"""
import time
import threading
from typing import List, Dict, Optional, Callable, Any, Union

# Global state
is_roasting = False
roast_start_time = 0
roast_data: List[Dict[str, float]] = []
markers: List[Dict[str, Any]] = []

# Thread for continuous monitoring
monitor_thread = None
stop_monitor = False

# Callbacks
on_temperature_change: Optional[Callable[[float], None]] = None
on_first_crack: Optional[Callable[[], None]] = None
on_second_crack: Optional[Callable[[], None]] = None

# State for crack detection
first_crack_detected = False
second_crack_detected = False
first_crack_time = None
second_crack_time = None

# Current roast ID for logging
current_roast_id = None