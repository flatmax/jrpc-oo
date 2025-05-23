"""
Python equivalent of the JRPCServerTestConcurrent.js test file.
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from jrpc_oo.JRPCServer import JRPCServer
from jrpc_oo.JRPCCommon import RPCMethodNotFoundError

class TestClass:
    """Test class with methods to expose via JRPC."""
    
    def __init__(self):
        self.test = 1
        self.i = 0
    
    def fn1(self, args):
        """Equivalent to the JavaScript fn1 method."""
        print('this is fn1')
        print('got args')
        print(f'args={args}')
        return 'this is fn1'
    
    async def multi_client_test(self, jrpc_server):
        """Test calling functions on multiple clients."""
        print('multi_client_test : enter')
        try:
            # Call uniqueFn1 on connected client(s)
            try:
                results = await jrpc_server.call['TestClass.uniqueFn1'](self.i, 'hi there 1')
                if len(results) > 1:
                    raise Exception('Expected only one remote to be called')
                i = None
                for uuid, result in results.items():
                    print(f'remote : {uuid} returns {result}')
                    i = result
            except RPCMethodNotFoundError as e:
                print(f'RPC method not found: {e.method_name}')
            except KeyError as e:
                print(f'RPC method not available in call dictionary: {e}')
            except Exception as e:
                print(f'Call to TestClass.uniqueFn1 failed: {e}')
                print(f'Exception type: {type(e).__name__}')
            
            # Call uniqueFn2 on connected client(s)
            try:
                results = await jrpc_server.call['TestClass.uniqueFn2'](self.i, 'hi there 2')
                if len(results) > 1:
                    raise Exception('Expected only one remote to be called')                
                i = None
                for uuid, result in results.items():
                    print(f'remote : {uuid} returns {result}')
                    i = result
            except RPCMethodNotFoundError as e:
                print(f'RPC method not found: {e.method_name}')
            except KeyError as e:
                print(f'RPC method not available in call dictionary: {e}')
            except Exception as e:
                print(f'Call to TestClass.uniqueFn2 failed: {e}')
                            
            # Call commonFn on all connected clients
            try:
                results = await jrpc_server.call['TestClass.commonFn']()
                print('commonFn returns')
                print(results)
            except RPCMethodNotFoundError as e:
                print(f'RPC method not found: {e.method_name}')
            
            self.i += 1
        except Exception as e:
            print('multi_client_test : error')
            print(e)


async def multi_client_test_loop(tc, jrpc_server):
    """Run the multi client test in a loop."""
    while True:
        await tc.multi_client_test(jrpc_server)
        await asyncio.sleep(1)


async def main():
    """Main function to set up the server."""
    jrpc_server = JRPCServer(port=9000)
    
    # Create test class instance and expose it
    tc = TestClass()
    jrpc_server.add_class(tc)
    
    # Start server
    await jrpc_server.start()
    
    # Run test loop
    test_task = asyncio.create_task(multi_client_test_loop(tc, jrpc_server))
    
    try:
        # Keep server running indefinitely
        await asyncio.Future()
    except KeyboardInterrupt:
        print("Server stopped by user")
        test_task.cancel()
    finally:
        await jrpc_server.stop()


if __name__ == "__main__":
    asyncio.run(main())
