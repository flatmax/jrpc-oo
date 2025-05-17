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
import json
import uuid
import time
from websocket import WebSocket, create_connection
from .expose_class import ExposeClass
from .debug_utils import debug_log

class JRPCCommon:
    # Default values that subclasses will override
    is_server = False
    is_client = False
    pending_requests = {}

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
        
        # Event to track when component discovery is complete
        from threading import Event
        self.connection_ready_event = Event()
        
        # Add system class by default
        self.add_class(self.System(self), 'System')
        
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
            if class_name != 'System':  # Don't expose System class methods
                methods = [name for name in dir(instance) 
                          if callable(getattr(instance, name)) and not name.startswith('_')]
                for method in methods:
                    method_name = f"{class_name}.{method}"
                    components[method_name] = True
                    debug_log(f"Added method to component list: {method_name}", self.debug)
        debug_log(f"Complete component list: {components}", self.debug)
        return components

    class System:
        """Built-in system methods"""
        def __init__(self, parent):
            self.parent = parent
                
        def listComponents(self):
            """List available RPC methods"""
            return self.parent.list_components()

    def handle_message(self, message_data):
        """Process an incoming JSON-RPC message"""
        try:
            debug_log(f"handle_message: Processing message: {message_data}", self.debug)
            
            if not isinstance(message_data, dict):
                debug_log("handle_message: Converting string to dict", self.debug)
                message_data = json.loads(message_data)
                
            if 'jsonrpc' not in message_data or message_data['jsonrpc'] != '2.0':
                debug_log("handle_message: Invalid JSON-RPC version", self.debug)
                return self.error_response(-32600, 'Invalid Request', message_data.get('id'))

            # Check if this is a response
            if ('result' in message_data or 'error' in message_data) and 'id' in message_data:
                msg_id = message_data.get('id')
                debug_log(f"Received response for request ID: {msg_id}", self.debug)
                if hasattr(self, 'pending_responses'):
                    debug_log(f"Storing response in pending_responses", self.debug)
                    self.pending_responses[msg_id] = message_data
                return None  # Don't send a response to a response
            
            # Handle method calls
            if message_data.get('method') == 'system.listComponents':
                debug_log("Received listComponents request", self.debug)
                # Just handle normally - don't do special server discovery
                return self.handle_request(message_data)
            elif 'method' in message_data:
                debug_log(f"handle_message: Processing request for method: {message_data['method']}", self.debug)
                return self.handle_request(message_data)
            else:
                debug_log("handle_message: Invalid message format", self.debug)
                return self.error_response(-32600, 'Invalid Request', message_data.get('id'))

            # Check if this is a response
            if ('result' in message_data or 'error' in message_data) and 'id' in message_data:
                msg_id = message_data.get('id')
                if msg_id in self.pending_requests:
                    debug_log(f"handle_message: Found pending request for response {msg_id}", self.debug)
                    future = self.pending_requests[msg_id]
                    if 'result' in message_data:
                        future.set_result(message_data['result'])
                    else:
                        future.set_exception(RuntimeError(message_data['error'].get('message', 'Unknown error')))
                    self.pending_requests.pop(msg_id, None)
                    return None  # Don't send a response to a response

            # Handle responses to system.listComponents
            elif ('result' in message_data or 'error' in message_data) and message_data.get('id'):
                return None
            # Then handle method calls
            elif 'method' in message_data:
                debug_log(f"handle_message: Processing request for method: {message_data['method']}", self.debug)
                return self.handle_request(message_data)
            else:
                debug_log("handle_message: Invalid message format", self.debug)
                return self.error_response(-32600, 'Invalid Request', message_data.get('id'))

        except Exception as e:
            debug_log(f"handle_message: Error processing message: {str(e)}", self.debug)
            return self.error_response(-32603, f'Internal error: {str(e)}', message_data.get('id'))

    def handle_request(self, request):
        """Handle an incoming RPC request"""
        method = request.get('method')
        params = request.get('params', [])
        msg_id = request.get('id')

        debug_log(f"handle_request: Processing method {method} with ID {msg_id}", self.debug)
        
        try:
            return self._execute_method(method, params, msg_id)
        except Exception as e:
            return self.error_response(-32000, str(e), msg_id)

    def _execute_method(self, method, params, msg_id):
        """Execute a method call in a worker thread"""

        if not method:
            return self.error_response(-32600, 'Method not specified', msg_id)

        try:
            # Only handle system.listComponents on server side
            if method == 'system.listComponents' and hasattr(self, 'instances'):
                debug_log("handle_request: Handling system.listComponents", self.debug)
                debug_log(f"handle_request: Current instances: {list(self.instances.keys())}", self.debug)
                result = {}
                for class_name, instance in self.instances.items():
                    debug_log(f"handle_request: Processing class {class_name}", self.debug)
                    methods = [name for name in dir(instance) 
                             if callable(getattr(instance, name)) and not name.startswith('_')]
                    for method in methods:
                        method_name = f"{class_name}.{method}"
                        result[method_name] = True
                        debug_log(f"handle_request: Added method {method_name}", self.debug)
                
                debug_log(f"handle_request: Final components list: {result}", self.debug)
                response = self.result_response(result, msg_id)
                debug_log(f"handle_request: Generated response: {response}", self.debug)
                return response

            # Find and execute the method
            for class_name, instance in self.instances.items():
                if method.startswith(class_name + '.'):
                    method_name = method.split('.')[-1]
                    if hasattr(instance, method_name):
                        method_func = getattr(instance, method_name)
                        if callable(method_func):
                            
                            # Handle wrapped args parameter format from JS client
                            try:
                                args = []
                                kwargs = {}
                                
                                if isinstance(params, dict):
                                    if 'args' in params:
                                        # This is how js-jrpc sends parameters
                                        if isinstance(params['args'], list):
                                            args = params['args']
                                        else:
                                            args = [params['args']]
                                    else:
                                        # Handle old-style dict params as kwargs
                                        kwargs = params
                                elif isinstance(params, list):
                                    # Handle direct list as positional args
                                    args = params
                                elif params is not None:
                                    # Handle single non-dict, non-list param
                                    args = [params]
                                
                                if kwargs:
                                    result = method_func(**kwargs)
                                else:
                                    result = method_func(*args)
                                    
                                return self.result_response(result, msg_id)
                            except Exception as e:
                                print(f"Method execution error: {str(e)}")
                                import traceback
                                print(f"Traceback: {traceback.format_exc()}")
                                return self.error_response(-32603, str(e), msg_id)

            return self.error_response(-32601, f'Method {method} not found', msg_id)

        except Exception as e:
            return self.error_response(-32000, str(e), msg_id)


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

    def send_message(self, message, client=None):
        """Send a message through websocket"""
        if not hasattr(self, 'ws') and not client:
            raise RuntimeError("No websocket connection available")
            
        # Always convert to JSON string before sending
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        elif isinstance(message, str):
            if not (message.startswith('{') or message.startswith('[')):
                message = json.dumps(message)
                
        debug_log(f"Sending message: {message}", self.debug)
        
        # Server sends through server.send_message
        if self.is_server:
            if hasattr(self, 'server') and hasattr(self.server, 'send_message'):
                self.server.send_message(client if client else self.ws, message)
            else:
                raise RuntimeError("Server not properly initialized for sending")
        # Client sends directly through websocket
        else:
            if hasattr(self.ws, 'send'):
                self.ws.send(message)
            else:
                raise RuntimeError("Client WebSocket not properly initialized")

    def discover_components(self):
        """Discover available components from the remote endpoint"""
        try:
            debug_log("Starting component discovery...", self.debug)
            
            if self.is_server:
                # Server doesn't need to discover its own components
                debug_log("Server skipping component discovery", self.debug)
                self.connection_ready_event.set()
                return True
                
            # Only clients need to discover remote components
            response = self.call_method('system.listComponents')
            debug_log(f"Components discovered: {response}", self.debug)
            
            # Set up the server object with callable methods
            debug_log("Client setting up server methods", self.debug)
            self.server = {}
            for method_name in response:
                debug_log(f"Setting up client method: {method_name}", self.debug)
                self.setup_method(method_name)
            
            self.remotes = response
            debug_log(f"Updated remotes dictionary: {self.remotes}", self.debug)
            self.connection_ready_event.set()
            debug_log(f"connection_ready_event.set()", self.debug)
            return True
                
        except Exception as e:
            debug_log(f"Component discovery failed: {e}", self.debug)
            import traceback
            debug_log(traceback.format_exc(), self.debug)
            return False


    def call_method(self, method: str, params=None):
        """Make an RPC call
        
        Args:
            method: Method name to call
            params: Parameters to pass to method
            
        Returns:
            Result from remote method
        """
        if not self.ws:
            raise RuntimeError("No websocket connection available")
                
        debug_log(f"Calling method: {method} with params: {params}", self.debug)
        # Create request
        request, request_id = self.create_request(method, params)
        debug_log(f"Created request: {json.dumps(request)}", self.debug)
        
        try:
            result = self.send_and_wait(request, request_id)
            debug_log(f"Got result for {method}: {result}", self.debug)
            return result
        except Exception as e:
            debug_log(f"Error in call_method: {e}", self.debug)
            import traceback
            debug_log(traceback.format_exc(), self.debug)
            raise RuntimeError(f"Error when calling remote function : {method}")

    def send_and_wait(self, request, request_id):
        """Send a request and wait for response"""
        try:
            debug_log(f"send_and_wait: Sending request {request_id}", self.debug)
            
            # Send the message depending on client or server mode
            if self.is_client:
                # Client mode - direct websocket send
                if hasattr(self.ws, 'send'):
                    self.ws.send(json.dumps(request))
                else:
                    raise RuntimeError("Client WebSocket not properly initialized")
            else:
                # Server mode - use server's send_message method
                if hasattr(self, 'server') and hasattr(self.server, 'send_message'):
                    self.server.send_message(self.ws, json.dumps(request))
                else:
                    raise RuntimeError("Server not properly initialized for sending")
            
            # Setup for response handling
            if not hasattr(self, 'pending_responses'):
                self.pending_responses = {}
                
            # Wait for response with timeout
            start_time = time.time()
            while time.time() - start_time < self.remote_timeout:
                if request_id in self.pending_responses:
                    response_data = self.pending_responses.pop(request_id)
                    if 'error' in response_data:
                        raise RuntimeError(response_data['error'].get('message', 'Unknown error'))
                    return response_data.get('result')
                time.sleep(0.1)
                
            raise TimeoutError(f"No response received within {self.remote_timeout} seconds")
            
        except Exception as e:
            debug_log(f"send_and_wait: Error for request {request_id}: {str(e)}", self.debug)
            raise RuntimeError(f"RPC call failed: {e}")

    def process_incoming_message(self, message, client=None, server=None):
        """Process incoming messages from either client or server
        
        Args:
            message: The message to process
            client: Optional client connection info (for server-side)
            server: Optional server instance (for server-side)
        """
        try:
            # Store client/server refs if provided (server-side)
            if client and server:
                self.ws = client
                self.server = server
            
            # Parse message into JSON if needed
            if isinstance(message, bytes):
                message = message.decode('utf-8')
                
            # Convert to dict if string
            if isinstance(message, str):
                try:
                    if message.startswith('{') or message.startswith('['):
                        msg_data = json.loads(message)
                    else:
                        msg_data = message
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    return {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                        "id": None
                    }
            else:
                msg_data = message
                
            # Handle responses to our requests
            if isinstance(msg_data, dict) and ('result' in msg_data or 'error' in msg_data) and 'id' in msg_data:
                msg_id = msg_data.get('id')
                if hasattr(self, 'pending_responses'):
                    self.pending_responses[msg_id] = msg_data
                return None
                
            if not isinstance(msg_data, dict):
                print("Invalid message format - not an object")
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Invalid message format - not a JSON object"},
                    "id": None
                }
                
            # Process message and get response
            response = self.handle_message(msg_data)
            
            # For responses to our requests, don't send anything back
            if 'result' in msg_data or 'error' in msg_data:
                return None
                
            if response:  # Only send response if one was generated
                
                # Convert response to JSON string if needed
                if isinstance(response, dict):
                    response = json.dumps(response)
                    
                # Send via appropriate mechanism
                if server and client:
                    server.send_message(client, response)
                else:
                    return response
                    
        except json.JSONDecodeError as e:
            debug_log(f"Invalid JSON received: {e}", self.debug)
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": f"Invalid JSON: {str(e)}"},
                "id": None
            }
        except Exception as e:
            debug_log(f"Error processing message: {e}", self.debug)
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": None
            }

    def __getitem__(self, class_name: str):
        """Allow dictionary-style access for RPC classes"""
        return type('RPCClass', (), {
            '__getattr__': lambda _, method: lambda *args: self.call_method(
                f"{class_name}.{method}", args
            )
        })()
    def setup_method(self, method_name):
        """Set up a callable method proxy for the remote method"""
        debug_log(f"Setting up method proxy for: {method_name}", self.debug)
        
        def method_proxy(*args):
            debug_log(f"Calling remote method: {method_name} with args: {args}", self.debug)
            try:
                # Format args the way JavaScript client expects
                payload = {'args': args}
                debug_log(f"Sending payload: {payload}", self.debug)
                result = self.call_method(method_name, payload)
                debug_log(f"Result from {method_name}: {result}", self.debug)
                return result
            except Exception as e:
                debug_log(f"Error calling {method_name}: {e}", self.debug)
                import traceback
                debug_log(f"Traceback: {traceback.format_exc()}", self.debug)
                console_msg = f"Error when calling remote function : {method_name}"
                print(console_msg)
                raise RuntimeError(console_msg)
        
        # Store the method in the server dictionary
        self.server[method_name] = method_proxy
