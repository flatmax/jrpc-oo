#!/usr/bin/env python3
"""
Python equivalent of the JRPCServerTest.js test file.
"""
import asyncio
import sys
import os
import json
import ssl
import shutil
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from jrpc_oo.JRPCServer import JRPCServer
from jrpc_oo.cert import Cert


class TestClass:
    """Test class with methods to expose via JRPC."""
    
    def __init__(self):
        self.test = 1
    
    def fn1(self, args=None):
        """Equivalent to the JavaScript fn1 method."""
        print('this is fn1')
        print('got args')
        # In Python we access arguments directly by their parameter names
        print(f'args={args}')
        return 'this is fn1'
    
    def fn2(self, arg1, arg2):
        """Equivalent to the JavaScript fn2 method."""
        print('fn2')
        print('arg1 :')
        print(json.dumps(arg1, indent=2))
        print('')
        print('arg2 :')
        print(json.dumps(arg2, indent=2))
        return arg1
    
    @property
    def server(self):
        """Property to access server functions."""
        return self.get_server()
    
    def echoBack(self, args):
        """Echo back function with delayed response."""
        print(f'echoBack {args}')
        # Schedule callEchoBack to run after 1 second
        asyncio.create_task(self.call_echo_back('nodejs responding'))
        return 'nodejs returning done'
    
    async def call_echo_back(self, args):
        """Call echoBack on remote client after a delay."""
        await asyncio.sleep(1)  # Equivalent to setTimeout
        try:
            result = await self.server['LocalJRPC.echoBack'](args)
            print('echoBack returns')
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error calling echoBack: {e}")


class TestClass2(TestClass):
    """Extension of TestClass with additional method."""
    
    def fn3(self, args):
        """Additional function in TestClass2."""
        print(json.dumps(args, indent=2))
        return 'this is fn3'


async def main():
    """Main function to set up the server."""
    # Parse command-line arguments
    use_ssl = not ('--no_wss' in sys.argv or 'no_wss' in sys.argv)
    debug = '--debug' in sys.argv
    
    # Setup SSL if requested
    ssl_context = None
    if use_ssl:
        print("Setting up SSL certificates for WSS connection...")
        
        # Create cert directory in a location that works better with JavaScript
        cert_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "certs")
        os.makedirs(cert_dir, exist_ok=True)
        
        # Initialize certificate manager with the specific cert directory
        cert_manager = Cert(domain="localhost", cert_dir=cert_dir)
        success, message = cert_manager.generate_cert()
        print(message)
        
        # Check if certutil is available for browser integration
        def is_certutil_available():
            return shutil.which("certutil") is not None
        
        if not is_certutil_available():
            print("Warning: 'certutil' is not available, so the CA can't be automatically installed in Firefox and/or Chrome/Chromium! ⚠️")
            print("Install 'certutil' with 'apt install libnss3-tools' and re-run 'mkcert -install' 👈")
        
        if success:
            cert_path, key_path = cert_manager.get_cert_paths()
            print(f"Using SSL certificates:")
            print(f"Certificate: {cert_path}")
            print(f"Key: {key_path}")
            
            
            # Create SSL context for Python server
            try:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(cert_path, key_path)
                print("SSL context created successfully for Python server")
            except Exception as e:
                print(f"Error creating SSL context: {e}")
                print("Falling back to WS connection")
                use_ssl = False
                ssl_context = None
        else:
            print("Failed to generate SSL certificates, falling back to WS")
            use_ssl = False
    
    # Create server with SSL if available
    if use_ssl and ssl_context:
        jrpc_server = JRPCServer(port=9000, remote_timeout=60, ssl_context=ssl_context)
    else:
        jrpc_server = JRPCServer(port=9000, remote_timeout=60)
    
    # Create test class instance
    tc2 = TestClass2()
    
    # Add class to server
    jrpc_server.add_class(tc2, "TestClass")  # Explicitly set the class name
    
    # Debug what methods are exposed
    if hasattr(jrpc_server, 'methods'):
        print("Exposed methods:")
        for method_name in jrpc_server.methods:
            print(f"  - {method_name}")
    
    # Start server
    await jrpc_server.start()
    
    protocol = "WSS" if use_ssl else "WS"
    print(f"Server started on port 9000 with {protocol} protocol")
    print(f"Connect to: {protocol.lower()}://localhost:9000")
    
    # Print certificate information for verification
    if use_ssl and ssl_context:
        print("\nCertificate locations for JavaScript client:")
        print(f"- ./cert/server.crt")
        print(f"- ./cert/server.key")
        print("\nWhen running JRPCServerTest.js in the same directory, you should be able to use SSL")
        print("without explicitly generating certificates in the JavaScript code.")
    
    try:
        # Keep server running indefinitely
        await asyncio.Future()
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        await jrpc_server.stop()


if __name__ == "__main__":
    asyncio.run(main())
