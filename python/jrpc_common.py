#!/usr/bin/env python3
"""
JSON-RPC 2.0 Common base class for client and server implementations.

This module provides the shared functionality between client and server including:
- Message formatting and parsing
- Request/response handling
- WebSocket communication
- SSL/TLS support
- Component registration and discovery
- Error handling
"""
import asyncio
import json
import uuid
import websockets
from expose_class import ExposeClass
from debug_utils import debug_log

class JRPCCommon:
    def __init__(self, host='0.0.0.0', port=9000, use_ssl=False, debug=False):
        """Initialize common RPC settings
        
        Args:
            host: Host address to use
            port: Port number to use
            use_ssl: Whether to use SSL/WSS
            debug: Enable debug logging
        """
        self.debug = debug
        self.instances = {}  # Registered class instances
        self.remotes = {}    # Connected remote endpoints
        self.remote_timeout = 60
        self.pending_requests = {}  # Track pending RPC requests
        
        # URL handling
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        protocol = 'wss' if use_ssl else 'ws'
        self.uri = f"{protocol}://{host}:{port}"
        
        # SSL context
        self.ssl_context = self.setup_ssl() if use_ssl else None
        
    def setup_ssl(self):
        """Abstract method to setup SSL context
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement setup_ssl()")
        
    def add_class(self, instance, class_name=None):
        """Register a class instance for RPC access"""
        if class_name is None:
            class_name = instance.__class__.__name__
        self.instances[class_name] = instance
        if hasattr(instance, 'set_rpc'):
            instance.set_rpc(self)

    def list_components(self):
        """List all registered components and their methods"""
        components = {}
        for class_name, instance in self.instances.items():
            methods = [name for name in dir(instance) 
                      if callable(getattr(instance, name)) and not name.startswith('_')]
            for method in methods:
                method_name = f"{class_name}.{method}"
                components[method_name] = True
        return components

    async def handle_message(self, message_data):
        """Process an incoming JSON-RPC message"""
        try:
            if not isinstance(message_data, dict):
                message_data = json.loads(message_data)
                
            if 'jsonrpc' not in message_data or message_data['jsonrpc'] != '2.0':
                return self.error_response(-32600, 'Invalid Request', message_data.get('id'))

            if 'method' in message_data:  # This is a request
                return await self.handle_request(message_data)
            elif 'result' in message_data or 'error' in message_data:  # This is a response
                return await self.handle_response(message_data)
            else:
                return self.error_response(-32600, 'Invalid Request', message_data.get('id'))
                
        except Exception as e:
            return self.error_response(-32603, f'Internal error: {str(e)}', None)

    async def handle_request(self, request):
        """Handle an incoming RPC request"""
        method = request.get('method')
        params = request.get('params', [])
        msg_id = request.get('id')

        if not method:
            return self.error_response(-32600, 'Method not specified', msg_id)

        try:
            if method == 'system.listComponents':
                result = self.list_components()
                return self.result_response(result, msg_id)

            # Find and execute the method
            for class_name, instance in self.instances.items():
                if method.startswith(class_name + '.'):
                    method_name = method.split('.')[-1]
                    if hasattr(instance, method_name):
                        method_func = getattr(instance, method_name)
                        if callable(method_func):
                            # Handle wrapped args parameter format from JS client
                            if isinstance(params, dict) and 'args' in params:
                                if isinstance(params['args'], list):
                                    result = await method_func(*params['args'])
                                else:
                                    result = await method_func(params['args'])
                            elif isinstance(params, dict):
                                result = await method_func(**params)
                            else:
                                result = await method_func(*params)
                            return self.result_response(result, msg_id)

            return self.error_response(-32601, f'Method {method} not found', msg_id)

        except Exception as e:
            return self.error_response(-32000, str(e), msg_id)

    async def handle_response(self, response):
        """Handle an incoming RPC response"""
        msg_id = response.get('id')
        if msg_id in self.pending_requests:
            future = self.pending_requests.pop(msg_id)
            if 'result' in response:
                future.set_result(response['result'])
            elif 'error' in response:
                future.set_exception(Exception(response['error']))

    def result_response(self, result, msg_id):
        """Create a JSON-RPC result response"""
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': msg_id
        }

    def error_response(self, code, message, msg_id):
        """Create a JSON-RPC error response"""
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': code,
                'message': message
            },
            'id': msg_id
        }

    def create_request(self, method, params=None):
        """Create a JSON-RPC request message"""
        request_id = str(uuid.uuid4())
        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params if params is not None else [],
            'id': request_id
        }
        return request, request_id

    async def send_message(self, message):
        """Send a message through websocket"""
        if not hasattr(self, 'ws') or self.ws is None:
            raise RuntimeError("No websocket connection available")
        await self.ws.send(json.dumps(message))

    async def send_and_wait(self, request, request_id, timeout=None):
        """Send a request and wait for response"""
        if timeout is None:
            timeout = self.remote_timeout

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send request
            await self.send_message(request)
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            self.pending_requests.pop(request_id, None)
            raise TimeoutError(f"Request timed out")
        except Exception as e:
            self.pending_requests.pop(request_id, None)
            raise RuntimeError(f"RPC call failed: {e}")

    async def process_incoming_messages(self, websocket):
        """Common handler for processing incoming websocket messages"""
        try:
            async for message in websocket:
                try:
                    # Parse JSON-RPC message
                    if isinstance(message, bytes):
                        message = message.decode('utf-8')
                    msg_data = json.loads(message)
                    debug_log(f"Received message: {message}", self.debug)
                    
                    # Process message and get response
                    response = await self.handle_message(msg_data)
                    
                    if response:  # Only send response if one was generated
                        debug_log(f"Sending response: {json.dumps(response)}", self.debug)
                        await self.send_message(response)
                        
                except json.JSONDecodeError as e:
                    debug_log(f"Invalid JSON received: {e}", self.debug)
                    await self.send_message({
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Invalid JSON: {str(e)}"},
                        "id": None
                    })
                except Exception as e:
                    debug_log(f"Error processing message: {e}", self.debug)
                    await self.send_message({
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                        "id": None
                    })
        except websockets.exceptions.ConnectionClosed:
            debug_log("Connection closed", self.debug)
        except Exception as e:
            debug_log(f"Unexpected error in message processing: {e}", self.debug)
