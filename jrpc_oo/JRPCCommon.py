"""
Common functionality for JRPC client and server.
Equivalent to JavaScript JRPCCommon class.
"""

import uuid
from typing import Dict, Any, Callable, List, Optional, Union
from .JRPC2 import JRPC2
from .ExposeClass import ExposeClass


class Promise:
    """Simple Promise-like implementation for Python."""
    
    def __init__(self, executor=None):
        self.then_callbacks = []
        self.catch_callbacks = []
        if executor:
            try:
                executor(self._resolve, self._reject)
            except Exception as e:
                self._reject(e)
    
    def _resolve(self, value):
        """Resolve the promise with a value and process callbacks"""
        print(f"Promise resolving with value: {value}")
        # Make a copy of callbacks to avoid modification during iteration
        callbacks = self.then_callbacks.copy()
        self.then_callbacks = []
        
        for callback in callbacks:
            try:
                result = callback(value)
                if hasattr(result, 'then'):
                    # Chain promise resolutions
                    result.then(
                        lambda val: self._resolve(val),
                        lambda err: self._reject(err)
                    )
                # If no then method but still a result, continue with that result
                elif result is not None:
                    self._resolve(result)
            except Exception as e:
                print(f"Promise callback error: {str(e)}")
                import traceback
                traceback.print_exc()
                self._reject(e)
    
    def _reject(self, reason):
        for callback in self.catch_callbacks:
            try:
                callback(reason)
            except Exception as e:
                print(f"Unhandled rejection in catch callback: {str(e)}")
    
    def then(self, callback):
        self.then_callbacks.append(callback)
        return self
    
    def catch(self, callback):
        self.catch_callbacks.append(callback)
        return self


