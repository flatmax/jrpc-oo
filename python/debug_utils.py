import time
from datetime import datetime

def debug_log(message, debug=True):
    """Print debug message with timestamp if debug is enabled"""
    if debug:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] DEBUG: {message}")
