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
import threading
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

    def setup_ssl(self):
        """Setup SSL context for client"""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations('./cert/server.crt')
        return ssl_context
        
    def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.ws = create_connection(
                self.uri,
                sslopt={"context": self.ssl_context} if self.ssl_context else None
            )
            
            # Start message handler thread
            self.message_thread = threading.Thread(
                target=self.process_incoming_messages,
                args=(self.ws,),
                daemon=True
            )
            self.message_thread.start()
            
            # Give message handler a moment to start
            time.sleep(0.1)
            
            # Discover server components
            success = self.discover_components()
            if success:
                # Wait for both sides to be ready
                self.wait_connection_ready()
                debug_log(f"Connected to server at {self.uri}", self.debug)
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
            if hasattr(self, 'message_thread'):
                self.message_thread.join(timeout=1.0)

    def process_incoming_messages(self, websocket):
        """Process incoming messages from the websocket"""
        try:
            debug_log("Client message processing thread started", self.debug)
            while True:
                try:
                    debug_log("Client waiting for next message...", self.debug)
                    message = websocket.recv()
                    debug_log(f"Client received raw message type: {type(message)}", self.debug)
                    
                    if isinstance(message, bytes):
                        message = message.decode('utf-8')
                        debug_log(f"Client decoded message from bytes: {message}", self.debug)
                    else:
                        debug_log(f"Client received string message: {message}", self.debug)
                    
                    # Parse message if needed
                    if isinstance(message, str):
                        message = json.loads(message)
                    
                    # Process the message
                    response = self.handle_message(message)
                    
                    # If we got a response and it's a request (not a response to our request)
                    # send it back through the websocket
                    if response and 'method' in message:
                        debug_log(f"Client sending response: {json.dumps(response)}", self.debug)
                        websocket.send(json.dumps(response))
                        
                except Exception as e:
                    debug_log(f"Error in message processing loop: {e}", self.debug)
                    if not websocket.connected:
                        debug_log("WebSocket disconnected, exiting loop", self.debug)
                        break
                    
        except Exception as e:
            debug_log(f"Fatal error in message processing thread: {e}", self.debug)

