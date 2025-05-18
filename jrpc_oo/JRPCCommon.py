"""
Common functionality for JRPC client and server.
Equivalent to JavaScript JRPCCommon class.
"""

import uuid
import time
from typing import Dict, Any, Callable, List, Optional, Union
from .JRPC2 import JRPC2
from .ExposeClass import ExposeClass
from .CallbackChain import CallbackChain


class Remote:
    """Wrapper for JRPC2 with additional metadata."""
    
    def __init__(self, jrpc, uuid_str):
        """Initialize a new remote wrapper."""
        self.jrpc = jrpc
        self.uuid = uuid_str
        self.rpcs = {}
        
    def call(self, method, params, callback):
        """Delegate call to the underlying JRPC2 instance."""
        return self.jrpc.call(method, params, callback)


class JRPCCommon:
    """Common functionality for JRPC client and server."""
    
    def __init__(self):
        """Initialize common JRPC functionality."""
        self.remotes = {}  # uuid -> Remote object
        self.classes = []  # Classes exposed for RPC
        self.call = {}     # Functions to call on all remotes
        self.remote_timeout = 60  # Default timeout
    
    def new_remote(self):
        """
        Instantiate a new remote.
        
        Returns:
            New Remote instance
        """
        jrpc = JRPC2(remote_timeout=self.remote_timeout)
        uuid_str = str(uuid.uuid4())
        remote = Remote(jrpc, uuid_str)
        self.remotes[uuid_str] = remote
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
        
        # Set up WebSocket handlers
        def transmit_func(message, next_callback):
            try:
                ws.send(message)
                next_callback(False)
            except Exception as e:
                print(f"Transmission error: {str(e)}")
                next_callback(True)
        
        remote.jrpc.set_transmitter(transmit_func)
        
        # Setup the remote with exposed classes
        if self.classes:
            for cls in self.classes:
                remote.jrpc.expose(cls)
        
        remote.jrpc.upgrade()
        
        # Set up message and close handlers
        if hasattr(ws, 'on_message'):
            ws.on_message = lambda message: remote.jrpc.receive(message)
        
        if hasattr(ws, 'on_close'):
            ws.on_close = lambda: self.rm_remote(None, remote.uuid)
            
        # Get available components from remote with retry logic
        def on_components_listed(err, result):
            if err:
                print(f"Error listing components: {err}")
                # Don't give up immediately - we'll retry later through other mechanisms
                return
            
            if result:
                try:
                    method_names = list(result.keys())
                    print(f"Remote components available: {method_names}")
                    self.setup_fns(method_names, remote)
                except Exception as e:
                    print(f"Error processing components: {str(e)}")
        
        # Add a small delay before calling to ensure remote is initialized
        import time
        time.sleep(0.1)
        
        try:
            remote.jrpc.call('system.listComponents', [], on_components_listed)
        except Exception as e:
            print(f"Error calling system.listComponents: {str(e)}")
        
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
        # Remove the remote
        if uuid in self.remotes:
            del self.remotes[uuid]
        
        # Update call methods - remove functions not in any remote
        self._update_call_functions()
        
        # Notify about disconnection
        self.remote_disconnected(uuid)
    
    def _update_call_functions(self):
        """Update call functions based on available remotes."""
        # If no remotes, clear all call functions
        if not self.remotes:
            self.call = {}
            return
            
        # Get all unique function names from all remotes
        all_functions = set()
        for remote in self.remotes.values():
            all_functions.update(remote.rpcs.keys())
        
        # Remove functions that don't exist in any remote
        for fn_name in list(self.call.keys()):
            if fn_name not in all_functions:
                del self.call[fn_name]
    
    def remote_disconnected(self, uuid):
        """
        Notify that a remote has been disconnected.
        
        Args:
            uuid: UUID of the disconnected remote
        """
        print(f"JPRCCommon::remote_disconnected {uuid}")
    
    def _create_remote_function(self, jrpc, fn_name):
        """Create a function for calling a remote method."""
        def fn_call(*args):
            result_chain = CallbackChain()
            
            def callback(err, result_value):
                if err:
                    print(f"Error calling {fn_name}: {err}")
                    result_chain.error = err
                else:
                    print(f"Function {fn_name} returned: {result_value}")
                    result_chain.value = result_value
            
            try:
                print(f"Calling remote function: {fn_name} with args: {args}")
                jrpc.call(fn_name, {'args': args}, callback)
            except Exception as e:
                print(f"Exception while calling {fn_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                result_chain.error = str(e)
            
            return result_chain
        
        return fn_call
    
    def _create_call_all_function(self, fn_name):
        """Create a function for calling a method on all remotes."""
        def call_all(*args):
            results = {}
            result_chain = CallbackChain()
            
            # No remotes with this function
            if not self.remotes:
                print(f"No remotes available for {fn_name}")
                result_chain.value = {}
                return result_chain
            
            # Find remotes with this function
            active_remotes = {
                remote_id: remote 
                for remote_id, remote in self.remotes.items() 
                if fn_name in remote.rpcs
            }
            
            # If no remotes have this function
            if not active_remotes:
                print(f"Function {fn_name} not available in any remote")
                result_chain.value = {}
                return result_chain
                
            print(f"Calling {fn_name} on {len(active_remotes)} remote(s)")
            
            # Track completion with a counter
            pending_count = len(active_remotes)
            
            # Process results from each remote
            def on_result(remote_id):
                def callback(err, value):
                    nonlocal pending_count
                    
                    if not err:
                        print(f"Result from {remote_id} for {fn_name}: {value}")
                        results[remote_id] = value
                    else:
                        print(f"Error from {remote_id} for {fn_name}: {err}")
                    
                    pending_count -= 1
                    if pending_count == 0:
                        # All results collected
                        print(f"All results collected for {fn_name}")
                        result_chain.value = results
                
                return callback
            
            # Call the function on each remote
            for remote_id, remote in active_remotes.items():
                try:
                    remote.jrpc.call(fn_name, {'args': args}, on_result(remote_id))
                except Exception as e:
                    print(f"Exception calling {fn_name} on {remote_id}: {str(e)}")
                    pending_count -= 1  # Reduce count even for failed calls
            
            return result_chain
        
        return call_all

    def setup_fns(self, fn_names, remote):
        """
        Set up functions for calling on the remote.
        
        Args:
            fn_names: List of function names
            remote: Remote instance
        """
        print(f"Setting up functions for remote {remote.uuid}: {fn_names}")
        
        # Create RPC functions for each method name
        for fn_name in fn_names:
            # Create a function in remote.rpcs 
            remote.rpcs[fn_name] = self._create_remote_function(remote.jrpc, fn_name)
            
            # Create function in this.call for calling all remotes
            if fn_name not in self.call:
                self.call[fn_name] = self._create_call_all_function(fn_name)
        
        # Notify that setup is complete
        if fn_names:
            self.setup_done()
    
    def setup_done(self):
        """
        Called when the setup is complete.
        """
        # Determine what type of class we are
        class_type = self.__class__.__name__
        print(f"{class_type}: Remote functions setup complete")
        
        # Make sure our classes are properly exposed to all remotes
        if self.remotes and self.classes:
            for remote in self.remotes.values():
                # Skip if this remote is already synced
                if remote.rpcs:
                    continue
                    
                # Re-expose all classes to this remote
                for cls in self.classes:
                    remote.jrpc.expose(cls)
                remote.jrpc.upgrade()
        
        print(f"Setup complete. Available functions: {list(self.call.keys())}")
        
    def process_remote_components(self, remote_id, result):
        """Process component list result from remote."""
        if result and remote_id in self.remotes:
            method_names = list(result.keys())
            print(f"Remote {remote_id} components available: {method_names}")
            self.setup_fns(method_names, self.remotes[remote_id])
    
    def add_class(self, cls_instance, obj_name=None):
        """
        Add a class to the JRPC system.
        
        Args:
            cls_instance: Class instance to expose
            obj_name: Optional name to use instead of the class name
        """
        # Expose class methods
        expose_class = ExposeClass()
        jrpc_obj = expose_class.expose_all_fns(cls_instance, obj_name)
        
        # Store the exposed class
        if not self.classes:
            self.classes = [jrpc_obj]
        else:
            self.classes.append(jrpc_obj)
            
        # Update all existing remotes
        for remote in self.remotes.values():
            remote.jrpc.expose(jrpc_obj)
            remote.jrpc.upgrade()
