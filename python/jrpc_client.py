#!/usr/bin/env python3
"""
JSON-RPC 2.0 Client implementation using jsonrpclib-pelix
"""
from jsonrpclib import Server
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jrpc_common import JRPCCommon
import time

class JRPCClient(JRPCCommon):
    def __init__(self, host="localhost", port=8080, debug=False):
        """Initialize RPC client with bidirectional capabilities
        
        Args:
            host: Server host to connect to
            port: Server port to connect to
        """
        super().__init__(debug)
        self.host = host
        self.server_port = port
        self.uri = f'http://{host}:{port}'
        self.server = Server(self.uri)
        
    def start_server(self):
        """Start the client's server for callbacks"""
        try:
            # Start our server for callbacks
            self.server = SimpleJSONRPCServer((self.host, 0))  # Let OS assign a port
            self.client_port = self.server.server_address[1]  # Get the assigned port
            
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
            return True
        except Exception as e:
            print(f"Failed to start client server: {e}")
            return False

    def connect_to_server(self):
        """Connect to the remote server"""
        try:
            self.client = Server(self.uri)
            components = self.client.system.listComponents()
            print(f"Connected to server at {self.uri}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    

    def call_method(self, method: str, params=None):
        """Make an RPC call to the server"""
        try:
            if params is None:
                params = []
            method_call = getattr(self.client, method)
            result = method_call(*params)
            return result
        except Exception as e:
            print(f"RPC call failed: {e}")
            raise

    def close(self):
        """Close all connections"""
        if hasattr(self, 'server') and self.server:
            try:
                self.server.server_close()
            except:
                pass
            self.server = None
        self.client = None

    def __getitem__(self, class_name: str):
        """Allow dictionary-style access for RPC classes e.g. client['Calculator']"""
        return type('RPCClass', (), {
            '__getattr__': lambda _, method: lambda *args: self.call_method(
                f"{class_name}.{method}", args
            )
        })()
