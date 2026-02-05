"""
Client implementation for JRPC over WebSockets.
"""
import asyncio
import websockets
from typing import Optional


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
        self._message_task = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 1.0
        
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
    
    async def reconnect(self, delay: float = None):
        """Attempt to reconnect to the server.
        
        Args:
            delay: Optional delay before reconnecting (uses _reconnect_delay if not specified)
            
        Returns:
            True if reconnection successful, False otherwise
        """
        if delay is None:
            delay = self._reconnect_delay
            
        self._reconnect_attempts += 1
        
        if self._reconnect_attempts > self._max_reconnect_attempts:
            print(f"Max reconnect attempts ({self._max_reconnect_attempts}) exceeded")
            return False
            
        print(f"Reconnecting in {delay}s (attempt {self._reconnect_attempts}/{self._max_reconnect_attempts})...")
        await asyncio.sleep(delay)
        
        # Store attempt count before connect() which may modify state
        attempts_before = self._reconnect_attempts
        
        await self.connect()
        
        # Check if connection succeeded
        if self.connected:
            self._reconnect_attempts = 0  # Reset on success
            self._reconnect_delay = 1.0
            return True
        else:
            # Restore attempt count (connect resets it on internal failure)
            self._reconnect_attempts = attempts_before
            # Exponential backoff
            self._reconnect_delay = min(self._reconnect_delay * 2, 30.0)
            return False
    
    def reset_reconnect_state(self):
        """Reset reconnection state (call after successful manual connect)."""
        self._reconnect_attempts = 0
        self._reconnect_delay = 1.0
