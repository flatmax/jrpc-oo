"""
JSON-RPC Server implementation over WebSockets.
"""

import json
import ssl
import threading
from websocket_server import WebsocketServer
from .JRPCCommon import JRPCCommon

class JRPCServer(JRPCCommon):
    """
    Server class for JSON-RPC over WebSockets.
    Similar to the JavaScript JRPCServer.
    """
    
    def __init__(self, port=9000, remote_timeout=60, ssl=True):
        """
        Initialize the server.
        
        Args:
            port: The port number to use for socket binding
            remote_timeout: The maximum timeout of connection
            ssl: Set False for regular connection, True for secure connection
        """
        super().__init__()
        self.remote_timeout = remote_timeout
        
        # Setup the WebSocket server
        if ssl:
            # Create SSL context
            ssl_context = {
                'certfile': './cert/server.crt',
                'keyfile': './cert/server.key'
            }
            self.wss = WebsocketServer(port=port, host='0.0.0.0', 
                                     loglevel=0, ssl_context=ssl_context)
        else:
            self.wss = WebsocketServer(port=port, host='0.0.0.0', loglevel=0)
        
        # Set up event handlers
        self.wss.set_fn_new_client(self.on_new_client)
        self.wss.set_fn_client_left(self.on_client_left)
        self.wss.set_fn_message_received(self.on_message_received)
    
    def start(self):
        """Start the server."""
        # Run the server in a background thread
        server_thread = threading.Thread(target=self.wss.run_forever)
        server_thread.daemon = True
        server_thread.start()
        return server_thread
    
    def on_new_client(self, client, server):
        """
        Handle new client connection.
        
        Args:
            client: Client information
            server: Server object
        """
        remote = self.new_remote()
        remote['client'] = client
        remote['rpcs'] = {}
        
        # Setup the WebSocket for this remote
        self.setup_remote(remote, client)
        
        self.remote_is_up()
    
    def on_client_left(self, client, server):
        """
        Handle client disconnection.
        
        Args:
            client: Client information
            server: Server object
        """
        # Find the remote for this client
        uuid_to_remove = None
        for uuid, remote in self.remotes.items():
            if remote.get('client') == client:
                uuid_to_remove = uuid
                break
        
        if uuid_to_remove:
            self.rm_remote(None, uuid_to_remove)
    
    def on_message_received(self, client, server, message):
        """
        Handle message from client.
        
        Args:
            client: Client information
            server: Server object
            message: The message received
        """
        # Find the remote for this client
        remote = None
        for r in self.remotes.values():
            if r.get('client') == client:
                remote = r
                break
        
        if not remote:
            print("Message received from unknown client")
            return
        
        try:
            # Parse the message
            data = json.loads(message)
            
            # Handle the message based on JSON-RPC format
            if 'method' in data:
                # Handle method call
                method_name = data['method']
                params = data.get('params', {})
                request_id = data.get('id')
                
                # Handle system.listComponents request
                if method_name == 'system.listComponents':
                    components = {}
                    for cls in self.classes:
                        for name in cls.keys():
                            components[name] = name
                    
                    response = {
                        'jsonrpc': '2.0',
                        'result': components,
                        'id': request_id
                    }
                    self.wss.send_message(client, json.dumps(response))
                    return
                
                # Find method in exposed classes
                method_found = False
                result = None
                
                for cls in self.classes:
                    if method_name in cls:
                        try:
                            # Extract args if available
                            method_found = True
                            result = cls[method_name](params)
                            break
                        except Exception as e:
                            print(f"Error executing {method_name}: {e}")
                            if request_id is not None:
                                error_response = {
                                    'jsonrpc': '2.0',
                                    'error': {
                                        'code': -32000,
                                        'message': str(e)
                                    },
                                    'id': request_id
                                }
                                self.wss.send_message(client, json.dumps(error_response))
                            return
                
                # Send response if request had an ID
                if request_id is not None:
                    if method_found:
                        response = {
                            'jsonrpc': '2.0',
                            'result': result,
                            'id': request_id
                        }
                    else:
                        response = {
                            'jsonrpc': '2.0',
                            'error': {
                                'code': -32601,
                                'message': f'Method not found: {method_name}'
                            },
                            'id': request_id
                        }
                    self.wss.send_message(client, json.dumps(response))
            
            # Handle response to a previous request
            elif ('result' in data or 'error' in data) and 'id' in data:
                # Process response - this would be for client->server calls
                pass
            
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
    
    def setup_remote(self, remote, ws):
        """
        Setup a remote connection.
        
        Args:
            remote: The remote to setup
            ws: WebSocket connection
        """
        # Expose our classes to the remote
        if self.classes:
            for cls_obj in self.classes:
                for method_name, method in cls_obj.items():
                    if 'methods' not in remote:
                        remote['methods'] = {}
                    remote['methods'][method_name] = method
        
        # Request the remote's exposed methods
        request = {
            'jsonrpc': '2.0',
            'method': 'system.listComponents',
            'params': [],
            'id': 1
        }
        self.wss.send_message(ws, json.dumps(request))
