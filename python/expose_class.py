#!/usr/bin/env python3
"""Python equivalent of ExposeClass.js for method discovery and exposure"""
import asyncio
import inspect

class ExposeClass:
    """Handles discovery and exposure of class methods for RPC"""
    
    def get_all_methods(self, cls, obj_name=None):
        """Get all callable methods from a class
        
        Args:
            cls: Class instance to inspect
            obj_name: Optional name to prepend to method names
        
        Returns:
            List of method names in format "ClassName.method_name"
        """
        methods = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_'):  # Skip private/special methods
                attr = getattr(cls, attr_name)
                if callable(attr):
                    name = f"{obj_name or cls.__class__.__name__}.{attr_name}"
                    methods.append(name)
        return methods

    def expose_all_methods(self, cls, obj_name=None):
        """Create RPC-friendly wrapper for all methods
        
        Args:
            cls: Class instance to expose methods from
            obj_name: Optional name to prepend to method names
            
        Returns:
            Dict of exposed methods with RPC-friendly wrappers
        """
        methods = self.get_all_methods(cls, obj_name)
        exposed = {}
        
        for method_name in methods:
            short_name = method_name.split('.')[-1]
            method = getattr(cls, short_name)
            
            async def wrapper(*args, method=method):
                try:
                    result = method(*args)
                    if asyncio.iscoroutine(result):
                        result = await result
                    return result
                except Exception as e:
                    raise RuntimeError(f"Method call failed: {e}")
                    
            exposed[method_name] = wrapper
            
        return exposed
