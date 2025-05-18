"""
Simple callback chain implementation for handling asynchronous operations.
Alternative to JavaScript Promises but simpler for Python.
"""

class CallbackChain:
    """Simple callback chain for handling asynchronous operations."""
    
    def __init__(self, value=None, error=None):
        """Initialize with an optional value or error."""
        self.value = value
        self.error = error
        self._then_called = False
    
    def then(self, callback):
        """Register a callback to handle successful results."""
        if self.error is not None:
            # Skip callback and return self with error intact for chaining
            return self
            
        if callback is not None and not self._then_called:
            self._then_called = True
            try:
                result = callback(self.value)
                # If result is another CallbackChain, return it
                if isinstance(result, CallbackChain):
                    return result
                # Otherwise wrap the result in a new CallbackChain
                return CallbackChain(value=result)
            except Exception as e:
                print(f"Exception in CallbackChain.then: {str(e)}")
                return CallbackChain(error=e)
        return self
    
    def catch(self, callback):
        """Register a callback to handle errors."""
        if self.error is not None and callback is not None:
            try:
                result = callback(self.error)
                # If handler returns a value, create new chain with that value
                return CallbackChain(value=result)
            except Exception as e:
                print(f"Exception in CallbackChain.catch: {str(e)}")
                import traceback
                traceback.print_exc()
                return CallbackChain(error=e)
        return self
