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
            # Validate JSON-RPC message structure
            if 'jsonrpc' not in message or message['jsonrpc'] != '2.0':
                return {
                    'jsonrpc': '2.0',
                    'error': {'code': -32600, 'message': 'Invalid Request'},
                    'id': message.get('id')
                }

            method_name = message.get('method')
            params = message.get('params', {})
            msg_id = message.get('id')

            if not method_name:
                return {
                    'jsonrpc': '2.0',
                    'error': {'code': -32600, 'message': 'Method not specified'},
                    'id': msg_id
                }

            # Handle system.listComponents
            if method_name == 'system.listComponents':
                result = self.list_components()
                return {
                    'jsonrpc': '2.0',
                    'result': result,
                    'id': msg_id
                }

            # Find and call the appropriate method
            for class_name, instance in self.instances.items():
                if method_name.startswith(class_name + '.'):
                    method = getattr(instance, method_name.split('.')[-1], None)
                    if callable(method):
                        # Handle wrapped args parameter format from JS client
                        if isinstance(params, dict) and 'args' in params:
                            if isinstance(params['args'], list):
                                result = await method(*params['args'])
                            else:
                                result = await method(params['args'])
                        elif isinstance(params, dict):
                            result = await method(**params)
                        else:
                            result = await method(*params)
                        return {
                            'jsonrpc': '2.0',
                            'result': result,
                            'id': msg_id
                        }

            return {
                'jsonrpc': '2.0',
                'error': {'code': -32601, 'message': f'Method {method_name} not found'},
                'id': msg_id
            }

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
