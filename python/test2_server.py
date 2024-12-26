#!/usr/bin/env python3
"""
Test 2: Server-to-Client RPC test server
"""
from jrpc_server import JRPCServer
from jsonrpclib import Server
import time

class NotificationServer:
    """A server that sends notifications to client"""
    def __init__(self):
        self.client = None
        self.client_ready = False
    
    def register_client(self, client_port):
        """Called by client to indicate it's ready for notifications"""
        try:
            self.client = Server(f'http://localhost:{client_port}')
            self.client_ready = True
            self._send_notifications()
            return True
        except Exception as e:
            print(f"Server: Failed to register - {str(e)}")
            return False
    
    def _send_notifications(self):
        """Send notifications to registered client"""
        if not self.client_ready:
            return False
            
        messages = [
            "Test message #1",
            "Test message #2",
            "Test message #3"
        ]
        
        for msg in messages:
            time.sleep(1)  # Pause between messages
            try:
                success = self.client.Display.show(msg)
            except Exception as e:
                print(f"Server Failed to send '{msg}': {e}")
                
        return True

if __name__ == "__main__":    
    server = JRPCServer(port=8082, debug=True)
    notifier = NotificationServer()
    server.add_class(notifier)
    
    print("Test 2 - Starting Notification Server on port 8082...")
    try:
        print("Starting server...")
        server.start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down notification server...")
