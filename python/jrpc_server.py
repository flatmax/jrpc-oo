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
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python.jrpc_common import JRPCCommon
from python.debug_utils import debug_log

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
            # Wait for client to discover our components first
            await self.wait_connection_ready()
            
            # Then discover client's components
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
        print(f"Server running at {protocol}://{self.host}:{self.port}", self.debug)
        
    def serve_forever(self):
        """Start serving requests forever"""
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            
    async def start_background(self):
        """Start the server in the background without blocking"""
        protocol = 'wss' if self.use_ssl else 'ws'
        debug_log(f"Starting {protocol}://{self.host}:{self.port}", self.debug)
        
        server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ssl=self.ssl_context
        )
        print(f"Server running at {protocol}://{self.host}:{self.port}")
        return server

    def run_in_thread(self):
        """Run the server in a background thread with its own event loop"""
        import threading
        
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            server = loop.run_until_complete(self.start_background())
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.close()
                loop.run_until_complete(server.wait_closed())
                loop.close()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        return thread
