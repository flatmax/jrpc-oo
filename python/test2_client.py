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
        print(f"\nClient received message: '{text}'")
        return True

def run_notification_test():
    client = JRPCClient(port=8082)
    display = Display()
    
    try:
        # Register display for callbacks
        client.register_instance(display)
        
        if client.connect():
            notifier = client['NotificationServer']
            
            print("\nStarting Notification Test:")
            print("-" * 30)
            
            # Tell server to start sending notifications
            success = notifier.start_notifications()
            
            if success:
                # Wait for all messages
                time.sleep(4)
                
                # Verify we got all messages
                assert len(display.messages) == 3, \
                    f"Expected 3 messages, got {len(display.messages)}"
                print("\nNotification test passed!")
            else:
                print("Server failed to start notifications")
                
    except Exception as e:
        print(f"Test error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    print("Test 2 - Starting Notification Client...")
    run_notification_test()
