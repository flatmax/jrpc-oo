#!/usr/bin/env python3
"""
JSON-RPC 2.0 Server implementation using jsonrpclib-pelix
"""
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib import Server
import logging
from jrpc_common import JRPCCommon

class JRPCServer(JRPCCommon):
    def __init__(self, host='localhost', port=8080, client_port=8081, debug=False):
        """Initialize JSON-RPC server with bidirectional capabilities
        
        Args:
            host: Host to bind to
            port: Port for server to listen on
            client_port: Port to connect back to clients
        """
        super().__init__(debug)
        self.host = host
        self.port = port
        self.client_port = client_port

    def start(self):
        """Start the JSON-RPC server and connect back to client"""
        # Start server
        self.server = SimpleJSONRPCServer((self.host, self.port))
        self.logger.debug(f"Server started on {self.host}:{self.port}")
        
        # Create client connection back to client
        try:
            self.client = Server(f'http://{self.host}:{self.client_port}')
            self.logger.info(f"Connected back to client on port {self.client_port}")
        except Exception as e:
            self.logger.error(f"Failed to connect back to client: {e}")
            self.client = None
        
        # Register all instance methods
        for class_name, instance in self.instances.items():
            for method_name in dir(instance):
                method = getattr(instance, method_name)
                if callable(method) and not method_name.startswith('_'):
                    self.logger.debug(f"Registering method: {class_name}.{method_name}")
                    self.server.register_function(
                        method,
                        name=f"{class_name}.{method_name}"
                    )

        # Register system methods
        self.server.register_function(self.list_components, 'system.listComponents')
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.shutdown()
