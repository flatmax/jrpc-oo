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
        client_id = client['id']
        remote = self.new_remote()
        self.client_remotes[client_id] = remote
        
        # Set up transmitter function
        def transmit(message, next_callback):
            try:
                server.send_message(client, message)
                next_callback(False)
            except Exception as e:
                print(f"Transmission error: {str(e)}")
                next_callback(True)
        
        # Configure remote
        remote.jrpc.set_transmitter(transmit)
        
        # Expose classes
        if self.classes:
            for cls in self.classes:
                remote.jrpc.expose(cls)
        remote.jrpc.upgrade()
        
        # Notify that a new client connected
        self.remote_is_up()
        
        # Get available components
        remote.jrpc.call('system.listComponents', [], lambda err, result: 
                         print(f"Error listing components: {err}") if err else 
                         self._handle_components(remote, result))
    
    def _handle_components(self, remote, result):
        """Process component list result from client."""
        if result:
            method_names = list(result.keys())
            print(f"Remote components available: {method_names}")
            self.setup_fns(method_names, remote)
    
    def _on_message(self, client, server, message):
        """
        Called when a message is received from a client.
        
        Args:
            client: Client information
            server: WebSocket server instance
            message: Received message
        """
        client_id = client['id']
        if client_id in self.client_remotes:
            remote = self.client_remotes[client_id]
            remote.jrpc.receive(message)
    
    def _on_client_left(self, client, server):
        """
        Called when a client disconnects.
        
        Args:
            client: Client information
            server: WebSocket server instance
        """
        client_id = client['id']
        if client_id in self.client_remotes:
            remote = self.client_remotes[client_id]
            
            # Clean up
            self.rm_remote(None, remote.uuid)
            del self.client_remotes[client_id]
    
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
