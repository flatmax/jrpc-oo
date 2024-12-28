import time
from datetime import datetime
import inspect
import os

def debug_log(message, debug=True):
    """Print debug message with timestamp if debug is enabled"""
    if debug:
        # Determine if we're running in server or client code
        stack = inspect.stack()
        for frame in stack:
            if "server.py" in frame.filename.lower():
                source = "SERVER"
                break
            elif "client.py" in frame.filename.lower():
                source = "CLIENT" 
                break
        else:
            # Default to CLIENT if we can't determine
            source = "CLIENT"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] {source} DEBUG: {message}")
