#!/usr/bin/env python3
"""
JSON-RPC 2.0 Client implementation with WebSocket support and class-based RPC
"""
import asyncio
import json
import websockets
from jrpc_common import JRPCCommon

class JRPCClient(JRPCCommon):
    def __init__(self, host="localhost", port=8080):
        """Initialize RPC client with host and port"""
        super().__init__()
        self.uri = f'ws://{host}:{port}'
        self.websocket = None
        self._handler_task = None
        self._response_queues = {}  # Map request IDs to response queues
        self._connection_lock = asyncio.Lock()
        self._connected = asyncio.Event()
        
    async def connect(self):
        """Connect to the WebSocket server"""
        async with self._connection_lock:
            if not self.websocket or self.websocket.closed:
                self.websocket = await websockets.connect(
                    self.uri, 
                    subprotocols=['jsonrpc']
                )
                # Start message handler if not running
                if not self._handler_task or self._handler_task.done():
                    self._handler_task = asyncio.create_task(self._handle_messages())
                # Get initial component list
                await self.call_remote(self.websocket, "system.listComponents")
                self._connected.set()
    
    async def _handle_messages(self):
        """Handle incoming messages from server"""
        print("DEBUG: Starting message handler loop")
        while True:
            try:
                if not self.websocket or self.websocket.closed:
                    print("DEBUG: Websocket closed or None, waiting for reconnect")
                    await asyncio.sleep(0.1)  # Wait before checking again
                    continue

                try:
                    message = await self.websocket.recv()
                    print(f"DEBUG: Received message: {message[:100]}...")
                    
                    parsed = json.loads(message)
                    
                    # Handle method calls from server
                    if 'method' in parsed:
                        # Handle method calls and get response
                        response = await self.handle_message(self.websocket, message)
                        # Only send response if there was an ID
                        if 'id' in parsed and response:
                            await self.websocket.send(response)
                        continue
                        
                    # Handle responses to our requests
                    if 'id' in parsed:
                        request_id = parsed['id']
                        if request_id in self._response_queues:
                            print(f"DEBUG: Routing response for request {request_id}")
                            self._response_queues[request_id].set_result(parsed)
                            del self._response_queues[request_id]  # Clean up immediately
                            
                except json.JSONDecodeError:
                    print(f"DEBUG: Invalid JSON received: {message}")
                    
            except (websockets.exceptions.ConnectionClosed, RuntimeError) as e:
                print(f"DEBUG: Connection error: {e}")
                self.websocket = None
                # Fail any pending requests
                for request_id, future in self._response_queues.items():
                    if not future.done():
                        future.set_exception(e)
                # Don't exit loop - allow reconnection
            except Exception as e:
                print(f"DEBUG: Error in message handler: {e}")
                print(f"DEBUG: Error type: {type(e)}")
                import traceback
                print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
                # Make sure to fail any pending requests
                for future in self._response_queues.values():
                    if not future.done():
                        future.set_exception(e)
                await asyncio.sleep(0.1)  # Wait before retrying

    async def call_method(self, method: str, params=None):
        """Make an RPC call to the server"""
        print(f"DEBUG: Calling method {method} with params {params}")
        
        # Ensure connection is active
        retries = 3
        while retries > 0:
            try:
                if not self.websocket or self.websocket.closed:
                    print("DEBUG: Websocket not connected, connecting...")
                    await self.connect()
                    await self._connected.wait()
                
                if self.websocket and not self.websocket.closed:
                    break
                    
            except Exception as e:
                print(f"DEBUG: Connection attempt failed: {e}")
                retries -= 1
                if retries > 0:
                    await asyncio.sleep(1)
                self._connected.clear()
                
        if not self.websocket or self.websocket.closed:
            raise Exception("Failed to establish websocket connection")
            
        try:
            # Create response future for this request
            request_id = id(method)
            response_future = asyncio.Future()
            self._response_queues[request_id] = response_future
            
            print(f"DEBUG: Making remote call with request ID {request_id}")
            await self.websocket.send(json.dumps({
                'jsonrpc': '2.0',
                'method': method,
                'params': {'args': params} if params else [],
                'id': request_id
            }))
            
            # Wait for response with timeout
            print(f"DEBUG: Waiting for response to request {request_id}")
            try:
                response = await asyncio.wait_for(response_future, timeout=self.remote_timeout)
            except asyncio.TimeoutError:
                raise Exception(f"Request timed out after {self.remote_timeout} seconds")
            print(f"DEBUG: Got response for request {request_id}")
            
            if 'error' in response:
                raise Exception(f"RPC Error: {response['error']}")
                
            return response['result']
            
        except Exception as e:
            print(f"DEBUG: Error in call_method: {e}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
            raise e
        finally:
            # Clean up response queue
            if request_id in self._response_queues:
                del self._response_queues[request_id]

    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        if self._handler_task:
            self._handler_task.cancel()
            try:
                await self._handler_task
            except asyncio.CancelledError:
                pass
            self._handler_task = None

    def __getitem__(self, class_name: str):
        """Allow dictionary-style access for RPC classes e.g. client['Calculator']"""
        return type('RPCClass', (), {
            '__getattr__': lambda _, method: lambda *args: self.call_method(f"{class_name}.{method}", args)
        })()
