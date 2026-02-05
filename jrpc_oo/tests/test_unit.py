"""
Unit tests for JRPC Python implementation.
Phase 1: Critical fixes verification.
"""
import pytest
import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jrpc_oo.JRPC2 import JRPC2
from jrpc_oo.JRPCServer import JRPCServer
from jrpc_oo.JRPCCommon import JRPCCommon
from jrpc_oo.ExposeClass import ExposeClass


class TestJRPC2ResponseParsing:
    """Tests for JRPC2 response parsing logic (Issue 1.1)."""
    
    def test_valid_response_with_result(self):
        """T1.1: Valid response with id and result should invoke callback."""
        jrpc = JRPC2()
        callback_called = False
        callback_result = None
        callback_error = None
        
        def callback(err, result):
            nonlocal callback_called, callback_result, callback_error
            callback_called = True
            callback_result = result
            callback_error = err
        
        # Manually add a pending request
        request_id = "test-123"
        jrpc.requests[request_id] = callback
        
        # Simulate receiving a valid response
        message = json.dumps({
            'jsonrpc': '2.0',
            'id': request_id,
            'result': 'success'
        })
        jrpc.receive(message)
        
        assert callback_called, "Callback should be invoked for valid response"
        assert callback_result == 'success', "Result should be passed to callback"
        assert callback_error is None, "Error should be None for successful response"
        assert request_id not in jrpc.requests, "Request should be removed after response"
    
    def test_valid_error_response(self):
        """T1.2: Valid error response should invoke callback with error."""
        jrpc = JRPC2()
        callback_called = False
        callback_error = None
        
        def callback(err, result):
            nonlocal callback_called, callback_error
            callback_called = True
            callback_error = err
        
        request_id = "test-456"
        jrpc.requests[request_id] = callback
        
        message = json.dumps({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {'code': -32000, 'message': 'Test error'}
        })
        jrpc.receive(message)
        
        assert callback_called, "Callback should be invoked for error response"
        assert callback_error is not None, "Error should be passed to callback"
    
    def test_malformed_message_error_only_ignored(self):
        """T1.3: Message with only 'error' key (no 'id') should be ignored."""
        jrpc = JRPC2()
        callback_called = False
        
        def callback(err, result):
            nonlocal callback_called
            callback_called = True
        
        # Add a pending request that should NOT be affected
        jrpc.requests["unrelated-request"] = callback
        
        # Send malformed message with only 'error' - no 'id'
        # Before fix: this would incorrectly match the response condition
        # After fix: this should be ignored (not a valid response)
        message = json.dumps({
            'error': 'orphan error message'
        })
        jrpc.receive(message)
        
        assert not callback_called, "Callback should NOT be invoked for message without 'id'"
        assert "unrelated-request" in jrpc.requests, "Pending request should remain"
    
    def test_response_requires_id(self):
        """Additional test: Response must have 'id' to be processed."""
        jrpc = JRPC2()
        
        # Message with result but no id should not crash and should be ignored
        message = json.dumps({
            'jsonrpc': '2.0',
            'result': 'orphan result'
        })
        # Should not raise any exception
        jrpc.receive(message)


