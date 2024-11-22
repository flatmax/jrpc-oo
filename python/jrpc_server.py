#!/usr/bin/env python3
"""
JSON-RPC 2.0 Server implementation with WebSocket support and class-based RPC
"""
import json
import inspect
import asyncio
import websockets
import traceback


class JRPCServer:
    def __init__(self, host='localhost', port=8080):
        """Initialize WebSocket RPC server"""
        self.host = host
        self.port = port
        self.instances = {}
        self._system_methods = {
            'system.listComponents': self.list_components
        }

    def list_components(self):
        """List all registered components and their methods
        This is called by jrpc-oo's setupRemote to discover available instances and methods
        Returns a dictionary of method names in the format {class_name.method_name: True}
        """
        components = {}
        for class_name, instance in self.instances.items():
            for name, method in inspect.getmembers(instance, inspect.ismethod):
                if not name.startswith('_'):
                    method_name = f"{class_name}.{name}"
                    components[method_name] = True
        return components

    def register_instance(self, instance, class_name=None):
        """Register a class instance for RPC access"""
        if class_name is None:
            class_name = instance.__class__.__name__
        self.instances[class_name] = instance

    async def _handle_ws_message(self, websocket, message):
        """Handle incoming WebSocket message"""
        try:
            # Parse message as JSON-RPC
            parsed = json.loads(message)

            # Get method name and parameters
            method_name = parsed.get('method')
            params = parsed.get('params', {})
            
            # Extract args from params if present
            if isinstance(params, dict) and 'args' in params:
                args = params['args']
            else:
                args = params if isinstance(params, list) else [params]

            # Handle system methods first
            if method_name in self._system_methods:
                result = self._system_methods[method_name]()
                response = json.dumps({
                    'jsonrpc': '2.0',
                    'result': result,
                    'id': parsed.get('id')
                })
            # Handle instance methods
            elif '.' in method_name:
                class_name, method = method_name.split('.')
                instance = self.instances.get(class_name)
                if instance and hasattr(instance, method):
                    method_obj = getattr(instance, method)
                    result = await asyncio.get_event_loop().run_in_executor(None, method_obj, *args)
                    response = json.dumps({
                        'jsonrpc': '2.0',
                        'result': result,
                        'id': parsed.get('id')
                    })
                else:
                    response = json.dumps({
                        'jsonrpc': '2.0',
                        'error': {'code': -32601, 'message': f'Method {method_name} not found'},
                        'id': parsed.get('id')
                    })
            else:
                response = json.dumps({
                    'jsonrpc': '2.0',
                    'error': {'code': -32601, 'message': f'Invalid method name format: {method_name}'},
                    'id': parsed.get('id')
                })

            await websocket.send(response)

        except Exception as e:
            error_response = json.dumps({
                'jsonrpc': '2.0',
                'error': {'code': -32603, 'message': str(e)},
                'id': parsed.get('id') if 'parsed' in locals() else None
            })
            await websocket.send(error_response)

    async def _handle_ws_connection(self, websocket):
        """Handle WebSocket connection"""
        try:
            async for message in websocket:
                await self._handle_ws_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass

    async def start(self):
        """Start the WebSocket server"""
        self.ws_server = await websockets.serve(
            self._handle_ws_connection,
            self.host,
            self.port,
            subprotocols=['jsonrpc']
        )
