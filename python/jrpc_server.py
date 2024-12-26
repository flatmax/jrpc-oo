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
    def __init__(self, host='0.0.0.0', port=9000, use_ssl=False, debug=False):
        """Initialize JSON-RPC server
        
        Args:
            host: Host to bind to
            port: Port for server to listen on
            use_ssl: Whether to use SSL/WSS
            debug: Enable debug logging
        """
        super().__init__(debug)
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.ssl_context = None
        if use_ssl:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(
                './cert/server.crt',
                './cert/server.key'
            )

    async def handle_client(self, websocket, path):
        """Handle individual client connections"""
        client_id = str(id(websocket))
        self.ws = websocket  # Store the websocket connection
        debug_log(f"New client connected: {client_id}", self.debug)
        try:
            async for message in websocket:
                try:
                    # Print raw message
                    debug_log(f"\n>>> Message received from client {client_id}:", self.debug)
                    debug_log(f"{message}", self.debug)
                    
                    # Parse JSON-RPC message
                    if isinstance(message, bytes):
                        message = message.decode('utf-8')
                    msg_data = json.loads(message)
                    debug_log(f"\n>>> Parsed JSON request:", self.debug)
                    debug_log(f"{json.dumps(msg_data, indent=4)}", self.debug)
                    
                    # Process message and get response
                    response = await self.process_message(msg_data)
                    debug_log(f"\n<<< Sending response:", self.debug)
                    debug_log(f"{json.dumps(response, indent=4)}", self.debug)
                    
                    # Send response back to client
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError as e:
                    debug_log(f"Invalid JSON received: {e}", self.debug)
                    await websocket.send(json.dumps({
                        "error": f"Invalid JSON: {str(e)}"
                    }))
                except Exception as e:
                    debug_log(f"Error processing message: {e}", self.debug)
                    await websocket.send(json.dumps({
                        "error": f"Internal error: {str(e)}"
                    }))
        except websockets.exceptions.ConnectionClosed:
            debug_log(f"Client {client_id} disconnected", self.debug)
        except Exception as e:
            debug_log(f"Unexpected error with client {client_id}: {e}", self.debug)

    async def process_message(self, message):
        """Process incoming JSON-RPC message"""
        try:
            # Handle the message using common handler
            return await self.handle_message(message)
        except Exception as e:
            return {
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': str(e)},
                'id': message.get('id')
            }

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
