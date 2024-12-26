#!/usr/bin/env python3
"""
JSON-RPC 2.0 Client implementation using jsonrpclib-pelix
"""
from jsonrpclib import Server
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jrpc_common import JRPCCommon

class JRPCClient(JRPCCommon):
    def __init__(self, host="localhost", port=8080, client_port=8081, debug=False):
        """Initialize RPC client with bidirectional capabilities
        
        Args:
            host: Server host to connect to
            port: Server port to connect to
            client_port: Port to listen on for server callbacks
        """
        super().__init__(debug)
        self.host = host
        self.server_port = port
        self.client_port = client_port
        self.uri = f'http://{host}:{port}'
        self.server = Server(self.uri)
        
    def connect(self):
        """Start client server and connect to remote server"""
        # Start our server for callbacks
        self.server = SimpleJSONRPCServer((self.host, self.client_port))
        
        # Register all instance methods
        for class_name, instance in self.instances.items():
            for method_name in dir(instance):
                method = getattr(instance, method_name)
                if callable(method) and not method_name.startswith('_'):
                    self.server.register_function(
                        method,
                        name=f"{class_name}.{method_name}"
                    )
        
        # Start server in background thread
        import threading
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Connect to remote server
        try:
            self.client = Server(self.uri)
            components = self.client.system.listComponents()
            self.logger.debug(f"Connected to server at {self.uri}")
            self.logger.debug(f"Available components: {components}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    

    def call_method(self, method: str, params=None):
        """Make an RPC call to the server"""
        try:
            if params is None:
                params = []
            self.logger.debug(f"Calling remote method: {method} with params: {params}")
            method_call = getattr(self.client, method)
            result = method_call(*params)
            self.logger.debug(f"Method {method} returned: {result}")
            return result
        except Exception as e:
            self.logger.error(f"RPC call failed: {e}")
            raise

    def close(self):
        """Close all connections"""
        if self.server:
            self.server.shutdown()
            self.server = None
        self.client = None

    def __getitem__(self, class_name: str):
        """Allow dictionary-style access for RPC classes e.g. client['Calculator']"""
        return type('RPCClass', (), {
            '__getattr__': lambda _, method: lambda *args: self.call_method(
                f"{class_name}.{method}", args
            )
        })()
