#!/usr/bin/env python3
"""
JSON-RPC 2.0 Server implementation with WebSocket support and class-based RPC
"""
import json
import websockets
from jrpc_common import JRPCCommon

class JRPCServer(JRPCCommon):
    def __init__(self, host='localhost', port=8080):
        """Initialize WebSocket RPC server"""
        super().__init__()
        self.host = host
        self.port = port

    async def _handle_ws_connection(self, websocket):
        """Handle WebSocket connection"""
        remote_id = id(websocket)
        print(f"DEBUG: New connection from {websocket.remote_address}, ID: {remote_id}")
        self.remotes[remote_id] = websocket
        
        try:
            async for message in websocket:
                print(f"DEBUG: Received message from {remote_id}: {message[:100]}...")
                try:
                    parsed = json.loads(message)
                    # Only handle messages with method calls
                    if 'method' in parsed:
                        response = await self.handle_message(websocket, message)
                        if response:
                            print(f"DEBUG: Sending response to {remote_id}: {response[:100]}...")
                            await websocket.send(response)
                except json.JSONDecodeError:
                    print(f"DEBUG: Invalid JSON received: {message}")
        except websockets.exceptions.ConnectionClosed:
            print(f"DEBUG: Connection closed for {remote_id}")
            del self.remotes[remote_id]
        except Exception as e:
            print(f"DEBUG: Error handling connection {remote_id}: {e}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback:\n{traceback.format_exc()}")

    async def start(self):
        """Start the WebSocket server"""
        self.ws_server = await websockets.serve(
            self._handle_ws_connection,
            self.host,
            self.port,
            subprotocols=['jsonrpc']
        )
