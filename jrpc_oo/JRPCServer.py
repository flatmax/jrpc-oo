"""
JRPC server implementation that handles WebSocket connections.
Equivalent to JavaScript JRPCServer class.
"""

import threading
import time
from typing import Optional, Dict, Any
from websocket_server import WebsocketServer
from .JRPCCommon import JRPCCommon


class JRPCServer(JRPCCommon):
    """
    JRPC server implementation that handles WebSocket connections.
    """
    
    def __init__(self, port: int = 9000, remote_timeout: int = 60):
        """
        Initialize a new JRPC server.
        
        Args:
            port: Port number for the WebSocket server
            remote_timeout: Timeout for remote calls in seconds
        """
        super().__init__()
        self.remote_timeout = remote_timeout
        self.port = port
        
        # Create WebSocket server
        self.wss = WebsocketServer(host='0.0.0.0', port=port)
        
        # Set up event handlers
        self.wss.set_fn_new_client(self._on_new_client)
        self.wss.set_fn_message_received(self._on_message)
        self.wss.set_fn_client_left(self._on_client_left)
        
        # Client -> Remote mapping
        self.client_remotes = {}
        
        # Server thread
        self._server_thread = None
    
    
    
    
    def _on_new_client(self, client, server):
        """
        Called when a new client connects.
        
        Args:
            client: Client information
            server: WebSocket server instance
        """
        # Create a wrapper for the client that provides WebSocket-like interface
        class WSWrapper:
            def __init__(self, client_id, server):
                self.client_id = client_id
                self.server = server
                self.on_message = None
                self.on_close = None
                
            def send(self, message):
                for client in self.server.clients:
                    if client['id'] == self.client_id:
                        self.server.send_message(client, message)
                        break
        
        ws_wrapper = WSWrapper(client['id'], server)
        remote = self.create_remote(ws_wrapper)
        self.client_remotes[client['id']] = (remote, ws_wrapper)
    
    def _on_message(self, client, server, message):
        """
        Called when a message is received from a client.
        
        Args:
            client: Client information
            server: WebSocket server instance
            message: Received message
        """
        print(f"Server received message from client {client['id']}: {message[:100]}{'...' if len(message) > 100 else ''}")
        if client['id'] in self.client_remotes:
            remote, ws_wrapper = self.client_remotes[client['id']]
            if hasattr(remote, "receive"):
                remote.receive(message)  # Pass directly to remote for processing
    
    def _on_client_left(self, client, server):
        """
        Called when a client disconnects.
        
        Args:
            client: Client information
            server: WebSocket server instance
        """
        if client['id'] in self.client_remotes:
            remote, ws_wrapper = self.client_remotes[client['id']]
            if ws_wrapper.on_close:
                ws_wrapper.on_close()
            
            # Clean up the connection
            self.rm_remote(None, remote.uuid)
            del self.client_remotes[client['id']]
    
    def start(self, blocking=True):
        """
        Start the WebSocket server.
        
        Args:
            blocking: If True, run in current thread; if False, run in a separate thread
        """
        if blocking:
            self.wss.run_forever()
        else:
            self._server_thread = threading.Thread(target=self.wss.run_forever)
            self._server_thread.daemon = True
            self._server_thread.start()
    
    def stop(self):
        """Stop the WebSocket server."""
        if self.wss:
            self.wss.shutdown_gracefully()
