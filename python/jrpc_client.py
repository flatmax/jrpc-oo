"""
JSON-RPC 2.0 Client implementation with WebSocket support.

This module provides a WebSocket-based JSON-RPC 2.0 client implementation that can:
- Connect to a JSON-RPC server over WebSocket
- Make remote procedure calls
- Handle responses and errors
- Support SSL/TLS encryption
- Provide thread-safe interface
"""
import json
import time
from websocket import WebSocket, create_connection
import ssl
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python.jrpc_common import JRPCCommon
from python.debug_utils import debug_log

class JRPCClient(JRPCCommon):
    # Override parent class variables
    is_client = True
    
    def __init__(self, host='localhost', port=9000, use_ssl=False, debug=False):
        super().__init__(host=host, port=port, use_ssl=use_ssl, debug=debug)
        self.ws = None
        self.pending_responses = {}

    def setup_ssl(self):
        """Setup SSL context for client"""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations('./cert/server.crt')
        return ssl_context

    def connect(self):
        """Connect to the WebSocket server"""
        try:
            print(f"Connecting to {self.uri}")
            self.ws = create_connection(
                self.uri,
                sslopt={"context": self.ssl_context} if self.use_ssl else None
            )
            
            # Initial connection setup
            debug_log("Client connected, starting message processing", self.debug)
            
            # Start message processing thread
            import threading
            self.message_thread = threading.Thread(
                target=self.receive_messages,
                daemon=True
            )
            self.message_thread.start()
            
            # Do initial component discovery
            success = self.discover_components()
            if not success:
                debug_log("Component discovery failed", self.debug)
                return False
                
            debug_log(f"Connected to server at {self.uri} and discovered components", self.debug)
            return True
            
        except Exception as e:
            debug_log(f"Connection failed: {e}", self.debug)
            if hasattr(self, 'message_thread') and hasattr(self, 'ws') and self.ws:
                self.ws.close()
            return False
            
    def receive_messages(self):
        """Continuously receive messages from the server"""
        try:
            print("Starting client message receiver thread")
            while True:
                try:
                    if hasattr(self, 'ws') and self.ws:
                        message = self.ws.recv()
                        if message:
                            self.process_incoming_message(message)
                    else:
                        # Connection closed
                        print("WebSocket connection closed")
                        break
                except Exception as e:
                    print(f"Error receiving message: {str(e)}")
                    if not hasattr(self, 'ws') or not self.ws:
                        break
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Fatal error in receive_messages: {e}")

    def close(self):
        """Close the connection"""
        if hasattr(self, 'ws') and self.ws:
            self.ws.close()
            self.ws = None
        if hasattr(self, 'pending_responses'):
            self.pending_responses.clear()

