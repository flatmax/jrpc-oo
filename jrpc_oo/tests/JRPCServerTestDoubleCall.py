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
        print("calling _double_call_Test")
        res = self._double_call_test(first_param, second_param)
        print("_double_call_test returns : ")
        print(res)
        return res
    
    def _double_call_test(self, first_param, second_param):
        print(f"double_call_test called with: {first_param}, {second_param}")
        
        # Generate a unique request ID for this call
        request_id = f"request_{asyncio.get_event_loop().time()}"
        
        # Create initial response with the same structure as _process_callback returns
        response = {
            "request_id": request_id,
            "first_param": first_param,
            "second_param": second_param,
            "callback_status": "pending",
            "callback_result": None  # Will be populated when callback completes
        }
        
        # Store the future in a class attribute so we can track it
        if not hasattr(self, 'callback_results'):
            self.callback_results = {}
        
        # Create a future that will store the final result
        future = asyncio.get_event_loop().create_future()
        self.callback_results[request_id] = future
        
        # Start the async callback task in the background
        asyncio.create_task(
            self._process_callback(request_id, future, first_param, second_param)
        )
        
        return response
    
    async def _process_callback(self, request_id, future, original_first, original_second):
        """Process the callback and store the result in the future."""
        try:
            # Call the client and get the result
            result = await self.call_back_to_client(original_first, original_second)
            
            # Create a complete response with the callback result
            complete_response = {
                "request_id": request_id,
                "first_param": original_first,
                "second_param": original_second,
                "callback_status": "completed",
                "callback_result": result
            }
            
            # Set the future's result
            future.set_result(complete_response)
            
            return complete_response
        except Exception as e:
            # If there's an error, store it in the future
            error_response = {
                "request_id": request_id,
                "callback_status": "error",
                "error": str(e)
            }
            future.set_result(error_response)
            return error_response
        
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
                    return result
                else:
                    print("Client callback method not found")
                    return {"error": "Client callback method not found"}
            else:
                print("No server connection available for callback")
                return {"error": "No server connection available for callback"}
        except Exception as e:
            error_message = f"Error calling back to client: {e}"
            print(error_message)
            return {"error": error_message}
    
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
        
    async def get_callback_result(self, request_id):
        """Get the result of a callback by its request ID.
        
        Args:
            request_id: The ID of the request to get results for
            
        Returns:
            The callback result if available, or a status message
        """
        if not hasattr(self, 'callback_results') or request_id not in self.callback_results:
            return {
                "status": "error",
                "message": f"No callback found for request_id: {request_id}"
            }
            
        future = self.callback_results[request_id]
        
        if future.done():
            # Result is available
            return future.result()
        else:
            # Still pending
            return {
                "request_id": request_id,
                "callback_status": "pending",
                "message": "Callback is still being processed"
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
