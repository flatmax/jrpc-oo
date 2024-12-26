#!/usr/bin/env python3
"""
JSON-RPC 2.0 Server implementation using jsonrpclib-pelix
"""
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib import Server
from jrpc_common import JRPCCommon

class JRPCServer(JRPCCommon):
    def __init__(self, host='localhost', port=8080, debug=False):
        """Initialize JSON-RPC server
        
        Args:
            host: Host to bind to
            port: Port for server to listen on
        """
        super().__init__(debug)
        self.host = host
        self.port = port

    def start(self):
        """Start the JSON-RPC server without connecting to client"""
        self.server = SimpleJSONRPCServer((self.host, self.port))
        print(f"Server started on {self.host}:{self.port}")
        
        # Register all instance methods
        for class_name, instance in self.instances.items():
            for method_name in dir(instance):
                method = getattr(instance, method_name)
                if callable(method) and not method_name.startswith('_'):
                    self.server.register_function(
                        method,
                        name=f"{class_name}.{method_name}"
                    )

        # Register system methods
        self.server.register_function(self.list_components, 'system.listComponents')
        
    def serve_forever(self):
        """Start serving requests forever"""
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.shutdown()