class TestJRPCServerAttributeCollision:
    """Tests for JRPCServer attribute collision fix (Issue 1.2)."""
    
    def test_server_dict_not_overwritten(self):
        """Verify parent's self.server dict is preserved after init."""
        server = JRPCServer(port=19000)
        
        # Parent JRPCCommon sets self.server = {} for RPC methods
        assert hasattr(server, 'server'), "Server should have 'server' attribute"
        assert isinstance(server.server, dict), "server.server should be a dict (from parent)"
        
        # WebSocket server should be stored in ws_server
        assert hasattr(server, 'ws_server'), "Server should have 'ws_server' attribute"
        assert server.ws_server is None, "ws_server should be None before start()"
    
    def test_ws_server_attribute_exists(self):
        """Verify ws_server attribute is properly initialized."""
        server = JRPCServer(port=19001, ssl_context=None)
        
        assert hasattr(server, 'ws_server'), "ws_server attribute should exist"
        assert server.ws_server is None, "ws_server should be None initially"
    
    @pytest.mark.asyncio
    async def test_server_start_uses_ws_server(self):
        """Verify start() populates ws_server, not server."""
        server = JRPCServer(port=19002)
        
        try:
            await server.start()
            
            # ws_server should now be set
            assert server.ws_server is not None, "ws_server should be set after start()"
            
            # server dict should still be a dict (not overwritten)
            assert isinstance(server.server, dict), "server should still be a dict"
            
        finally:
            await server.stop()
    
    @pytest.mark.asyncio
    async def test_server_stop_uses_ws_server(self):
        """Verify stop() uses ws_server attribute."""
        server = JRPCServer(port=19003)
        
        await server.start()
        assert server.ws_server is not None, "ws_server should be set"
        
        await server.stop()
        # After stop, ws_server.close() was called - server should be closed
        # We verify it didn't crash and the attribute was used correctly


class TestJRPCCommonInheritance:
    """Tests verifying JRPCCommon functionality is preserved."""
    
    def test_server_dict_initialized(self):
        """Verify JRPCCommon initializes server as dict."""
        common = JRPCCommon()
        
        assert hasattr(common, 'server'), "JRPCCommon should have 'server' attribute"
        assert isinstance(common.server, dict), "server should be initialized as dict"
    
    def test_remotes_initialized(self):
        """Verify remotes dict is initialized."""
        common = JRPCCommon()
        
        assert hasattr(common, 'remotes'), "Should have 'remotes' attribute"
        assert isinstance(common.remotes, dict), "remotes should be a dict"
    
    def test_call_initialized(self):
        """Verify call dict is initialized."""
        common = JRPCCommon()
        
        assert hasattr(common, 'call'), "Should have 'call' attribute"
        assert isinstance(common.call, dict), "call should be a dict"


class TestExposeClass:
    """Basic tests for ExposeClass functionality."""
    
    def test_get_all_fns_excludes_private(self):
        """T2.3: Private methods should not be exposed."""
        
        class TestClass:
            def public_method(self):
                pass
            
            def _private_method(self):
                pass
            
            def __dunder_method__(self):
                pass
        
        expose = ExposeClass()
        instance = TestClass()
        fns = expose.get_all_fns(instance)
        
        fn_names = [fn.split('.')[-1] for fn in fns]
        
        assert 'public_method' in fn_names, "Public method should be included"
        assert '_private_method' not in fn_names, "Private method should be excluded"
        assert '__dunder_method__' not in fn_names, "Dunder method should be excluded"
    
    def test_get_all_fns_with_custom_name(self):
        """Test using custom object name."""
        
        class MyClass:
            def my_method(self):
                pass
        
        expose = ExposeClass()
        instance = MyClass()
        fns = expose.get_all_fns(instance, obj_name="CustomName")
        
        assert any("CustomName.my_method" in fn for fn in fns), \
            "Custom name should be used as prefix"
        assert not any("MyClass." in fn for fn in fns), \
            "Original class name should not appear when custom name provided"
    
    def test_expose_all_fns_returns_callable_wrappers(self):
        """T2.4: Exposed functions should be callable with args dict."""
        
        class Calculator:
            def add(self, a, b):
                return a + b
        
        expose = ExposeClass()
        calc = Calculator()
        exposed = expose.expose_all_fns(calc)
        
        # Find the add function
        add_fn = None
        for name, fn in exposed.items():
            if 'add' in name:
                add_fn = fn
                break
        
        assert add_fn is not None, "add function should be exposed"
        
        # Test calling with args format
        result_holder = {}
        
        def next_cb(err, result):
            result_holder['err'] = err
            result_holder['result'] = result
        
        add_fn({'args': [2, 3]}, next_cb)
        
        assert result_holder.get('err') is None, "Should not have error"
        assert result_holder.get('result') == 5, "2 + 3 should equal 5"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
