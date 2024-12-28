#!/usr/bin/env python3
"""
Test 2: Simple client that connects and stays running
"""
from jrpc_client import JRPCClient
import time

class Display:
    """Display class that receives server notifications"""
    def __init__(self):
        self.messages = []
        
    def show(self, text):
        """Handle incoming server messages"""
        self.messages.append(text)
        print(f"\nClient received message: '{text}'")
        return True

def run_client():
    """Run the client"""
    client = JRPCClient(port=8082, debug=True)
    display = Display()
    client.add_class(display)
    
    try:
        print("\nConnecting to server...")
        if not client.connect():
            print("Failed to connect to server")
            return

        print("Connected and running. Press Ctrl+C to exit.")
        
        # Create an event for clean shutdown
        import threading
        shutdown_event = threading.Event()
        
        # First wait for connection
        client.connection_ready_event.wait()
        
        # Then wait for shutdown signal
        while not shutdown_event.is_set():
            try:
                shutdown_event.wait(timeout=0.1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print('test2_client.py starting')
    run_client()
