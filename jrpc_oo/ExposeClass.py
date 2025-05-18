"""
Class to expose another class's methods for use with JSON-RPC.
Similar to JavaScript ExposeClass.
"""

import inspect
from typing import Any, Dict, List, Callable, Optional


class ExposeClass:
    """Class to expose another class's methods for use with JSON-RPC."""
    
    def get_all_fns(self, cls_instance: Any, obj_name: Optional[str] = None) -> List[str]:
        """
        Get the functions in a class, without the constructor.
        The names include the class name.method_name
        
        Args:
            cls_instance: The class instance to inspect
            obj_name: An optional name to prepend which doesn't allow inheritance iteration
            
        Returns:
            List of function names as strings
        """
        names = []
        cls = cls_instance.__class__
        
        # Use provided name or class name
        if obj_name is not None:
            class_name = obj_name
        else:
            class_name = cls.__name__
        
        # Get methods from class and its inheritance chain
        current_cls = cls
        while current_cls != object:
            # Get all methods belonging to this class
            for name, method in inspect.getmembers(current_cls, predicate=inspect.isfunction):
                if not name.startswith('__') and name != 'constructor':  # Skip special methods
                    if f"{class_name}.{name}" not in names:
                        names.append(f"{class_name}.{name}")
            
            # Move up the inheritance chain
            if obj_name is not None:  # If object name is specified, don't go up the inheritance chain
                break
                
            current_cls = current_cls.__bases__[0] if current_cls.__bases__ else object
        
        return names
    
    def expose_all_fns(self, cls_instance: Any, name: Optional[str] = None) -> Dict[str, Callable]:
        """
        For each function in cls_instance, create a JSON-RPC friendly function.
        
        Args:
            cls_instance: Get all functions from this class to expose
            name: Optional name to use instead of the class name
            
        Returns:
            Dictionary with exposed functions
        """
        fns = self.get_all_fns(cls_instance, name)
        fns_exp = {}
        
        for fn_name in fns:
            method_name = fn_name.split('.')[1]
            
            # Create a wrapper function for each method
            def create_wrapper(method_name):
                def wrapper(params, next_callback):
                    try:
                        args = params.get('args', [])
                        result = getattr(cls_instance, method_name)(*args)
                        next_callback(None, result)
                    except Exception as e:
                        print(f"Failed: {str(e)}")
                        next_callback(str(e), None)
                return wrapper
            
            fns_exp[fn_name] = create_wrapper(method_name)
        
        return fns_exp
