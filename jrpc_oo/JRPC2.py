"""
JSON-RPC 2.0 implementation for WebSockets.
"""
import asyncio
import json
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class JRPC2:
    """JSON-RPC 2.0 implementation for handling RPC calls over WebSockets."""
    
    def __init__(self, remote_timeout: int = 60):
        self.active = True
        self.transmitter = None
        self.remote_timeout = remote_timeout
        self.requests = {}
        self.methods = {}
        self.uuid = str(uuid.uuid4())
    
    def set_transmitter(self, transmitter: Callable):
        """Set the function used to transmit messages.
        
        Args:
            transmitter: A function that takes a message and a callback.
        """
        self.transmitter = transmitter
    
    def expose(self, obj: Dict[str, Callable]):
        """Expose methods for remote calling.
        
        Args:
            obj: A dictionary mapping method names to callable functions.
        """
        self.methods.update(obj)
    
    def upgrade(self):
        """Initialize capabilities after setup."""
        # Add system.listComponents method - expose method names for discovery
        self.methods["system.listComponents"] = lambda params, next_cb: next_cb(None, list(self.methods.keys()))
        
        # Define empty methods dictionary if none exists
        if not hasattr(self, 'rpcs'):
            self.rpcs = {}
    
    def call(self, method: str, params: Any, callback: Callable):
        """Make a remote procedure call.
        
        Args:
            method: The method name to call.
            params: Parameters to pass to the method.
            callback: Function to call with results or error.
        """
        request_id = str(uuid.uuid4())
        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': request_id
        }

        self.requests[request_id] = callback
        
        def next_cb(error):
            if error:
                if request_id in self.requests:
                    del self.requests[request_id]
                callback(Exception(f"Failed to send request: {error}"), None)
        
        asyncio.create_task(self._transmit_message(json.dumps(request), next_cb))
    
    async def _transmit_message(self, message, next_cb):
        """Handle message transmission with proper awaiting for async transmitters.
        
        Args:
            message: The JSON message to send
            next_cb: Callback after transmission
        """
        try:
            if callable(self.transmitter):
                if asyncio.iscoroutinefunction(self.transmitter):
                    await self.transmitter(message, next_cb)
                else:
                    self.transmitter(message, next_cb)
        except Exception as e:
            print(f"Error in _transmit_message: {e}")
            next_cb(True)
    
    def receive(self, message_str: str):
        """Process a received message.
        
        Args:
            message_str: The message string received from remote.
        """
        try:
            message = json.loads(message_str)
            
            # Handle response
            if 'id' in message and 'result' in message or 'error' in message:
                request_id = message.get('id')
                if request_id in self.requests:
                    callback = self.requests[request_id]
                    del self.requests[request_id]
                    
                    if 'error' in message:
                        callback(message['error'], None)
                    else:
                        callback(None, message['result'])
            
            # Handle request
            elif 'method' in message:
                method = message.get('method')
                params = message.get('params', {})
                request_id = message.get('id')
                
                if method in self.methods:
                    try:
                        # Create callback for sending response
                        def response_callback(err, res):
                            self._send_response(request_id, err, res)
                            
                        # Call method with parameters and callback
                        self.methods[method](params, response_callback)
                    except Exception as e:
                        self._send_error(request_id, str(e))
                else:
                    self._send_error(request_id, f"Method not found: {method}")
        
        except json.JSONDecodeError:
            print(f"Error decoding JSON message: {message_str}")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _send_response(self, request_id, error, result):
        """Send a response for a request.
        
        Args:
            request_id: The ID of the original request.
            error: Error information or None.
            result: Result data or None.
        """
        if not request_id:
            return
            
        response = {
            'jsonrpc': '2.0',
            'id': request_id
        }
        
        if error:
            response['error'] = {
                'code': -32000,
                'message': str(error)
            }
        else:
            response['result'] = result
            
        def next_cb(err):
            if err:
                print(f"Failed to send response: {err}")
        
        try:
            json_response = json.dumps(response)
        except TypeError as e:
            # Handle non-serializable objects
            print(f"JSON serialization error: {e}")
            self._send_error(request_id, "Internal error: Result not serializable")
            return
                
        asyncio.create_task(self._transmit_message(json_response, next_cb))
    
    def _send_error(self, request_id, message, code=-32000):
        """Send an error response.
        
        Args:
            request_id: The ID of the original request.
            message: Error message.
            code: Error code.
        """
        response = {
            'jsonrpc': '2.0',
            'error': {
                'code': code,
                'message': message
            },
            'id': request_id
        }
        
        def next_cb(err):
            if err:
                print(f"Failed to send error response: {err}")
                
        asyncio.create_task(self._transmit_message(json.dumps(response), next_cb))
