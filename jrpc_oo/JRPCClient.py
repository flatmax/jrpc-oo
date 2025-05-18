"""
JRPC client implementation that connects to a WebSocket server.
Equivalent to JavaScript JRPCClient class.
"""

import threading
import time
from websocket import create_connection, WebSocket
from typing import Optional, Dict, Any
from .JRPCCommon import JRPCCommon


class JRPCClient(JRPCCommon):
    """
    JRPC client implementation that connects to a WebSocket server.
    """
    
    def __init__(self, server_uri: str = None, remote_timeout: int = 60):
        """
        Initialize a new JRPC client.
        
        Args:
            server_uri: URI of the WebSocket server (ws://host:port)
            remote_timeout: Timeout for remote calls in seconds
        """
        super().__init__()
        self.server_uri = server_uri
        self.remote_timeout = remote_timeout
        self.ws = None
        self._connected = False
        self._ws_wrapper = None
        
        # Start connection if URI provided
        if server_uri:
            self.server_changed()
    
    def server_changed(self):
        """Handle changes to the server URI."""
        if self.ws:
            self.ws.close()
            self.ws = None
            
        try:
            # Create a WebSocket connection
            self.ws = create_connection(self.server_uri)
            
            # Create a wrapper around the WebSocket
            class WSWrapper:
                def __init__(self, ws):
                    self.ws = ws
                    self.on_message = None
                    self.on_close = None
                
                def send(self, message):
                    self.ws.send(message)
            
            self._ws_wrapper = WSWrapper(self.ws)
            
            # Set up the remote
            self.create_remote(self._ws_wrapper)
            
            # Start receive thread
            self._connected = True
            self._receive_thread = threading.Thread(target=self._receive_loop)
            self._receive_thread.daemon = True
            self._receive_thread.start()
            
        except Exception as e:
            print(f"Connection error: {str(e)}")
            self.ws_error(e)
    
    def _receive_loop(self):
        """Run a loop to receive messages from the WebSocket."""
        try:
            while self._connected and self.ws:
                try:
                    message = self.ws.recv()
                    if message:
                        print(f"Client received raw message: {message[:100]}{'...' if len(message) > 100 else ''}")
                        if self._ws_wrapper and self._ws_wrapper.on_message:
                            self._ws_wrapper.on_message(message)
                except Exception as e:
                    print(f"WebSocket receive error: {str(e)}")
                    self._connected = False
                    if self._ws_wrapper and self._ws_wrapper.on_close:
                        self._ws_wrapper.on_close()
                    break
        except Exception as e:
            print(f"Receive loop error: {str(e)}")
    
    def ws_error(self, event):
        """
        Handle WebSocket connection errors.
        
        Args:
            event: Error event
        """
        self.setup_skip(event)
    
    def setup_skip(self, event=None):
        """
        Called when setup fails.
        
        Args:
            event: Optional error event
        """
        print("is JRPC-OO.node.js running?")
        print("is the ws url cleared with the browser for access?")
    
    def setup_done(self):
        """Called when the remote setup is complete."""
        print("JRPCClient: Remote functions setup complete")
        super().setup_done()
    
    def is_connected(self):
        """
        Check if the client is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected and hasattr(self, 'server') and bool(self.server)
    
    def remote_is_up(self):
        """Called when the remote server is up."""
        print("JRPCClient::remote_is_up")
        super().remote_is_up()
    
    def remote_disconnected(self, uuid):
        """
        Called when the remote disconnects.
        
        Args:
            uuid: UUID of the disconnected remote
        """
        super().remote_disconnected(uuid)
        self._connected = False
    
    def close(self):
        """Close the WebSocket connection."""
        self._connected = False
        if self.ws:
            self.ws.close()
