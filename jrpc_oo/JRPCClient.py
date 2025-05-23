"""
Client implementation for JRPC over WebSockets.
"""
import asyncio
import websockets
from typing import Optional, Dict, Any

from .JRPCCommon import JRPCCommon


class JRPCClient(JRPCCommon):
    """Client implementation for JRPC over WebSockets."""
    
    def __init__(self, server_uri: str, remote_timeout: int = 60):
        """Initialize the JRPC client.
        
        Args:
            server_uri: URI of the server to connect to (ws://host:port)
            remote_timeout: Timeout for remote connections in seconds
        """
        super().__init__()
        self.server_uri = server_uri
        self.remote_timeout = remote_timeout
        self.ws = None
        self.connected = False
        
    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            self.ws = await websockets.connect(self.server_uri)
            self.connected = True
            print(f"Connected to {self.server_uri}")
            
            # Create remote with proper async handling
            remote = self.create_remote(self.ws)
            
            # Define message handler
            async def on_message_handler(message):
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                remote.receive(message)
            
            # Handle incoming messages
            try:
                async for message in self.ws:
                    await on_message_handler(message)
            except websockets.exceptions.ConnectionClosed:
                self.connected = False
                print(f"Disconnected from {self.server_uri}")
                if hasattr(self.ws, 'on_close'):
                    self.ws.on_close()
                
        except Exception as e:
            self.connected = False
            self.setup_skip()
            print(f"Failed to connect to {self.server_uri}: {e}")
    
    def add_class(self, cls_instance, obj_name=None):
        """Add a class to expose its methods to the server.
        
        Args:
            cls_instance: The class instance to expose
            obj_name: Optional name to use instead of the class name
        """
        super().add_class(cls_instance, obj_name)
    
    def remote_is_up(self):
        """Called when the remote connection is established."""
        print("JRPCClient::remote_is_up")
    
    def setup_done(self):
        """Called when the setup is complete."""
        print("JRPCClient::setup_done - Server connected")
        
    def setup_skip(self):
        """Called when setup fails."""
        print("JRPCClient::setup_skip - Connection failed")
        
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.ws and self.connected:
            await self.ws.close()
            self.connected = False
            print(f"Disconnected from {self.server_uri}")
