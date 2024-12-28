"""
JSON-RPC 2.0 Server implementation with WebSocket and SSL support.

This module provides a WebSocket server that:
- Accepts JSON-RPC 2.0 requests
- Manages client connections
- Exposes Python classes and methods via RPC
- Supports SSL/TLS encryption
- Handles multiple concurrent clients
"""
import ssl
import threading
from websocket_server import WebsocketServer
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python.jrpc_common import JRPCCommon
from python.debug_utils import debug_log

class JRPCServer(JRPCCommon):
    def setup_ssl(self):
        """Setup SSL context for server"""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            './cert/server.crt',
            './cert/server.key'
        )
        return ssl_context

    def handle_client(self, client, server):
        """Handle individual client connections"""
        client_id = str(id(client))
        self.ws = client  # Store client info
        self.server = server  # Store server reference
        debug_log(f"New client connected: {client_id}", self.debug)
        debug_log(f"Server has registered instances: {list(self.instances.keys())}", self.debug)
        
        # Mark connection as ready immediately since we have our components registered
        self.connection_ready()
        debug_log("Server marked connection as ready", self.debug)

    def new_client(self, client, server):
        """Called when a client connects"""
        print(f"Client {client['address']} connected")
        self.handle_client(client, server)

    def client_left(self, client, server):
        """Called when a client disconnects"""
        print(f"Client {client['address']} disconnected")

    def message_received(self, client, server, message):
        """Handle incoming messages"""
        try:
            debug_log(f"Server received message from {client['address']}: {message}", self.debug)
            
            # Parse and validate message
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            debug_log(f"Server decoded message: {message}", self.debug)
            
            # Store client and server references for response handling
            self.ws = client
            self.server = server
            
            # Process the message
            response = self.process_message(message)
            debug_log(f"Server processed message, generated response: {response}", self.debug)
            
            if response:
                debug_log(f"Server preparing to send response: {response}", self.debug)
                # Convert response to JSON string if it's a dict
                if isinstance(response, dict):
                    import json
                    response_str = json.dumps(response)
                else:
                    response_str = str(response)
                debug_log(f"Server sending response string: {response_str}", self.debug)
                server.send_message(client, response_str)
                debug_log("Server completed sending response", self.debug)
        except Exception as e:
            debug_log(f"Error in server message_received: {e}", self.debug)
            debug_log(f"Error type: {type(e)}", self.debug)
            debug_log(f"Error traceback: {sys.exc_info()[2]}", self.debug)

    def send_message(self, message):
        """Override send_message to use websocket server"""
        if hasattr(self, 'server') and hasattr(self, 'ws'):
            self.server.send_message(self.ws, str(message))
        else:
            raise RuntimeError("No websocket connection available")

    def start(self):
        """Start the WebSocket server"""
        protocol = 'wss' if self.use_ssl else 'ws'
        debug_log(f"Starting {protocol}://{self.host}:{self.port}", self.debug)
        
        self.server = WebsocketServer(port=self.port, host=self.host)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)
        
        if self.use_ssl:
            self.server.ssl_context = self.ssl_context
            
        print(f"Server running at {protocol}://{self.host}:{self.port}")
        self.server.run_forever()

    def start_background(self):
        """Start the server in a background thread"""
        server_thread = threading.Thread(target=self.start, daemon=True)
        server_thread.start()
        return self.server
