#!/usr/bin/env python3
"""
JSON-RPC 2.0 Common base class for client and server implementations
"""
import asyncio
import json
import uuid
from expose_class import ExposeClass

class JRPCCommon:
    def __init__(self, debug=False):
        self.debug = debug
        self.instances = {}  # Registered class instances
        self.remotes = {}    # Connected remote endpoints
        self.remote_timeout = 60
        self.pending_requests = {}  # Track pending RPC requests
        
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
                            if isinstance(params, dict):
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
