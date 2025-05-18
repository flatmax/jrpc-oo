"""
Server implementation for JRPC over WebSockets.
"""
import asyncio
import websockets
from typing import Optional, Dict, Any

from .JRPCCommon import JRPCCommon


class JRPCServer(JRPCCommon):
    """Server implementation for JRPC over WebSockets."""
    
    def __init__(self, port: int = 9000, remote_timeout: int = 60):
        """Initialize the JRPC server.
        
        Args:
            port: Port to listen on
            remote_timeout: Timeout for remote connections in seconds
        """
        super().__init__()
        self.port = port
        self.remote_timeout = remote_timeout
        self.server = None
        self.clients = {}
        
    async def start(self):
        """Start the WebSocket server."""
        self.server = await websockets.serve(self.handle_connection, "0.0.0.0", self.port)
        print(f"JRPC Server started on port {self.port}")
        
    async def handle_connection(self, websocket):
        """Handle a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
        """
        # Create the remote with proper async handling
        remote = self.create_remote(websocket)
        
        # Define message handler function
        async def on_message_handler(message):
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            remote.receive(message)
        
        try:
            # Wait for messages from the client
            async for message in websocket:
                await on_message_handler(message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.rm_remote(None, remote.uuid)
    
    def add_class(self, cls_instance, obj_name=None):
        """Add a class to expose its methods to remote clients.
        
        Args:
            cls_instance: The class instance to expose
            obj_name: Optional name to use instead of the class name
        """
        super().add_class(cls_instance, obj_name)
        
    def remote_is_up(self):
        """Called when a remote connection is established."""
        print("JRPCServer::remote_is_up")
        
    def setup_done(self):
        """Called when setup is complete."""
        print("JRPCServer::setup_done")
        
    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("JRPC Server stopped")
