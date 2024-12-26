#!/usr/bin/env python3
"""
Test 2: Server-to-Client RPC test client
"""
from jrpc_client import JRPCClient
import asyncio

class Display:
    """Display class that receives server notifications"""
    def __init__(self):
        self.messages = []
        
    def show(self, text):
        """Handle incoming server messages"""
        self.messages.append(text)
        print(f"\nClient received message: '{text}'")
        return True

async def run_notification_test():
    client = JRPCClient(port=8082, debug=False)
    display = Display()
    
    try:
        # Connect to server and register display for callbacks
        if await client.connect():
            client.add_class(display)
            notifier = client['NotificationServer']
            
            print("\nStarting Notification Test:")
            print("-" * 30)
            
            print("\nClient: Attempting to register with server...")
            try:
                success = await notifier.register_client(None)
                print(f"Client: Registration call returned: {success}")
                
                if success:
                    print("Client: Successfully registered, waiting for notifications...")
                    # Wait for all messages
                    await asyncio.sleep(4)
                    
                    # Verify we got all messages
                    assert len(display.messages) == 3, \
                        f"Expected 3 messages, got {len(display.messages)}"
                    print("\nNotification test passed!")
                else:
                    print("Failed to register with server")
                    
            except Exception as e:
                print(f"Test error: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    print("Test 2 - Starting Notification Client...")
    asyncio.run(run_notification_test())
