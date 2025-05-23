"""
Class to expose another class's methods for use with JRPC.
"""
import inspect
from typing import Any, Dict, List, Callable, Optional


class ExposeClass:
    """Class to expose another class's methods for use with JRPC."""
    
    def get_all_fns(self, cls_instance, obj_name: Optional[str] = None) -> List[str]:
        """Get the functions in a class, without the constructor.
        
        The names include the class name.method name
        
        Args:
            cls_instance: Instance of the class to analyze
            obj_name: An optional name to prepend which doesn't allow inheritance iteration
            
        Returns:
            The functions as a list of strings
        """
        names = []
        
        # Get class and its mro (method resolution order)
        cls = cls_instance.__class__
        mro = cls.__mro__ if obj_name is None else [cls]
        
        for c in mro:
            if c.__name__ == 'object':
                continue
                
            class_name = obj_name if obj_name is not None else c.__name__
            
            # Get methods that don't start with underscore
            methods = [
                f"{class_name}.{name}" 
                for name, method in inspect.getmembers(c, predicate=inspect.isfunction)
                if not name.startswith('_')
            ]
            
            names.extend(methods)
            
            if obj_name is not None:
                break
                
        return names
    
    def expose_all_fns(self, cls_instance, name: Optional[str] = None) -> Dict[str, Callable]:
        """For each function in cls_instance, create a JRPC friendly function.
        
        Args:
            cls_instance: Instance of the class to expose
            name: If name is specified, use it rather than the constructor's name
            
        Returns:
            A dict with each of cls_instance class's functions extended with JRPC
            required executions
        """
        fns = self.get_all_fns(cls_instance, name)
        fns_exp = {}
        
        for fn_name in fns:
            method_name = fn_name.split('.')[1]
            
            def wrapper(params, next_cb, method_name=method_name):
                """Wrapper function for the method call."""
                try:
                    method = getattr(cls_instance, method_name)
                    
                    # Handle args format used by JS implementation
                    if isinstance(params, dict) and 'args' in params:
                        args = params['args']
                        if isinstance(args, list):
                            result = method(*args)
                        else:
                            result = method(args)
                    else:
                        # For direct calls without args wrapping
                        result = method(params)
                        
                    return next_cb(None, result)
                except Exception as e:
                    print(f"Failed: {e}")
                    return next_cb(str(e), None)
            
            fns_exp[fn_name] = wrapper
            
        return fns_exp
