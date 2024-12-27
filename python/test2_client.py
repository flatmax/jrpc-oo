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
        
    async def show(self, text):
        """Handle incoming server messages"""
        self.messages.append(text)
        print(f"\nClient received message: '{text}'")
        return True

async def run_notification_test():
    client = JRPCClient(port=8082, debug=True)
    display = Display()
    client.add_class(display)
    
    try:
        # Connect to server and register display for callbacks
        if await client.connect():
            notifier = client['NotificationServer']
            
            print("\nStarting Notification Test:")
            print("-" * 30)
            
            print("\nClient: Attempting to register with server...")
            try:
                success = await notifier.register_client(None)
                print(f"Client: Registration call returned: {success}")
                
                if success:
                    print("Client: Successfully registered, waiting for notifications...")
                    # Keep connection alive longer to receive messages
                    try:
                        await asyncio.sleep(5)  # Wait longer for messages
                        # Verify we got all messages
                        if len(display.messages) == 3:
                            print("\nNotification test passed!")
                        else:
                            print(f"\nTest incomplete: Expected 3 messages, got {len(display.messages)}")
                    except asyncio.CancelledError:
                        print("\nTest interrupted")
                else:
                    print("Failed to register with server")
                    
            except Exception as e:
                print(f"Test error: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    print("Test 2 - Starting Notification Client...")
    asyncio.run(run_notification_test())
