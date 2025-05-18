"""
Common functionality for JRPC clients and servers.
"""
import asyncio
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import importlib.util

# Check if running in Python or using a web context
try:
    import websockets
    IS_BROWSER = False
except ImportError:
    IS_BROWSER = True

# Import our modules
from .ExposeClass import ExposeClass
from .JRPC2 import JRPC2


class JRPCCommon:
    """Common functionality for JRPC clients and servers."""
    
    def __init__(self):
        """Initialize the JRPCCommon object."""
        self.remotes = {}  # Maps UUID to remote
        self.classes = []  # List of exposed class objects
        self.call = {}     # Function to call all remotes with the same method
        self.server = {}   # Legacy: Functions mapped to a particular remote
        self.remote_timeout = 60
        
    def new_remote(self) -> JRPC2:
        """Instantiate a new remote. It gets added to the array of remotes.
        
        Returns:
            The new remote object
        """
        remote = JRPC2(remote_timeout=self.remote_timeout)
        remote.uuid = str(uuid.uuid4())
        
        if not hasattr(self, 'remotes') or self.remotes is None:
            self.remotes = {}
            
        self.remotes[remote.uuid] = remote
        return remote
    
    def create_remote(self, ws):
        """Function called when a WebSocket connection is established.
        
        Args:
            ws: The WebSocket object for communication
        """
        remote = self.new_remote()
        self.remote_is_up()
        
        # Set up message transmission and handling
        if hasattr(self, 'ws'):  # Browser version
            ws = self.ws
            
            async def on_message(message):
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                remote.receive(message)
                
            async def transmit(msg, next_cb):
                try:
                    await ws.send(msg)
                    next_cb(False)
                except Exception as e:
                    print(f"Error transmitting: {e}")
                    next_cb(True)
            
            ws.on_message = on_message
            ws.on_close = lambda ev: self.rm_remote(ev, remote.uuid)
            remote.set_transmitter(transmit)
            
        else:  # Server version
            async def on_message(message):
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                remote.receive(message)
                
            async def transmit(msg, next_cb):
                try:
                    await ws.send(msg)
                    next_cb(False)
                except Exception as e:
                    print(f"Error transmitting: {e}")
                    next_cb(True)
            
            ws.on_message = on_message
            ws.on_close = lambda: self.rm_remote(None, remote.uuid)
            remote.set_transmitter(transmit)
            
        self.setup_remote(remote, ws)
        return remote
    
    def remote_is_up(self):
        """Called when a remote connection is established."""
        print("JRPCCommon::remote_is_up")
    
    def rm_remote(self, event, uuid):
        """Remove a remote connection.
        
        Args:
            event: Event that triggered the removal
            uuid: UUID of the remote to remove
        """
        # Remove methods from server object
        if hasattr(self, 'server') and self.server:
            if uuid in self.remotes and hasattr(self.remotes[uuid], 'rpcs'):
                for fn in self.remotes[uuid].rpcs:
                    if fn in self.server:
                        del self.server[fn]
        
        # Remove the remote
        if hasattr(self, 'remotes') and self.remotes and uuid in self.remotes:
            del self.remotes[uuid]
        
        # Update call methods
        if hasattr(self, 'call') and self.call and hasattr(self, 'remotes') and self.remotes:
            remaining_fns = []
            for rem_uuid in self.remotes:
                if hasattr(self.remotes[rem_uuid], 'rpcs'):
                    remaining_fns.extend(self.remotes[rem_uuid].rpcs.keys())
            
            if hasattr(self, 'call'):
                existing_fns = list(self.call.keys())
                for fn in existing_fns:
                    if fn not in remaining_fns:
                        del self.call[fn]
        else:
            self.call = {}
        
        self.remote_disconnected(uuid)
    
    def remote_disconnected(self, uuid):
        """Notify that a remote has been disconnected.
        
        Args:
            uuid: UUID of the disconnected remote
        """
        print(f"JRPCCommon::remote_disconnected {uuid}")
    
    def setup_remote(self, remote, ws):
        """Expose classes and handle setting up remote's functions.
        
        Args:
            remote: The remote to set up
            ws: The WebSocket for transmission
        """
        if hasattr(self, 'classes') and self.classes:
            for cls_obj in self.classes:
                remote.expose(cls_obj)
        
        remote.upgrade()
        
        # List available components
        remote.call('system.listComponents', [], lambda err, result: 
            self.handle_list_components(err, result, remote))
    
    def handle_list_components(self, err, result, remote):
        """Handle the response from system.listComponents.
        
        Args:
            err: Error object if any
            result: Result of the call
            remote: The remote that was called
        """
        if err:
            print(f"Error listing components: {err}")
            return
        
        self.setup_fns(list(result.keys()), remote)
    
    def setup_fns(self, fn_names, remote):
        """Set up functions for calling on the server.
        
        Args:
            fn_names: Functions to make available
            remote: The remote to call
        """
        # Initialize remote.rpcs if needed
        if not hasattr(remote, 'rpcs'):
            remote.rpcs = {}
        
        for fn_name in fn_names:
            # Create function in remote.rpcs
            async def remote_call(params, fn_name=fn_name):
                """Call a remote function and return a Promise."""
                future = asyncio.get_event_loop().create_future()
                
                def callback(err, result):
                    if err:
                        print(f"Error calling {fn_name}: {err}")
                        if not future.done():
                            future.set_exception(Exception(str(err)))
                    else:
                        if not future.done():
                            future.set_result(result)
                
                remote.call(fn_name, {'args': params}, callback)
                return await future
            
            remote.rpcs[fn_name] = remote_call
            
            # Setup call structure for all remotes
            if not hasattr(self, 'call'):
                self.call = {}
                
            if fn_name not in self.call:
                async def call_all_remotes(*args, fn_name=fn_name):
                    """Call the function on all remotes."""
                    promises = []
                    rems = []
                    
                    for r_uuid, r in self.remotes.items():
                        if hasattr(r, 'rpcs') and fn_name in r.rpcs:
                            rems.append(r_uuid)
                            promises.append(r.rpcs[fn_name](*args))
                    
                    results = await asyncio.gather(*promises, return_exceptions=True)
                    
                    # Create a dict of uuid: result
                    result_dict = {}
                    for i, res in enumerate(results):
                        result_dict[rems[i]] = res
                        
                    return result_dict
                
                self.call[fn_name] = call_all_remotes
            
            # For backwards compatibility - setup server functions
            if not hasattr(self, 'server'):
                self.server = {}
                
            if fn_name not in self.server:
                self.server[fn_name] = remote.rpcs[fn_name]
            else:
                async def error_fn(*args):
                    """Error function for ambiguous calls."""
                    raise Exception(f"More than one remote has this RPC, not sure who to talk to: {fn_name}")
                
                self.server[fn_name] = error_fn
        
        self.setup_done()
    
    def setup_done(self):
        """Called when the setup is complete."""
        pass
    
    def add_class(self, cls_instance, obj_name=None):
        """Add a class to the JRPC system. All functions in the class are exposed for use.
        
        Args:
            cls_instance: The class instance to expose
            obj_name: Optional name to use instead of the class name
        """
        # Add getters for the class
        cls_instance.get_remotes = lambda: self.remotes
        cls_instance.get_call = lambda: self.call
        cls_instance.get_server = lambda: self.server  # Legacy
        
        expose_class = ExposeClass()
        jrpc_obj = expose_class.expose_all_fns(cls_instance, obj_name)
        
        if not hasattr(self, 'classes') or self.classes is None:
            self.classes = [jrpc_obj]
        else:
            self.classes.append(jrpc_obj)
        
        # Update existing remotes
        if hasattr(self, 'remotes') and self.remotes:
            for remote in self.remotes.values():
                remote.expose(jrpc_obj)
                remote.upgrade()
