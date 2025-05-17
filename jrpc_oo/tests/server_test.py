"""
Test server for JRPC-OO Python implementation.
Similar to JRPCServerTestConcurrent.js
"""

import time
import sys
import os
import subprocess
import pathlib

# Add the repository root to Python path so modules can be imported with their package structure
# This allows relative imports within the package to work
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import using the full package path
from jrpc_oo.JRPCServer import JRPCServer

def ensure_certificates_exist():
    """
    Create certificates for SSL if they don't exist.
    Similar to the logic in JRPCServerTest.sh
    """
    # Get the repository root directory
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cert_dir = os.path.join(repo_root, "cert")
    
    # Check if certificates already exist
    if os.path.exists(cert_dir) and os.path.exists(os.path.join(cert_dir, "server.crt")) and os.path.exists(os.path.join(cert_dir, "server.key")):
        print("Certificates already exist")
        return
    
    print("Generating certificates...")
    
    # Create cert directory if it doesn't exist
    cert_server_dir = os.path.join(repo_root, "cert.server")
    if not os.path.exists(cert_server_dir):
        os.makedirs(cert_server_dir)
    
    # Create a symbolic link for cert -> cert.server
    if os.path.exists(cert_dir) and not os.path.islink(cert_dir):
        os.rmdir(cert_dir)
    
    if not os.path.exists(cert_dir):
        # Create symbolic link (cross-platform)
        try:
            os.symlink(cert_server_dir, cert_dir, target_is_directory=True)
        except (OSError, AttributeError):
            # Fallback for Windows/systems without symlinks
            if not os.path.exists(cert_dir):
                os.makedirs(cert_dir)
    
    # Generate server config file
    config_file = os.path.join(cert_dir, "server.cnf")
    with open(config_file, "w") as f:
        f.write("""
# --- no modifications required below ---
[ req ]
default_bits = 2048
default_md = sha256
prompt = no
encrypt_key = no
distinguished_name = dn
req_extensions = req_ext

[ dn ]
C = AU
ST=Some-State
L=Sydney
O = Flatmax
OU=testing
emailAddress=flatmax@flatmax.org
CN = buildroot.deqxbox

[ req_ext ]
subjectAltName = DNS:buildroot.deqxbox
""")
    
    # Generate certificates using OpenSSL
    try:
        subprocess.run([
            "openssl", "req", "-newkey", "rsa:2048", "-new", "-nodes", 
            "-x509", "-days", "365", "-config", config_file,
            "-keyout", os.path.join(cert_dir, "server.key"),
            "-out", os.path.join(cert_dir, "server.crt")
        ], check=True)
        
        # Set permissions
        os.chmod(os.path.join(cert_dir, "server.key"), 0o600)
        
        print("Certificates generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {e}")
        print("Continuing without SSL...")
        return False
    except FileNotFoundError:
        print("OpenSSL not found. Continuing without SSL...")
        return False
    
    return True

class TestClass:
    """Test class with methods to expose over RPC."""
    
    def __init__(self):
        """Initialize test class."""
        self.test = 1
        self.i = 0
    
    def fn1(self, args):
        """Test function similar to JavaScript version."""
        print("this is fn1")
        print("got args")
        print(args)
        print(f"args={args}")
        return "this is fn1"
    
    def multi_client_test(self, jrpc_server):
        """Test function that calls methods on multiple clients."""
        print("multiClientTest : enter")
        
        try:
            # Define handler functions for each step
            def handle_uniqueFn1_result(res):
                if len(res) > 1:
                    raise Exception("Expected only one remote to be called")
                remote_id = list(res.keys())[0]
                value = list(res.values())[0]
                print(f"remote : {remote_id} returns {value}")
                return jrpc_server.call['TestClass.uniqueFn2'](value, 'hi there 2')
            
            def handle_uniqueFn2_result(res):
                if len(res) > 1:
                    raise Exception("Expected only one remote to be called")
                remote_id = list(res.keys())[0]
                value = list(res.values())[0]
                print(f"remote : {remote_id} returns {value}")
                return jrpc_server.call['TestClass.commonFn'](value, 'common Fn')
            
            def print_final_result(data):
                print("commonFn returns")
                print(data)
            
            def handle_error(e):
                print("multiClientTest : error ")
                print(e)
            
            # Start the promise chain
            jrpc_server.call['TestClass.uniqueFn1'](self.i, 'hi there 1').then(
                handle_uniqueFn1_result
            ).then(
                handle_uniqueFn2_result
            ).then(
                print_final_result
            ).catch(
                handle_error
            )
            
            self.i += 1
            
        except Exception as e:
            print(f"multiClientTest error: {e}")
    
if __name__ == "__main__":
    # Ensure certificates exist for SSL
    ssl_available = ensure_certificates_exist()
    
    # Create server on port 9000
    jrpc_server = JRPCServer(9000, use_ssl=ssl_available)
    
    # Create test class instance
    tc = TestClass()
    
    # Add the class to the server
    jrpc_server.add_class(tc)
    
    print("Starting JRPC server on port 9000")
    print(f"Using SSL: {ssl_available}")
    if ssl_available:
        print("Don't forget to open https://0.0.0.0:9000 in the browser to clear security issues")
        print("(We're using self-signed certificates for testing)")
    
    # Start the server
    server_thread = jrpc_server.start()
    
    # Run the multi-client test every second
    try:
        while True:
            tc.multi_client_test(jrpc_server)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped")
