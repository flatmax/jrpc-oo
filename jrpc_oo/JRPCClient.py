"""
JSON-RPC Client implementation over WebSockets.
"""

import json
import threading
import time
from websocket import WebSocketApp
from .JRPCCommon import JRPCCommon

class JRPCClient(JRPCCommon):
    """
    Client class for JSON-RPC over WebSockets.
    Similar to the JavaScript JRPCNodeClient.
    """
    
    def __init__(self, server_uri):
        """
        Initialize the client.
        
        Args:
            server_uri: The WebSocket URI of the server
        """
        super().__init__()
        self.server_uri = server_uri
        self.remote_timeout = 60  # Default timeout in seconds
        self.ws = None
        self.pending_requests = {}  # Track outgoing requests
        self.next_request_id = 1
    
    def connect(self):
        """Connect to the server."""
        # Create WebSocket connection
        self.ws = WebSocketApp(
            self.server_uri,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Start the WebSocket connection using the common method
        self.ws_thread = self.start_background_thread(self.ws)
        
        # Wait for connection to be established
        start_time = time.time()
        while not hasattr(self.ws, '_app') or not self.ws._app:
            if time.time() - start_time > self.remote_timeout:
                raise TimeoutError(f"Failed to connect within {self.remote_timeout} seconds")
            time.sleep(0.1)
    
    def on_open(self, ws):
        """
        Handle WebSocket connection open.
        
        Args:
            ws: WebSocket object
        """
        # Create a new remote for this connection
        remote = self.new_remote()
        remote['ws'] = ws
        remote['connection'] = ws  # Use consistent key for connection
        remote['client'] = self
        
        # Setup the remote and request components
        self.setup_remote(remote, ws)
    
    def on_message(self, ws, message):
        """
        Handle incoming WebSocket message.
        
        Args:
            ws: WebSocket object
            message: Message received
        """
        self.process_message(ws, message)
    
    def send_response(self, connection, message):
        """
        Send a response to a WebSocket connection.
        
        Args:
            connection: WebSocket connection
            message: The message to send
        """
        connection.send(message)
        
    def send_request_to_connection(self, connection, message):
        """
        Send a request to a WebSocket connection.
        
        Args:
            connection: The connection to send to
            message: The message to send
        """
        connection.send(message)
    
    def on_error(self, ws, error):
        """
        Handle WebSocket error.
        
        Args:
            ws: WebSocket object
            error: Error information
        """
        print(f"WebSocket error: {error}")
        self.setup_skip()
    
    def handle_response(self, remote, data):
        """
        Handle responses to requests we've sent.
        
        Args:
            remote: The remote connection
            data: The parsed JSON-RPC response
        """
        request_id = data.get('id')
        if request_id == 1 and 'result' in data:
            # Handle system.listComponents response
            result = data['result']
            self.setup_fns(list(result.keys()), remote)
        elif request_id in self.pending_requests:
            callback = self.pending_requests[request_id]['callback']
            if 'error' in data:
                callback(data['error'], None)
            else:
                callback(None, data['result'])
            del self.pending_requests[request_id]
    
    def on_close(self, ws, close_status_code, close_msg):
        """
        Handle WebSocket connection close.
        
        Args:
            ws: WebSocket object
            close_status_code: Status code
            close_msg: Close message
        """
        self.handle_connection_closed(ws)
    
    def setup_skip(self):
        """Handle setup failure."""
        print("is JRPC-OO.python running?")
        print("is the ws url cleared with the browser for access?")
    
    def send_request(self, method, params, callback):
        """
        Send a JSON-RPC request.
        
        Args:
            method: Method name to call
            params: Parameters for the method
            callback: Function to call with the result
        """
        request_id = self.next_request_id
        self.next_request_id += 1
        
        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': {'args': params} if isinstance(params, list) else params,
            'id': request_id
        }
        
        self.pending_requests[request_id] = {
            'method': method,
            'params': params,
            'callback': callback,
            'time': time.time()
        }
        
        self.ws.send(json.dumps(request))
        
        # Set timeout to clean up the request if no response is received
        def timeout_handler():
            if request_id in self.pending_requests:
                callback({'code': -32603, 'message': 'Request timed out'}, None)
                del self.pending_requests[request_id]
        
        timer = threading.Timer(self.remote_timeout, timeout_handler)
        timer.daemon = True
        timer.start()
