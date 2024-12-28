#!/usr/bin/env python3
"""
Test 2: Server-to-Client RPC test server
"""
import time
import threading
from jrpc_server import JRPCServer

def send_test_messages(server):
    """Send test messages to client"""
    try:
        # Wait for connection to be fully ready
        server.connection_ready_event.wait()
        print("\nConnection fully established!")

        if "Display.show" not in server.remotes:
            print("Error: Display.show not found in client components")
            return

        messages = [
            "Test message #1",
            "Test message #2", 
            "Test message #3"
        ]
        
        for msg in messages:
            time.sleep(1)  # Pause between messages
            try:
                server.call_method("Display.show", {"args": [msg]})
                print(f"Server sent '{msg}'")
            except Exception as e:
                print(f"Server Failed to send '{msg}': {e}")

    except Exception as e:
        print(f"Error sending messages: {e}")

if __name__ == "__main__":    
    print('test2_server.py starting')
    server = JRPCServer(port=8082, debug=True)
    
    print("Test 2 - Starting Notification Server on port 8082...")
    
    # Start message sending in a separate thread
    import threading
    message_thread = threading.Thread(target=send_test_messages, args=(server,), daemon=True)
    message_thread.start()
    
    try:
        print("Starting server...")
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down notification server...")
