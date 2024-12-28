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
            filename = frame.filename.lower()
            if any(server_file in filename for server_file in ["server.py", "jrpcserver.py", "test_server.py"]):
                source = "SERVER"
                break
            elif any(client_file in filename for client_file in ["client.py", "jrpcclient.py", "test_client.py"]):
                source = "CLIENT"
                break
        else:
            # If we can't determine, use the class name
            calling_class = None
            for frame in stack:
                if 'self' in frame.frame.f_locals:
                    instance = frame.frame.f_locals['self']
                    class_name = instance.__class__.__name__
                    if 'Server' in class_name:
                        source = "SERVER"
                        break
                    elif 'Client' in class_name:
                        source = "CLIENT"
                        break
            else:
                # Default to UNKNOWN if we still can't determine
                source = "UNKNOWN"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] {source} DEBUG: {message}")
