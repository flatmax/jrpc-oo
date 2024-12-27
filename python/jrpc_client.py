"""
JSON-RPC 2.0 Client implementation with WebSocket support.

This module provides a WebSocket-based JSON-RPC 2.0 client implementation that can:
- Connect to a JSON-RPC server over WebSocket
- Make remote procedure calls
- Handle responses and errors
- Support SSL/TLS encryption
- Provide async/await interface
"""
import asyncio
import websockets
import ssl
from jrpc_common import JRPCCommon
from debug_utils import debug_log

class JRPCClient(JRPCCommon):

    ws = None

    def setup_ssl(self):
        """Setup SSL context for client"""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations('./cert/server.crt')
        return ssl_context
        
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.ws = await websockets.connect(
                self.uri,
                ssl=self.ssl_context
            )
            
            # Start message handler in background task
            self.message_task = asyncio.create_task(
                self.process_incoming_messages(self.ws)
            )
            
            # Give message handler a moment to start
            await asyncio.sleep(0.1)
            
            # Discover server components
            success = await self.discover_components()
            if success:
                # Wait for both sides to be ready
                await self.wait_connection_ready()
                debug_log(f"Connected to server at {self.uri}", self.debug)
                return True
            
        except Exception as e:
            debug_log(f"Connection failed: {e}", self.debug)
            if hasattr(self, 'message_task'):
                self.message_task.cancel()
            return False

    async def close(self):
        """Close the connection"""
        if hasattr(self, 'message_task'):
            self.message_task.cancel()
            try:
                await self.message_task
            except asyncio.CancelledError:
                pass
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.pending_requests.clear()

