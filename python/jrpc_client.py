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

    ws = None
    
    def __init__(self, host='0.0.0.0', port=9000, use_ssl=False, debug=False):
        """Initialize common RPC settings
        
        Args:
            host: Host address to use
            port: Port number to use
            use_ssl: Whether to use SSL/WSS
            debug: Enable debug logging
        """
        super().__init__(host=host, port=port, use_ssl=use_ssl, debug=debug)
        self.pending_requests = {}

    def setup_ssl(self):
        """Setup SSL context for client"""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations('./cert/server.crt')
        return ssl_context
        
    def is_server(self):
        """This is not a server instance"""
        return False
        
    def is_client(self):
        """This is a client instance"""
        return True

    def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.ws = create_connection(
                self.uri,
                sslopt={"context": self.ssl_context} if self.ssl_context else None
            )
            
            # Initial connection setup
            debug_log("Client connected, starting message processing", self.debug)
            
            # Start message processing thread
            import threading
            self.message_thread = threading.Thread(
                target=self.process_incoming_messages,
                args=(self.ws,),
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
            if hasattr(self, 'message_thread'):
                self.ws.close()
            return False

    def close(self):
        """Close the connection"""
        if self.ws:
            self.ws.close()
            self.ws = None
            self.pending_requests.clear()

    def process_incoming_messages(self, websocket):
        """Process incoming messages from the websocket"""
        try:
            debug_log("Client message processing thread started", self.debug)
            while True:
                try:
                    message = websocket.recv()
                    debug_log(f"Client received raw message: {message}", self.debug)
                    
                    # Try to parse JSON
                    try:
                        msg_data = json.loads(message)
                        debug_log(f"Client parsed message: {json.dumps(msg_data, indent=2)}", self.debug)
                    except json.JSONDecodeError:
                        debug_log(f"Client received non-JSON message: {message}", self.debug)
                    
                    # Process using common handler
                    response = self.process_incoming_message(message)
                    
                    # Send response if needed
                    if response and isinstance(message, dict) and 'method' in message:
                        debug_log(f"Client sending response: {response}", self.debug)
                        websocket.send(response)
                        
                except Exception as e:
                    debug_log(f"Error in message processing loop: {e}", self.debug)
                    if not websocket.connected:
                        debug_log("WebSocket disconnected, exiting loop", self.debug)
                        break
                    
        except Exception as e:
            debug_log(f"Fatal error in message processing thread: {e}", self.debug)

