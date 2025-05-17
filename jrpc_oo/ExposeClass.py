"""
ExposeClass module provides functionality to expose class methods over RPC.
"""

import inspect

class ExposeClass:
    """
    Class that helps expose methods of other classes for RPC.
    Similar to the JavaScript ExposeClass.
    """
    
    def get_all_methods(self, obj_to_expose, obj_name=None):
        """
        Get the functions in a class, without the constructor.
        The names include the class name . method name.
        
        Args:
            obj_to_expose: The object whose methods will be exposed
            obj_name: An optional name to prepend
        
        Returns:
            The functions as a list of strings
        """
        names = []
        cls = obj_to_expose.__class__
        
        # Iterate through the inheritance tree
        for c in cls.__mro__:
            if c is object:  # Skip built-in object class
                continue
                
            obj_class_name = c.__name__
            if obj_name is not None:
                obj_class_name = obj_name
                
            # Get methods that aren't special methods
            for name, method in inspect.getmembers(c, predicate=inspect.isfunction):
                if not name.startswith('__'):
                    method_name = f"{obj_class_name}.{name}"
                    if method_name not in names:
                        names.append(method_name)
        
        return names
    
    def expose_all_methods(self, class_to_expose, name=None):
        """
        Create a dictionary of RPC-ready functions for each method in the class.
        
        Args:
            class_to_expose: The object whose methods will be exposed
            name: Optional name to prepend
        
        Returns:
            Dictionary of functions that can be exposed over RPC
        """
        methods = self.get_all_methods(class_to_expose, name)
        funcs_exposed = {}
        
        for method_name in methods:
            # Get the actual method name (after the dot)
            actual_method_name = method_name.split('.')[1]
            
            # Create wrapper function that will handle the RPC call
            def create_wrapper(method):
                def wrapper(params, next_func=None):
                    try:
                        result = method(*params.get('args', []))
                        if next_func:
                            return next_func(None, result)
                        return result
                    except Exception as e:
                        print(f"Failed: {e}")
                        if next_func:
                            return next_func(str(e), None)
                        raise
                return wrapper
            
            # Get the method from the class and create a wrapper
            method = getattr(class_to_expose, actual_method_name)
            funcs_exposed[method_name] = create_wrapper(method)
            
        return funcs_exposed
