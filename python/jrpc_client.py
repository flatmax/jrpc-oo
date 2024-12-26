#!/usr/bin/env python3
"""
JSON-RPC 2.0 Client implementation with WebSocket support
"""
import asyncio
import websockets
import json
import ssl
from jrpc_common import JRPCCommon
from debug_utils import debug_log

class JRPCClient(JRPCCommon):
    def __init__(self, uri="ws://localhost:9000", port=None, use_ssl=False, debug=False):
        """Initialize WebSocket RPC client
        
        Args:
            uri: WebSocket URI to connect to
            port: Optional port number (overrides port in URI if specified)
            use_ssl: Whether to use SSL/WSS
            debug: Enable debug logging
        """
        super().__init__(debug)
        # Handle port parameter
        if port is not None:
            # Parse URI and replace port
            import urllib.parse
            parsed = urllib.parse.urlparse(uri)
            netloc = parsed.netloc.split(':')[0]  # Get hostname without port
            self.uri = f"{parsed.scheme}://{netloc}:{port}"
        else:
            self.uri = uri
        self.ws = None
        self.ssl_context = None
        if use_ssl:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.ssl_context.load_verify_locations('./cert/server.crt')
            
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.ws = await websockets.connect(
                self.uri,
                ssl=self.ssl_context
            )
            # Start message handler
            asyncio.create_task(self._message_handler())
            
            # Get available components
            response = await self.call_method('system.listComponents')
            debug_log(f"Connected to server at {self.uri}", self.debug)
            debug_log(f"Available components: {response}", self.debug)
            return True
            
        except Exception as e:
            debug_log(f"Connection failed: {e}", self.debug)
            return False

    async def _message_handler(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.ws:
                debug_log(f"Received: {message}", self.debug)
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            debug_log("Connection closed", self.debug)
        except Exception as e:
            print(f"Message handler error: {e}")

    async def call_method(self, method: str, params=None):
        """Make an RPC call to the server
        
        Args:
            method: Method name to call
            params: Parameters to pass to method
            
        Returns:
            Result from remote method
        """
        if not self.ws:
            raise RuntimeError("Not connected to server")
            
        # Create request
        request, request_id = self.create_request(method, params)
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send request
            await self.ws.send(json.dumps(request))
            
            # Wait for response with timeout
            response = await asyncio.wait_for(
                future,
                timeout=self.remote_timeout
            )
            return response
            
        except asyncio.TimeoutError:
            self.pending_requests.pop(request_id, None)
            raise TimeoutError(f"Request {method} timed out")
        except Exception as e:
            self.pending_requests.pop(request_id, None)
            raise RuntimeError(f"RPC call failed: {e}")

    async def close(self):
        """Close the connection"""
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.pending_requests.clear()
            
    async def connect_to_server(self):
        """Connect to the main server"""
        return await self.connect()
        
    async def start_server(self):
        """Start the client's server for receiving callbacks"""
        # For now just connect to receive callbacks
        return await self.connect()

    def __getitem__(self, class_name: str):
        """Allow dictionary-style access for RPC classes"""
        return type('RPCClass', (), {
            '__getattr__': lambda _, method: lambda *args: self.call_method(
                f"{class_name}.{method}", args
            )
        })()
