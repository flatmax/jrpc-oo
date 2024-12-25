#!/usr/bin/env python3
"""
JSON-RPC 2.0 Common base class for client and server implementations
"""
import json
import asyncio
import websockets
import inspect
from typing import Dict, Any, Optional, Callable

class JRPCCommon:
    def __init__(self):
        self.instances = {}  # Registered class instances
        self.remotes = {}    # Connected remote endpoints
        self.remote_timeout = 60
        
    def register_instance(self, instance, class_name: Optional[str] = None):
        """Register a class instance for RPC access"""
        if class_name is None:
            class_name = instance.__class__.__name__
        self.instances[class_name] = instance
        
    async def handle_message(self, websocket, message):
        """Handle incoming JSON-RPC message"""
        try:
            parsed = json.loads(message)
            method_name = parsed.get('method')
            params = parsed.get('params', {})
            request_id = parsed.get('id')
            
            # Extract args from params if present
            if isinstance(params, dict) and 'args' in params:
                args = params['args']
            else:
                args = params if isinstance(params, list) else [params]

            # Handle system methods
            if method_name == 'system.listComponents':
                result = self.list_components()
            # Handle instance methods
            elif '.' in method_name:
                class_name, method = method_name.split('.')
                instance = self.instances.get(class_name)
                if instance and hasattr(instance, method):
                    method_obj = getattr(instance, method)
                    if asyncio.iscoroutinefunction(method_obj):
                        result = await method_obj(*args)
                    else:
                        result = await asyncio.get_event_loop().run_in_executor(
                            None, method_obj, *args
                        )
                else:
                    raise Exception(f'Method {method_name} not found')
            else:
                raise Exception(f'Invalid method name format: {method_name}')

            response = {
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            }
            
        except Exception as e:
            response = {
                'jsonrpc': '2.0',
                'error': {'code': -32603, 'message': str(e)},
                'id': request_id if 'request_id' in locals() else None
            }
            
        await websocket.send(json.dumps(response))
        return json.dumps(response)

    def list_components(self):
        """List all registered components and their methods"""
        components = {}
        for class_name, instance in self.instances.items():
            for name, method in inspect.getmembers(instance, inspect.ismethod):
                if not name.startswith('_'):
                    method_name = f"{class_name}.{name}"
                    components[method_name] = True
        return components

    async def call_remote(self, websocket, method: str, params=None):
        """Call a method on the remote endpoint"""
        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': {'args': params} if params else [],
            # Don't include ID for notifications
        }
        
        print(f"DEBUG: Sending request: {json.dumps(request)[:100]}...")
        await websocket.send(json.dumps(request))
        print(f"DEBUG: Request sent")
        return True
