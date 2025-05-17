"""
Common functionality for JSON-RPC over WebSockets.
"""

import uuid
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
    
    def new_remote(self):
        """
        Create a new remote connection.
        
        Returns:
            The new remote object
        """
        remote = {}
        remote["uuid"] = str(uuid.uuid4())
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
        # Set up transmitter - implementation will be in subclasses
        
        # Expose registered classes
        if self.classes:
            for cls in self.classes:
                # Expose the class to the remote
                pass
                
        # Call system.listComponents to get available methods
    
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
