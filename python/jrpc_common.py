#!/usr/bin/env python3
"""
JSON-RPC 2.0 Common base class for client and server implementations using jsonrpclib-pelix
"""
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib import Server
import asyncio
import uuid
import json
from expose_class import ExposeClass

class JRPCCommon:
    def __init__(self, debug=False):
        self.instances = {}  # Registered class instances
        self.remotes = {}    # Connected remote endpoints
        self.remote_timeout = 60
        self.server = None
        self.client = None
        self.classes = []    # Registered classes for RPC
        
    def register_instance(self, instance, class_name=None):
        """Register a class instance for RPC access"""
        if class_name is None:
            class_name = instance.__class__.__name__
        self.instances[class_name] = instance
        # Give the instance access to our client connection if it needs it
        if hasattr(instance, 'client'):
            instance.client = self.client
        

    def list_components(self):
        """List all registered components and their methods"""
        components = {}
        for class_name, instance in self.instances.items():
            methods = [name for name in dir(instance) 
                      if callable(getattr(instance, name)) and not name.startswith('_')]
            for method in methods:
                method_name = f"{class_name}.{method}"
                components[method_name] = True
        return components

    async def call_remote(self, method: str, *args):
        """Make an RPC call to the remote endpoint"""
        if self.client is None:
            raise RuntimeError("No client connection established")
        try:
            method_call = getattr(self.client, method)
            result = method_call(*args)
            
            # Handle potential coroutine results
            if asyncio.iscoroutine(result):
                result = await result
            return result
        except Exception as e:
            print(f"Remote call failed: {e}")
            raise
