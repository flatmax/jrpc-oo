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
        print(f"\nServer: [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}] register_client called with port {client_port}")
        try:
            self.client = Server(f'http://localhost:{client_port}')
            self.client_ready = True
            print("Server: Client registered successfully")
            print("Server: Starting notifications...")
            self._send_notifications()
            return True
        except Exception as e:
            print(f"Server: [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}] Failed to register - {str(e)}")
            return False
    
    def _send_notifications(self):
        """Send notifications to registered client"""
        print(f"\nServer: [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}] Checking if ready to send notifications")
        print(f"Server: [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}] client_ready = {self.client_ready}")
        print(f"Server: [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}] client object = {self.client}")
        
        if not self.client_ready:
            print(f"Server: [{time.strftime('%Y-%m-%d %H:%M:%S.%f')}] Not ready to send notifications")
            return False
            
        print(f"\nServer: [{time.strftime('%Y-%m-%d %H:%M:%S.%f')}] Starting notification sequence...")
        messages = [
            "Test message #1",
            "Test message #2",
            "Test message #3"
        ]
        
        for msg in messages:
            time.sleep(1)  # Pause between messages
            try:
                success = self.client.Display.show(msg)
                print(f"Server [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}] sent: '{msg}', Client responded: {success}")
            except Exception as e:
                print(f"Server [{time.strftime('%Y-%m-%d %H:%M:%S.%f')}] Failed to send '{msg}': {e}")
                
        return True

if __name__ == "__main__":    
    server = JRPCServer(port=8082, debug=True)
    notifier = NotificationServer()
    server.register_instance(notifier)
    
    print("Test 2 - Starting Notification Server on port 8082...")
    try:
        print("Starting server...")
        server.start()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down notification server...")
