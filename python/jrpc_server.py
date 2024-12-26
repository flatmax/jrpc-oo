#!/usr/bin/env python3
"""
JSON-RPC 2.0 Server implementation using jsonrpclib-pelix with SSL support
"""
import ssl
import json
import asyncio
import websockets
from jsonrpclib import Server
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
        await self.process_incoming_messages(websocket)


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
