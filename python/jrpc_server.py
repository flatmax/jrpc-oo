"""
JSON-RPC 2.0 Server implementation with WebSocket and SSL support.

This module provides a WebSocket server that:
- Accepts JSON-RPC 2.0 requests
- Manages client connections
- Exposes Python classes and methods via RPC
- Supports SSL/TLS encryption
- Handles multiple concurrent clients
"""
import json
import ssl
import time
from websocket_server import WebsocketServer
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python.jrpc_common import JRPCCommon
from python.debug_utils import debug_log

class JRPCServer(JRPCCommon):
    # Override parent class variables
    is_server = True

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
            # Start message processing in a thread
            import threading
            thread = threading.Thread(
                target=self.process_incoming_message,
                args=(message, client, server),
                daemon=True
            )
            thread.start()
        except Exception as e:
            debug_log(f"Error in server message_received: {e}", self.debug)

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

