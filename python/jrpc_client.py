#!/usr/bin/env python3
"""
JSON-RPC 2.0 Client implementation with WebSocket support
"""
import asyncio
import websockets
import json
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
            # Start message handler
            asyncio.create_task(self._message_handler())
            
            # Get available components
            response = await self.call_method('system.listComponents')
            debug_log(f"Connected to server at {self.uri}", self.debug)
            debug_log(f"Available components: {response}", self.debug)
            return True
            
        except Exception as e:
            debug_log(f"Connection failed: {e}", self.debug)
            return False

    async def _message_handler(self):
        """Handle incoming messages from server"""
        await self.process_incoming_messages(self.ws)

    async def call_method(self, method: str, params=None):
        """Make an RPC call to the server
        
        Args:
            method: Method name to call
            params: Parameters to pass to method
            
        Returns:
            Result from remote method
        """
        if not self.ws:
            raise RuntimeError("Not connected to server")
            
        # Create request
        request, request_id = self.create_request(method, params)
        return await self.send_and_wait(request, request_id)

    async def close(self):
        """Close the connection"""
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.pending_requests.clear()
            
    async def connect_to_server(self):
        """Connect to the main server"""
        return await self.connect()
        
    async def start_server(self):
        """Start the client's server for receiving callbacks"""
        # For now just connect to receive callbacks
        return await self.connect()

    def __getitem__(self, class_name: str):
        """Allow dictionary-style access for RPC classes"""
        return type('RPCClass', (), {
            '__getattr__': lambda _, method: lambda *args: self.call_method(
                f"{class_name}.{method}", args
            )
        })()
