"""
JSON-RPC Server implementation over WebSockets.
"""

import json
import threading
from websocket_server import WebsocketServer
from .JRPCCommon import JRPCCommon

class JRPCServer(JRPCCommon):
    """
    Server class for JSON-RPC over WebSockets.
    Similar to the JavaScript JRPCServer.
    """
    
    def __init__(self, port=9000, remote_timeout=60):
        """
        Initialize the server.
        
        Args:
            port: The port number to use for socket binding
            remote_timeout: The maximum timeout of connection
        """
        super().__init__()
        self.remote_timeout = remote_timeout
        
        # Simple WebSocket server initialization
        try:
            # Initialize without SSL
            self.wss = WebsocketServer(host='0.0.0.0', port=port)
        except Exception as e:
            print(f"Error initializing WebSocket server: {e}")
            raise
        
        # Set up event handlers
        self.wss.set_fn_new_client(self.on_new_client)
        self.wss.set_fn_client_left(self.on_client_left)
        self.wss.set_fn_message_received(self.on_message_received)
    
    def start(self):
        """Start the server."""
        # Run the server in a background thread using the common method
        self.ws_thread = self.start_background_thread(self.wss)
        return self.ws_thread
    
    def on_new_client(self, client, server):
        """
        Handle new client connection.
        
        Args:
            client: Client information
            server: Server object
        """
        remote = self.new_remote()
        remote['client'] = client
        remote['connection'] = client  # Use consistent key for connection
        
        # Setup the WebSocket for this remote
        self.setup_remote(remote, client)
        
        self.remote_is_up()
    
    def on_client_left(self, client, server):
        """
        Handle client disconnection.
        
        Args:
            client: Client information
            server: Server object
        """
        self.handle_connection_closed(client)
    
    def on_message_received(self, client, server, message):
        """
        Handle message from client.
        
        Args:
            client: Client information
            server: Server object
            message: The message received
        """
        self.process_message(client, message)
    
    def send_response(self, connection, message):
        """
        Send a response to a client connection.
        
        Args:
            connection: Client connection
            message: The message to send
        """
        self.wss.send_message(connection, message)
    
    def setup_remote(self, remote, ws):
        """
        Setup a remote connection.
        
        Args:
            remote: The remote to setup
            ws: WebSocket connection
        """
        # Expose our classes to the remote
        if self.classes:
            for cls_obj in self.classes:
                for method_name, method in cls_obj.items():
                    if 'methods' not in remote:
                        remote['methods'] = {}
                    remote['methods'][method_name] = method
        
        # Request the remote's exposed methods
        request = {
            'jsonrpc': '2.0',
            'method': 'system.listComponents',
            'params': [],
            'id': 1
        }
        self.wss.send_message(ws, json.dumps(request))
