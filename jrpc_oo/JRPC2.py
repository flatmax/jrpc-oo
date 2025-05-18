"""
Custom JSON-RPC 2.0 implementation for WebSockets.
Provides functionality similar to js-jrpc.
"""

import json
import uuid
import time
from typing import Dict, Any, Callable, List, Optional, Union


class JRPC2:
    """JSON-RPC 2.0 implementation for WebSockets."""
    
    def __init__(self, remote_timeout: int = 60):
        """Initialize a new JRPC2 instance.
        
        Args:
            remote_timeout: Timeout for remote calls in seconds
        """
        self.active = True
        self.transmitter = None
        self.remote_timeout = remote_timeout
        self.local_timeout = 0
        self.next_id = 1
        self.requests = {}
        self.notifications = {}
        self.methods = {}
        self.uuid = str(uuid.uuid4())
        self.rpcs = None  # Will hold remote procedures
    
    def set_transmitter(self, transmitter: Callable):
        """Set the function that transmits messages.
        
        Args:
            transmitter: Function to transmit messages
        """
        self.transmitter = transmitter
    
    def receive(self, message: str):
        """Process a received message.
        
        Args:
            message: JSON-RPC 2.0 message string
        """
        try:
            data = json.loads(message)
            if isinstance(data, list):
                # Batch request
                for item in data:
                    self._handle_message(item)
            else:
                self._handle_message(data)
        except json.JSONDecodeError:
            self._send_error(None, -32700, "Parse error")
        except Exception as e:
            self._send_error(None, -32603, f"Internal error: {str(e)}")
    
    def _handle_message(self, data: Dict[str, Any]):
        """Handle a single JSON-RPC 2.0 message.
        
        Args:
            data: JSON-RPC 2.0 message data
        """
        if 'jsonrpc' not in data or data['jsonrpc'] != '2.0':
            self._send_error(data.get('id'), -32600, "Invalid Request")
            return
            
        if 'method' in data:
            # Request or notification
            if 'id' in data:
                # Request
                self._handle_request(data)
            else:
                # Notification
                self._handle_notification(data)
        elif 'result' in data or 'error' in data:
            # Response
            self._handle_response(data)
        else:
            self._send_error(data.get('id'), -32600, "Invalid Request")
    
    def _handle_request(self, data: Dict[str, Any]):
        """Handle a JSON-RPC 2.0 request.
        
        Args:
            data: Request data
        """
        method = data['method']
        params = data.get('params', {})
        request_id = data['id']
        
        if method not in self.methods:
            self._send_error(request_id, -32601, f"Method not found: {method}")
            return
            
        try:
            self.methods[method](params, lambda err, result: 
                self._send_error(request_id, -32603, str(err)) if err else 
                self._send_result(request_id, result)
            )
        except Exception as e:
            self._send_error(request_id, -32603, f"Internal error: {str(e)}")
    
    def _handle_notification(self, data: Dict[str, Any]):
        """Handle a JSON-RPC 2.0 notification.
        
        Args:
            data: Notification data
        """
        method = data['method']
        params = data.get('params', {})
        
        if method in self.methods:
            try:
                self.methods[method](params, lambda *args: None)
            except Exception as e:
                # Notifications don't send errors back
                print(f"Error in notification handler: {str(e)}")
    
    def _handle_response(self, data: Dict[str, Any]):
        """Handle a JSON-RPC 2.0 response.
        
        Args:
            data: Response data
        """
        response_id = data.get('id')
        if response_id in self.requests:
            callback = self.requests.pop(response_id)
            if 'result' in data:
                callback(None, data['result'])
            elif 'error' in data:
                callback(data['error'], None)
    
    def _send_result(self, request_id: Union[str, int], result: Any):
        """Send a successful response.
        
        Args:
            request_id: Request ID
            result: Result data
        """
        response = {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': result
        }
        self._transmit(json.dumps(response))
    
    def _send_error(self, request_id: Optional[Union[str, int]], code: int, message: str):
        """Send an error response.
        
        Args:
            request_id: Request ID or None
            code: Error code
            message: Error message
        """
        response = {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': code,
                'message': message
            }
        }
        self._transmit(json.dumps(response))
    
    def _transmit(self, message: str):
        """Transmit a message using the configured transmitter.
        
        Args:
            message: Message to transmit
        """
        if self.transmitter:
            self.transmitter(message, lambda err: print(f"Transmission error: {err}") if err else None)
    
    def call(self, method: str, params: Any, callback: Callable):
        """Call a remote method.
        
        Args:
            method: Method name
            params: Parameters
            callback: Callback function for the response
        """
        request_id = self.next_id
        self.next_id += 1
        self.requests[request_id] = callback
        
        request = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method,
            'params': params
        }
        
        self._transmit(json.dumps(request))
    
    def expose(self, methods: Dict[str, Callable]):
        """Expose methods for remote calling.
        
        Args:
            methods: Dictionary of method names and implementations
        """
        self.methods.update(methods)
    
    def upgrade(self):
        """Perform any necessary upgrade steps after connection."""
        pass
