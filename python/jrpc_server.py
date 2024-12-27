"""
JSON-RPC 2.0 Server implementation with WebSocket and SSL support.

This module provides a WebSocket server that:
- Accepts JSON-RPC 2.0 requests
- Manages client connections
- Exposes Python classes and methods via RPC
- Supports SSL/TLS encryption
- Handles multiple concurrent clients
"""
import ssl
import asyncio
import websockets
from jrpc_common import JRPCCommon
from debug_utils import debug_log

class JRPCServer(JRPCCommon):

    def setup_ssl(self):
        """Setup SSL context for server"""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            './cert/server.crt',
            './cert/server.key'
        )
        return ssl_context

    async def handle_client(self, websocket, path):
        """Handle individual client connections"""
        client_id = str(id(websocket))
        self.ws = websocket  # Store the websocket connection
        debug_log(f"New client connected: {client_id}", self.debug)
        
        # Start message processing in background task
        process_messages_task = asyncio.create_task(
            self.process_incoming_messages(websocket)
        )
        
        try:
            # Do component discovery
            await self.discover_components()
            debug_log("Server completed component discovery", self.debug)
            
            # Keep connection alive
            await process_messages_task
            
        except Exception as e:
            debug_log(f"Error in handle_client: {e}", self.debug)
            if not process_messages_task.done():
                process_messages_task.cancel()


    def start(self):
        """Start the WebSocket server"""
        protocol = 'wss' if self.use_ssl else 'ws'
        debug_log(f"Starting {protocol}://{self.host}:{self.port}", self.debug)
        
        start_server = websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ssl=self.ssl_context
        )
        
        # Start the async event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        debug_log(f"Server running at {protocol}://{self.host}:{self.port}", self.debug)
        
    def serve_forever(self):
        """Start serving requests forever"""
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
