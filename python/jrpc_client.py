#!/usr/bin/env python3
"""
JSON-RPC 2.0 Client implementation with WebSocket support and class-based RPC
"""
import json
import asyncio
import websockets
from typing import Any


class JRPCClient:
    def __init__(self, host="localhost", port=8080):
        """Initialize RPC client with host and port"""
        self.uri = f'ws://{host}:{port}'
        self.websocket = None
        self.request_id = 0
        
    async def connect(self):
        """Connect to the WebSocket server"""
        if not self.websocket:
            self.websocket = await websockets.connect(self.uri, subprotocols=['jsonrpc'])
            await self.call_method("system.listComponents")
    
    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
    async def call_method(self, method: str, params=None):
        """Make an RPC call to the server"""
        if not self.websocket:
            await self.connect()
            
        self.request_id += 1
        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': {'args': params} if params else [],
            'id': self.request_id
        }
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        
        parsed = json.loads(response)
        if 'error' in parsed:
            raise Exception(f"RPC Error: {parsed['error']}")
        return parsed['result']

    def __getitem__(self, class_name: str):
        """Allow dictionary-style access for RPC classes e.g. client['Calculator']"""
        return type('RPCClass', (), {
            '__getattr__': lambda _, method: lambda *args: self.call_method(f"{class_name}.{method}", args)
        })()
