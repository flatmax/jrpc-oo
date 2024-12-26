#!/usr/bin/env python3
"""
Test 2: Server-to-Client RPC test client
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
        print(f"\nClient [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}] received message: '{text}'")
        return True

def run_notification_test():
    client = JRPCClient(port=8082, debug=True)
    display = Display()
    
    try:
        # Register display for callbacks and start client server first
        client.register_instance(display)
        if not client.start_server():
            print("Failed to start client server")
            return
            
        # Now connect to main server
        if client.connect_to_server():
            notifier = client['NotificationServer']
            
            print("\nStarting Notification Test:")
            print("-" * 30)
            
            print(f"\nClient [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}]: Attempting to register with server...")
            try:
                success = notifier.register_client(client.client_port)
                print(f"Client [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}]: Registration call returned: {success}")
                
                if success:
                    print(f"Client [{time.strftime('%Y-%m-%d %H:%M:%S')}.{int(time.time() * 1000000) % 1000000:06d}]: Successfully registered, waiting for notifications...")
                    # Wait for all messages
                    time.sleep(4)
                    
                    # Verify we got all messages
                    assert len(display.messages) == 3, \
                        f"Expected 3 messages, got {len(display.messages)}"
                    print("\nNotification test passed!")
                else:
                    print("Failed to register with server")
                    
            except Exception as e:
                print(f"Test error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    print("Test 2 - Starting Notification Client...")
    run_notification_test()
