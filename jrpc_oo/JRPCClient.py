"""
JSON-RPC Client implementation over WebSockets.
"""

import json
import ssl
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
        
        # Start the WebSocket connection in a separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={
            'sslopt': {"cert_reqs": ssl.CERT_NONE}
        })
        ws_thread.daemon = True
        ws_thread.start()
        
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
        remote['client'] = self
        
        # Request the list of available methods
        self.send_request('system.listComponents', [], lambda err, result: 
                         self.setup_fns(list(result.keys()), remote) if not err else None)
    
    def on_message(self, ws, message):
        """
        Handle incoming WebSocket message.
        
        Args:
            ws: WebSocket object
            message: Message received
        """
        try:
            data = json.loads(message)
            
            # Handle requests from the server
            if 'method' in data:
                method_name = data['method']
                params = data.get('params', {})
                request_id = data.get('id')
                
                # Find method in exposed classes
                method_found = False
                result = None
                error = None
                
                for cls in self.classes:
                    if method_name in cls:
                        try:
                            method_found = True
                            result = cls[method_name](params)
                            break
                        except Exception as e:
                            error = str(e)
                            print(f"Error executing {method_name}: {e}")
                
                # Send response if request had an ID
                if request_id is not None:
                    if method_found and error is None:
                        response = {
                            'jsonrpc': '2.0',
                            'result': result,
                            'id': request_id
                        }
                    else:
                        response = {
                            'jsonrpc': '2.0',
                            'error': {
                                'code': -32601 if not method_found else -32000,
                                'message': f'Method not found: {method_name}' if not method_found else error
                            },
                            'id': request_id
                        }
                    ws.send(json.dumps(response))
            
            # Handle responses to our requests
            elif ('result' in data or 'error' in data) and 'id' in data:
                request_id = data['id']
                if request_id in self.pending_requests:
                    callback = self.pending_requests[request_id]['callback']
                    if 'error' in data:
                        callback(data['error'], None)
                    else:
                        callback(None, data['result'])
                    del self.pending_requests[request_id]
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
    
    def on_error(self, ws, error):
        """
        Handle WebSocket error.
        
        Args:
            ws: WebSocket object
            error: Error information
        """
        print(f"WebSocket error: {error}")
        self.setup_skip()
    
    def on_close(self, ws, close_status_code, close_msg):
        """
        Handle WebSocket connection close.
        
        Args:
            ws: WebSocket object
            close_status_code: Status code
            close_msg: Close message
        """
        # Find the remote for this connection
        uuid_to_remove = None
        for uuid, remote in self.remotes.items():
            if remote.get('ws') == ws:
                uuid_to_remove = uuid
                break
        
        if uuid_to_remove:
            self.rm_remote(None, uuid_to_remove)
    
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
