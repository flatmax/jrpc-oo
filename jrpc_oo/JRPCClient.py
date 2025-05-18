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
        self._setup_done_in_progress = False
        self._last_sync_time = {}
        
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
        # Prevent recursive calls to setup_done
        if hasattr(self, '_setup_done_in_progress') and self._setup_done_in_progress:
            print("Setup already in progress, skipping recursive call")
            return
            
        try:
            self._setup_done_in_progress = True
            print("JRPCClient: Remote functions setup complete")
            
            # Now make sure our classes are properly exposed to all remotes
            if hasattr(self, 'remotes') and self.remotes and hasattr(self, 'classes') and self.classes:
                current_time = time.time()
                
                for remote_id, remote in self.remotes.items():
                    # Skip if we've synced with this remote recently
                    if hasattr(self, '_last_sync_time') and remote_id in self._last_sync_time:
                        last_sync = self._last_sync_time[remote_id]
                        if current_time - last_sync < 5:  # Don't re-sync more than once every 5 seconds
                            print(f"Skipping re-sync for {remote_id} - too soon since last sync")
                            continue
                    
                    # Re-expose all classes to this remote
                    for cls in self.classes:
                        remote.expose(cls)
                    
                    # Force an upgrade to update the remote's method list
                    remote.upgrade()
                    
                    # Track sync time
                    self._last_sync_time[remote_id] = current_time
                    
                    # Call system.listComponents again to ensure both sides are in sync
                    print(f"Re-requesting components from remote {remote_id}")
                    remote.call('system.listComponents', [], lambda err, result: 
                        print(f"Re-sync error: {err}") if err else 
                        self.process_remote_components(remote_id, result))
            
            super().setup_done()
        finally:
            self._setup_done_in_progress = False
    
    def process_remote_components(self, remote_id, result):
        """Process available components from remote"""
        if result:
            component_list = list(result.keys())
            print(f"Re-sync successful, remote {remote_id} components: {component_list}")
            
            # Check if we already have all these functions registered
            already_registered = True
            if hasattr(self, 'call'):
                for fn in component_list:
                    if fn not in self.call:
                        already_registered = False
                        break
            else:
                already_registered = False
                
            if already_registered:
                print(f"All functions already registered for remote {remote_id}, skipping setup_fns")
                return
                
            # Find the remote with this ID
            if hasattr(self, 'remotes') and remote_id in self.remotes:
                remote = self.remotes[remote_id]
                # Set up the functions from the result
                self.setup_fns(component_list, remote)
    
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
        
        # Wait for receive thread to terminate if it exists
        if hasattr(self, '_receive_thread') and self._receive_thread.is_alive():
            try:
                self._receive_thread.join(1.0)  # Give thread 1 second to terminate
            except Exception as e:
                print(f"Error joining receive thread: {str(e)}")
        
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                print(f"Error closing WebSocket: {str(e)}")
