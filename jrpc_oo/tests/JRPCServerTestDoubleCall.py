#!/usr/bin/env python3
"""
Python JRPC server test for double call functionality.
This server exposes methods that can be called from a web client button press.
"""
import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from jrpc_oo.JRPCServer import JRPCServer


class DoubleCallTestClass:
    """Test class with methods for double call testing."""
    
    def __init__(self):
        self.call_count = 0
        self.last_message = ""
    
    def button_press_handler(self, message="Button pressed!"):
        """Handle button press from web client."""
        self.call_count += 1
        self.last_message = message
        
        print(f"Button press received! Count: {self.call_count}")
        print(f"Message: {message}")
        
        # Return response data
        response = {
            "status": "success",
            "call_count": self.call_count,
            "message": f"Server processed: {message}",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return response
    
    def double_call_test(self, first_param, second_param):
        """Method that demonstrates calling back to the client."""
        print(f"double_call_test called with: {first_param}, {second_param}")
        
        # Schedule a callback to the client
        asyncio.create_task(self.call_back_to_client(first_param, second_param))
        
        return {
            "immediate_response": "Server received your call",
            "first_param": first_param,
            "second_param": second_param
        }
    
    async def call_back_to_client(self, original_first, original_second):
        """Call back to the client after a delay."""
        await asyncio.sleep(2)  # Wait 2 seconds
        
        try:
            # Call the client's callback method
            if hasattr(self, 'get_server') and self.get_server():
                server_methods = self.get_server()
                if 'DoubleCallClient.client_callback' in server_methods:
                    result = await server_methods['DoubleCallClient.client_callback'](
                        f"Server calling back with: {original_first}",
                        f"And also: {original_second}",
                        "This is the delayed callback!"
                    )
                    print("Client callback returned:")
                    print(json.dumps(result, indent=2))
                else:
                    print("Client callback method not found")
            else:
                print("No server connection available for callback")
        except Exception as e:
            print(f"Error calling back to client: {e}")
    
    def get_status(self):
        """Get current server status."""
        return {
            "call_count": self.call_count,
            "last_message": self.last_message,
            "server_status": "running"
        }
    
    def reset_counter(self):
        """Reset the call counter."""
        old_count = self.call_count
        self.call_count = 0
        self.last_message = ""
        
        return {
            "status": "reset",
            "previous_count": old_count,
            "new_count": self.call_count
        }


async def main():
    """Main function to set up the server."""
    # Parse command-line arguments
    use_ssl = not ('--no_wss' in sys.argv or 'no_wss' in sys.argv)
    
    # Create server
    jrpc_server = JRPCServer(port=9001, remote_timeout=60)
    
    # Create test class instance
    test_class = DoubleCallTestClass()
    
    # Add class to server
    jrpc_server.add_class(test_class, "DoubleCallTestClass")
    
    # Debug what methods are exposed
    if hasattr(jrpc_server, 'methods'):
        print("Exposed methods:")
        for method_name in jrpc_server.methods:
            print(f"  - {method_name}")
    
    # Start server
    await jrpc_server.start()
    
    print(f"DoubleCall Test Server started on port 9001 with {'WSS' if use_ssl else 'WS'} protocol")
    print("Available methods:")
    print("  - DoubleCallTestClass.button_press_handler(message)")
    print("  - DoubleCallTestClass.double_call_test(first_param, second_param)")
    print("  - DoubleCallTestClass.get_status()")
    print("  - DoubleCallTestClass.reset_counter()")
    
    try:
        # Keep server running indefinitely
        await asyncio.Future()
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        await jrpc_server.stop()


if __name__ == "__main__":
    asyncio.run(main())