class JRPCCommon:
    """Common functionality for JRPC client and server."""
    
    def __init__(self):
        """Initialize common JRPC functionality."""
        self.remotes = {}  # uuid -> remote
        self.classes = []  # Classes exposed for RPC
        self.server = {}  # Legacy compat - functions exposed by remote
        self.call = {}  # Functions to call on all remotes
        self.remote_timeout = 60  # Default timeout
    
    def new_remote(self):
        """
        Instantiate a new remote.
        
        Returns:
            New remote instance
        """
        remote = JRPC2(remote_timeout=self.remote_timeout)
        remote.uuid = str(uuid.uuid4())
        if not hasattr(self, 'remotes') or self.remotes is None:
            self.remotes = {}
        self.remotes[remote.uuid] = remote
        return remote
    
    def create_remote(self, ws):
        """
        Function called when a WebSocket connection is established.
        
        Args:
            ws: The WebSocket connection
            
        Returns:
            The new remote instance
        """
        remote = self.new_remote()
        self.remote_is_up()
        
        # Set up WebSocket handlers based on ws implementation
        def transmit_func(message, next_callback):
            try:
                ws.send(message)
                next_callback(False)
            except Exception as e:
                print(f"Transmission error: {str(e)}")
                next_callback(True)
        
        remote.set_transmitter(transmit_func)
        
        # Setup the remote with exposed classes
        if hasattr(self, 'classes') and self.classes:
            for cls in self.classes:
                remote.expose(cls)
        
        remote.upgrade()
        
        # Set up the on_message handler to receive messages
        if hasattr(ws, 'on_message'):
            ws.on_message = lambda message: remote.receive(message)
        
        # Set up on_close handler
        if hasattr(ws, 'on_close'):
            ws.on_close = lambda: self.rm_remote(None, remote.uuid)
            
        # List available components from the remote
        def on_components_listed(err, result):
            print(f"system.listComponents callback - err: {err}, result: {result}")
            if err:
                print(f"Error listing components: {err}")
                return
            
            if result:
                method_names = list(result.keys())
                print(f"Remote components available: {method_names}")
                self.setup_fns(method_names, remote)
                print("setup_fns completed")
            else:
                print("No components returned from remote")
        
        print("Calling system.listComponents")
        # Use an empty array for parameters to match JS implementation
        remote.call('system.listComponents', [], on_components_listed)
        
        return remote
    
    def remote_is_up(self):
        """
        Called when a remote connection is established.
        Overload this to execute code when the remote comes up.
        """
        print("JRPCCommon::remote_is_up")
    
    def rm_remote(self, event, uuid):
        """
        Remove a remote connection.
        
        Args:
            event: Event data
            uuid: UUID of the remote to remove
        """
        # Remove methods from server (legacy compat)
        if hasattr(self, 'server') and self.server and uuid in self.remotes:
            remote = self.remotes[uuid]
            if hasattr(remote, 'rpcs'):
                for fn in remote.rpcs.keys():
                    if fn in self.server:
                        del self.server[fn]
        
        # Remove the remote
        if hasattr(self, 'remotes') and self.remotes and uuid in self.remotes:
            del self.remotes[uuid]
        
        # Update call methods
        if hasattr(self, 'call') and self.call and hasattr(self, 'remotes') and self.remotes:
            remaining_fns = []
            for remote_id, remote in self.remotes.items():
                if hasattr(remote, 'rpcs') and remote.rpcs:
                    remaining_fns.extend(list(remote.rpcs.keys()))
            
            # Remove functions that no longer exist in any remote
            for fn_name in list(self.call.keys()):
                if fn_name not in remaining_fns:
                    del self.call[fn_name]
        else:
            self.call = {}  # Reset call object if no remotes remain
        
        # Notify about disconnection
        self.remote_disconnected(uuid)
    
    def remote_disconnected(self, uuid):
        """
        Notify that a remote has been disconnected.
        
        Args:
            uuid: UUID of the disconnected remote
        """
        print(f"JPRCCommon::remote_disconnected {uuid}")
    
    def setup_fns(self, fn_names, remote):
        """
        Set up functions for calling on the remote.
        
        Args:
            fn_names: List of function names
            remote: Remote instance
        """
        # Initialize remote RPCs container if needed
        if not hasattr(remote, 'rpcs') or remote.rpcs is None:
            remote.rpcs = {}
        
        # Create RPC functions for each method name
        for fn_name in fn_names:
            # Create a function in remote.rpcs that returns a Promise
            def create_fn(fn_name=fn_name):  # Use default parameter to create closure
                def fn_call(*args):
                    def executor(resolve, reject):
                        def callback(err, result):
                            if err:
                                print(f"Error when calling remote function: {fn_name}")
                                reject(err)
                            else:
                                print(f"Remote function {fn_name} returned: {result}")
                                resolve(result)
                            
                        print(f"Calling remote function: {fn_name} with args: {args}")
                        remote.call(fn_name, {'args': args}, callback)
                        
                    return Promise(executor)
                return fn_call
            
            remote.rpcs[fn_name] = create_fn(fn_name)
            
            # Create function in this.call for calling all remotes with this function
            if not hasattr(self, 'call') or self.call is None:
                self.call = {}
                
            if fn_name not in self.call:
                def create_call_all(fn_name=fn_name):  # Use default parameter to create closure
                    def call_all(*args):
                        promises = []
                        rem_ids = []
                        
                        print(f"Call all for {fn_name} with args: {args}")
                        print(f"Available remotes: {list(self.remotes.keys())}")
                        
                        for rem_id, rem in self.remotes.items():
                            if hasattr(rem, 'rpcs') and rem.rpcs and fn_name in rem.rpcs:
                                print(f"Adding remote {rem_id} to call {fn_name}")
                                rem_ids.append(rem_id)
                                promises.append(rem.rpcs[fn_name](*args))
                        
                        def all_settled(promises):
                            def executor(resolve, reject):
                                results = [None] * len(promises)
                                completed = 0
                                
                                for i, promise in enumerate(promises):
                                    def make_handler(idx):
                                        def handler(result):
                                            nonlocal completed
                                            results[idx] = result
                                            completed += 1
                                            if completed == len(promises):
                                                # Create result dict with remote IDs as keys
                                                result_dict = {rem_ids[j]: results[j] for j in range(len(rem_ids))}
                                                resolve(result_dict)
                                        return handler
                                    
                                    def error_handler(err):
                                        nonlocal completed
                                        results[i] = None
                                        completed += 1
                                        if completed == len(promises):
                                            # Even if some promises failed, we still resolve with what we have
                                            result_dict = {rem_ids[j]: results[j] for j in range(len(rem_ids))}
                                            resolve(result_dict)
                                    
                                    promise.then(make_handler(i)).catch(error_handler)
                            
                            return Promise(executor)
                        
                        return all_settled(promises)
                    
                    return call_all
                
                self.call[fn_name] = create_call_all(fn_name)
            
            # For backwards compatibility (server)
            if not hasattr(self, 'server') or self.server is None:
                self.server = {}
                
            if fn_name not in self.server:
                self.server[fn_name] = remote.rpcs[fn_name]
            else:
                # Multiple remotes with the same function name - error case
                def error_fn(*args):
                    p = Promise()
                    p._reject(f"More than one remote has this RPC, not sure who to talk to: {fn_name}")
                    return p
                
                self.server[fn_name] = error_fn
        
        # For each new function we receive, call setup_done
        # This ensures the server can know when new functions become available
        if len(fn_names) > 0:
            print(f"Calling setup_done from setup_fns with {len(fn_names)} functions: {fn_names}")
            self.setup_done()
    
    def setup_done(self):
        """
        Called when the setup is complete.
        You should override this function to get a notification once the 'server' variable is ready.
        """
        print("*** setup_done called ***")
        print("Setup complete. Remote functions available:", list(self.server.keys()))
        print("Call functions available:", list(self.call.keys()))
    
    def add_class(self, cls_instance, obj_name=None):
        """
        Add a class to the JRPC system.
        
        Args:
            cls_instance: Class instance to expose
            obj_name: Optional name to use instead of the class name
        """
        # Add methods to access JRPC properties
        cls_instance.get_remotes = lambda: self.remotes
        cls_instance.get_call = lambda: self.call
        cls_instance.get_server = lambda: self.server  # Legacy compat
        
        # Expose class methods
        expose_class = ExposeClass()
        jrpc_obj = expose_class.expose_all_fns(cls_instance, obj_name)
        
        if not hasattr(self, 'classes') or self.classes is None:
            self.classes = [jrpc_obj]
        else:
            self.classes.append(jrpc_obj)
            
        # Update all existing remotes
        if hasattr(self, 'remotes') and self.remotes:
            for remote in self.remotes.values():
                remote.expose(jrpc_obj)
                remote.upgrade()
