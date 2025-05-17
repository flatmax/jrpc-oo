"""
Common functionality for JSON-RPC over WebSockets.
"""

import uuid
import json
import threading
from jsonrpclib.jsonrpc import ServerProxy
from .ExposeClass import ExposeClass

class JRPCCommon:
    """
    Base class for both JRPC client and server implementations.
    Handles remote connections and method exposure.
    """
    
    def __init__(self):
        """Initialize the common functionality."""
        self.remotes = {}  # Dictionary of connected remotes
        self.server = {}   # Backwards compatibility
        self.call = {}     # Methods to call all remotes
        self.classes = []  # List of exposed class objects
        self.remote_timeout = 60  # Default timeout
        self.ws_thread = None  # Thread for WebSocket connection
    
    def new_remote(self):
        """
        Create a new remote connection.
        
        Returns:
            The new remote object
        """
        remote = {}
        remote["uuid"] = str(uuid.uuid4())
        remote["rpcs"] = {}  # Initialize rpcs dictionary for all remotes
        if self.remotes is None:
            self.remotes = {}
        self.remotes[remote["uuid"]] = remote
        return remote
    
    def create_remote(self, ws):
        """
        Create a remote connection for the given websocket.
        
        Args:
            ws: The websocket connection
        
        Returns:
            The newly created remote
        """
        remote = self.new_remote()
        self.remote_is_up()
        
        # Different handling for client/server will be implemented in subclasses
        return remote
        
    def remote_is_up(self):
        """Called when a remote connection is established."""
        print("JRPCCommon::remoteIsUp")
    
    def rm_remote(self, event, uuid):
        """
        Remove a remote connection.
        
        Args:
            event: The event that triggered the removal
            uuid: The UUID of the remote to remove
        """
        # Remove methods from the server (backwards compatibility)
        if self.server and uuid in self.remotes:
            if 'rpcs' in self.remotes[uuid]:
                for fn in self.remotes[uuid]['rpcs']:
                    if fn in self.server:
                        del self.server[fn]
        
        # Remove the remote
        if uuid in self.remotes:
            del self.remotes[uuid]
        
        # Rebuild the call dictionary if remotes remain
        if self.call and self.remotes:
            remaining_fns = []
            for remote in self.remotes.values():
                if 'rpcs' in remote:
                    remaining_fns.extend(remote['rpcs'].keys())
            
            # Remove functions that no longer exist in any remote
            if self.call:
                existing_fns = list(self.call.keys())
                for fn_name in existing_fns:
                    if fn_name not in remaining_fns:
                        del self.call[fn_name]
        else:
            self.call = {}  # Reset call object
        
        self.remote_disconnected(uuid)
    
    def remote_disconnected(self, uuid):
        """
        Notify that a remote has been disconnected.
        
        Args:
            uuid: The UUID of the removed remote
        """
        print(f"JPRCCommon::remoteDisconnected {uuid}")
    
    def setup_remote(self, remote, ws):
        """
        Expose classes and handle setting up remote functions.
        
        Args:
            remote: The remote to setup
            ws: The websocket for transmission
        """
        # Expose registered classes
        if self.classes:
            for cls in self.classes:
                for method_name, method in cls.items():
                    if 'methods' not in remote:
                        remote['methods'] = {}
                    remote['methods'][method_name] = method
                
        # Call system.listComponents to get available methods
        self.request_remote_components(remote, ws)
    
    def transmit(self, msg, next_func):
        """
        Transmit a message to the remote.
        
        Args:
            msg: The message to send
            next_func: Callback function
        """
        try:
            self.send(msg)
            return next_func(False)
        except Exception as e:
            print(e)
            return next_func(True)
    
    def setup_fns(self, fn_names, remote):
        """
        Setup functions for calling on the remote.
        
        Args:
            fn_names: List of function names
            remote: The remote object
        """
        for fn_name in fn_names:
            # Initialize the remote's rpcs dictionary if needed
            if 'rpcs' not in remote:
                remote['rpcs'] = {}
            
            # Create method in the remote's rpcs
            def create_method(name):
                def method(*args):
                    # Return a promise that resolves with the result
                    return remote['client'].call(name, {'args': list(args)})
                return method
            
            remote['rpcs'][fn_name] = create_method(fn_name)
            
            # Create method in the global call dictionary (to call all remotes)
            if fn_name not in self.call:
                def create_call_all_method(name):
                    def call_all(*args):
                        promises = []
                        rems = []
                        
                        for remote_id, remote_obj in self.remotes.items():
                            if name in remote_obj.get('rpcs', {}):
                                rems.append(remote_id)
                                promises.append(remote_obj['rpcs'][name](*args))
                        
                        # Gather all results
                        results = {}
                        for i, promise in enumerate(promises):
                            try:
                                results[rems[i]] = promise
                            except Exception as e:
                                results[rems[i]] = {'error': str(e)}
                                
                        return results
                    return call_all
                
                self.call[fn_name] = create_call_all_method(fn_name)
            
            # For backwards compatibility - to be removed in future
            if self.server is None:
                self.server = {}
                
            if fn_name not in self.server:
                # First time this function is seen
                self.server[fn_name] = remote['rpcs'][fn_name]
            else:
                # Function already exists in another remote
                def error_method(*args):
                    raise Exception(f"More than one remote has this RPC, not sure who to talk to: {fn_name}")
                self.server[fn_name] = error_method
        
        self.setup_done()
    
    def setup_done(self):
        """Called when setup is complete."""
        pass
        
    def handle_message(self, remote, message):
        """
        Common method to handle JSON-RPC messages.
        
        Args:
            remote: The remote connection object
            message: The JSON-RPC message received
        
        Returns:
            Tuple of (response, is_notification) where:
                - response is the JSON-RPC response object or None
                - is_notification is True if the message was a notification (no id)
        """
        try:
            # Parse the message
            data = json.loads(message)
            
            # Handle the message based on JSON-RPC format
            if 'method' in data:
                # Handle method call
                method_name = data['method']
                params = data.get('params', {})
                request_id = data.get('id')
                
                # Handle system.listComponents request separately
                if method_name == 'system.listComponents':
                    return self.handle_system_list_components(remote, request_id), False
                
                # Find method in exposed classes
                method_found = False
                result = None
                error = None
                
                for cls in self.classes:
                    if method_name in cls:
                        try:
                            method_found = True
                            result = cls[method_name](params)
                            break
                        except Exception as e:
                            error = str(e)
                            print(f"Error executing {method_name}: {e}")
                
                # Create response if request had an ID
                if request_id is not None:
                    if method_found and error is None:
                        return {
                            'jsonrpc': '2.0',
                            'result': result,
                            'id': request_id
                        }, False
                    else:
                        return {
                            'jsonrpc': '2.0',
                            'error': {
                                'code': -32601 if not method_found else -32000,
                                'message': f'Method not found: {method_name}' if not method_found else error
                            },
                            'id': request_id
                        }, False
                return None, True  # It's a notification, no response needed
            
            # Handle response to a previous request
            elif ('result' in data or 'error' in data) and 'id' in data:
                self.handle_response(remote, data)
                return None, True  # No response needed for a response
                
            return None, True  # Unknown message type, treat as notification
                
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32700,
                    'message': 'Parse error: Invalid JSON'
                },
                'id': None
            }, False
    
    def handle_system_list_components(self, remote, request_id):
        """
        Handle the system.listComponents request.
        
        Args:
            remote: The remote connection
            request_id: The request ID to include in the response
            
        Returns:
            The response object
        """
        components = {}
        for cls in self.classes:
            for name in cls.keys():
                components[name] = name
        
        return {
            'jsonrpc': '2.0',
            'result': components,
            'id': request_id
        }
    
    def handle_response(self, remote, data):
        """
        Handle responses to requests we've sent.
        By default does nothing, should be overridden by subclasses.
        
        Args:
            remote: The remote connection
            data: The parsed JSON-RPC response
        """
        pass
    
    def process_message(self, connection, message):
        """
        Process a message from a connection.
        
        Args:
            connection: The connection object (ws or client)
            message: The message received
        """
        # Find the remote for this connection
        remote = None
        for r in self.remotes.values():
            if r.get('connection') == connection:
                remote = r
                break
        
        if not remote:
            print("Message received from unknown connection")
            return
        
        # Use common message handling
        response, is_notification = self.handle_message(remote, message)
        
        # Send response if needed
        if not is_notification and response is not None:
            self.send_response(connection, json.dumps(response))
    
    def send_response(self, connection, message):
        """
        Send a response back to a connection.
        Must be implemented by subclasses.
        
        Args:
            connection: The connection to send to
            message: The message to send
        """
        raise NotImplementedError("Subclasses must implement send_response")
    
    def handle_connection_closed(self, connection):
        """
        Common handler for when a connection is closed.
        
        Args:
            connection: The closed connection object
        """
        # Find the remote for this connection
        uuid_to_remove = None
        for uuid, remote in self.remotes.items():
            if remote.get('connection') == connection:
                uuid_to_remove = uuid
                break
        
        if uuid_to_remove:
            self.rm_remote(None, uuid_to_remove)
        
    def request_remote_components(self, remote, connection):
        """
        Request the component list from a remote.
        
        Args:
            remote: The remote to request components from
            connection: The connection object to send the request through
        """
        # Create the standard request
        request = {
            'jsonrpc': '2.0',
            'method': 'system.listComponents',
            'params': [],
            'id': 1
        }
        
        # Send the request (implemented differently in subclasses)
        self.send_request_to_connection(connection, json.dumps(request))
    
    def send_request_to_connection(self, connection, message):
        """
        Send a request to a specific connection.
        Must be implemented by subclasses.
        
        Args:
            connection: The connection to send to
            message: The message to send
        """
        raise NotImplementedError("Subclasses must implement send_request_to_connection")
    
    def start_background_thread(self, target):
        """
        Start a background thread for the given target.
        
        Args:
            target: The object with a run_forever method
        
        Returns:
            The created thread
        """
        thread = threading.Thread(target=target.run_forever)
        thread.daemon = True
        thread.start()
        return thread
    
    def add_class(self, c, obj_name=None):
        """
        Add a class to expose its methods over RPC.
        
        Args:
            c: The class instance to expose
            obj_name: Optional name to use instead of the class name
        """
        # Add helper methods to the class
        c.get_remotes = lambda: self.remotes
        c.get_call = lambda: self.call
        c.get_server = lambda: self.server  # To be removed in future
        
        # Expose the class methods
        expose_class = ExposeClass()
        jrpc_obj = expose_class.expose_all_methods(c, obj_name)
        
        if self.classes is None:
            self.classes = [jrpc_obj]
        else:
            self.classes.append(jrpc_obj)
        
        # Update existing remotes with the new methods
        if self.remotes:
            for remote in self.remotes.values():
                # Implementation in subclasses
                pass
