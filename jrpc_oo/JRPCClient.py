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
        self.remote = None  # Single remote instead of remotes dictionary
        
        # Start connection if URI provided
        if server_uri:
            self.server_changed()
    
    def server_changed(self):
        """Handle changes to the server URI."""
        if self.ws:
            self.close()
            
        try:
            # Create WebSocket connection
            self.ws = create_connection(self.server_uri)
            
            # Create a remote instance
            self.remote = self.new_remote()
            
            # Set up direct transmitter
            def transmit(message, next_callback):
                try:
                    self.ws.send(message)
                    next_callback(False)
                except Exception as e:
                    print(f"Transmission error: {str(e)}")
                    next_callback(True)
            
            self.remote.jrpc.set_transmitter(transmit)
            
            # Expose classes to remote
            if self.classes:
                for cls in self.classes:
                    self.remote.jrpc.expose(cls)
                self.remote.jrpc.upgrade()
            
            # Notify that a remote is connected
            self.remote_is_up()
            
            # Start receive thread
            self._connected = True
            self._receive_thread = threading.Thread(target=self._receive_loop)
            self._receive_thread.daemon = True
            self._receive_thread.start()
            
            # Request remote functions
            self.remote.jrpc.call('system.listComponents', [], self._on_components_listed)
            
        except Exception as e:
            print(f"Connection error: {str(e)}")
            self.ws_error(e)
    
    def _on_components_listed(self, err, result):
        """Handle remote component listing."""
        if err:
            print(f"Error listing components: {err}")
            return
        
        if result:
            try:
                method_names = list(result.keys())
                print(f"Remote components available: {method_names}")
                self.setup_fns(method_names, self.remote)
            except Exception as e:
                print(f"Error processing component listing: {str(e)}")
    
    def _receive_loop(self):
        """Run a loop to receive messages from the WebSocket."""
        while self._connected and self.ws:
            try:
                # Use a timeout to prevent blocking forever
                self.ws.settimeout(1.0)  # 1 second timeout
                message = self.ws.recv()
                if message:
                    print(f"Client received message: {message[:100]}{'...' if len(message) > 100 else ''}")
                    self.remote.jrpc.receive(message)
            except Exception as e:
                # If it's a timeout, just continue
                import socket
                if isinstance(e, socket.timeout):
                    continue
                    
                print(f"WebSocket receive error: {str(e)}")
                self._disconnect()
                break
    
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
    
    
    
    def is_connected(self):
        """
        Check if the client is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected and self.remote is not None
    
    def remote_is_up(self):
        """Called when the remote server is up."""
        print("JRPCClient::remote_is_up")
        super().remote_is_up()
    
    def _disconnect(self):
        """Handle disconnection internally."""
        self._connected = False
        if self.remote:
            self.remote_disconnected(self.remote.uuid)
    
    def remote_disconnected(self, uuid):
        """
        Called when the remote disconnects.
        
        Args:
            uuid: UUID of the disconnected remote
        """
        super().remote_disconnected(uuid)
        self._connected = False
    
    def close(self):
        """Close the WebSocket connection and clean up."""
        self._connected = False
        
        # Clean up receive thread
        if hasattr(self, '_receive_thread') and self._receive_thread.is_alive():
            try:
                self._receive_thread.join(1.0)
            except Exception:
                pass  # Thread may already be dead
        
        # Close WebSocket
        if self.ws:
            try:
                self.ws.close()
                self.ws = None
            except Exception as e:
                print(f"Error closing WebSocket: {str(e)}")
        
        # Clean up remote
        if self.remote:
            self.rm_remote(None, self.remote.uuid)
            self.remote = None
