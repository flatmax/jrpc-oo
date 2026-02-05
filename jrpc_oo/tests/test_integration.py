"""
Integration tests for JRPC Python implementation.
Tests Python server with Python client communication.
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jrpc_oo.JRPCServer import JRPCServer
from jrpc_oo.JRPCClient import JRPCClient


class ServerTestClass:
    """Test class exposed by the server."""
    
    def __init__(self):
        self.call_count = 0
    
    def echo(self, message):
        """Echo back the message."""
        return f"echo: {message}"
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def increment_counter(self):
        """Increment and return counter."""
        self.call_count += 1
        return self.call_count
    
    async def async_multiply(self, a, b):
        """Async method that multiplies two numbers."""
        await asyncio.sleep(0.01)
        return a * b


class ClientTestClass:
    """Test class exposed by the client."""
    
    def client_info(self):
        """Return client information."""
        return {"client": "python", "version": "1.0"}
    
    def reverse_string(self, s):
        """Reverse a string."""
        return s[::-1]


@pytest.fixture
async def server():
    """Create and start a test server."""
    server = JRPCServer(port=19100)
    test_class = ServerTestClass()
    server.add_class(test_class, "TestClass")
    await server.start()
    yield server
    await server.stop()


@pytest.fixture
async def client(server):
    """Create a client connected to the test server."""
    client = JRPCClient("ws://127.0.0.1:19100")
    client_class = ClientTestClass()
    client.add_class(client_class, "ClientClass")
    
    # Start connection in background task
    connect_task = asyncio.create_task(client.connect())
    
    # Wait for connection and setup
    for _ in range(50):  # 5 second timeout
        await asyncio.sleep(0.1)
        if client.connected and client.server:
            break
    
    yield client
    
    # Cleanup
    await client.disconnect()
    connect_task.cancel()
    try:
        await connect_task
    except asyncio.CancelledError:
        pass


class TestServerClientConnection:
    """Tests for basic server-client connectivity."""
    
    @pytest.mark.asyncio
    async def test_client_connects_to_server(self, server):
        """T4.1: Client should successfully connect to server."""
        client = JRPCClient("ws://127.0.0.1:19100")
        
        connect_task = asyncio.create_task(client.connect())
        
        # Wait for connection
        for _ in range(50):
            await asyncio.sleep(0.1)
            if client.connected:
                break
        
        assert client.connected, "Client should be connected"
        
        await client.disconnect()
        connect_task.cancel()
        try:
            await connect_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_system_list_components_exchanged(self, server):
        """T4.1: system.listComponents should be exchanged on connect."""
        client = JRPCClient("ws://127.0.0.1:19100")
        client_class = ClientTestClass()
        client.add_class(client_class, "ClientClass")
        
        connect_task = asyncio.create_task(client.connect())
        
        # Wait for setup to complete
        for _ in range(50):
            await asyncio.sleep(0.1)
            if client.server and 'TestClass.echo' in client.server:
                break
        
        # Client should have server's methods available
        assert 'TestClass.echo' in client.server, "Client should know server methods"
        assert 'TestClass.add' in client.server, "Client should know server methods"
        
        await client.disconnect()
        connect_task.cancel()
        try:
            await connect_task
        except asyncio.CancelledError:
            pass


class TestClientCallsServer:
    """Tests for client calling server methods."""
    
    @pytest.mark.asyncio
    async def test_client_calls_server_echo(self, client):
        """T4.2: Client should be able to call server method."""
        result = await client.server['TestClass.echo']("hello")
        assert result == "echo: hello", "Echo should return correct result"
    
    @pytest.mark.asyncio
    async def test_client_calls_server_add(self, client):
        """Client can call server method with multiple args."""
        result = await client.server['TestClass.add'](10, 20)
        assert result == 30, "Add should return correct sum"
    
    @pytest.mark.asyncio
    async def test_client_calls_server_async_method(self, client):
        """Client can call async server methods."""
        result = await client.server['TestClass.async_multiply'](6, 7)
        assert result == 42, "Async multiply should return correct product"
    
    @pytest.mark.asyncio
    async def test_client_calls_server_stateful_method(self, client):
        """Client calls to stateful methods work correctly."""
        result1 = await client.server['TestClass.increment_counter']()
        result2 = await client.server['TestClass.increment_counter']()
        
        assert result1 == 1, "First call should return 1"
        assert result2 == 2, "Second call should return 2"


class TestServerCallsClient:
    """Tests for server calling client methods."""
    
    @pytest.mark.asyncio
    async def test_server_calls_client_method(self, server, client):
        """T4.3: Server should be able to call client method."""
        # Wait for server to have client's methods
        for _ in range(50):
            await asyncio.sleep(0.1)
            if server.call and 'ClientClass.client_info' in server.call:
                break
        
        assert 'ClientClass.client_info' in server.call, "Server should know client methods"
        
        results = await server.call['ClientClass.client_info']()
        
        # Results is a dict of {uuid: result}
        assert len(results) == 1, "Should have one client"
        result = list(results.values())[0]
        assert result['client'] == 'python', "Client info should be correct"
    
    @pytest.mark.asyncio
    async def test_server_calls_client_with_args(self, server, client):
        """Server can call client method with arguments."""
        # Wait for server to have client's methods
        for _ in range(50):
            await asyncio.sleep(0.1)
            if server.call and 'ClientClass.reverse_string' in server.call:
                break
        
        results = await server.call['ClientClass.reverse_string']("hello")
        
        result = list(results.values())[0]
        assert result == "olleh", "Reverse string should work"


class TestClientDisconnect:
    """Tests for client disconnection handling."""
    
    @pytest.mark.asyncio
    async def test_client_removed_from_remotes_on_disconnect(self, server):
        """T4.5: Disconnected client should be removed from remotes."""
        client = JRPCClient("ws://127.0.0.1:19100")
        client_class = ClientTestClass()
        client.add_class(client_class, "ClientClass")
        
        connect_task = asyncio.create_task(client.connect())
        
        # Wait for connection
        for _ in range(50):
            await asyncio.sleep(0.1)
            if client.connected and len(server.remotes) > 0:
                break
        
        assert len(server.remotes) == 1, "Server should have one remote"
        
        # Disconnect
        await client.disconnect()
        connect_task.cancel()
        try:
            await connect_task
        except asyncio.CancelledError:
            pass
        
        # Give server time to process disconnect
        await asyncio.sleep(0.2)
        
        assert len(server.remotes) == 0, "Server should have no remotes after disconnect"


class TestMultipleClients:
    """Tests for multiple simultaneous clients."""
    
    @pytest.mark.asyncio
    async def test_multiple_clients_connect(self, server):
        """T4.4: Multiple clients can connect to server."""
        clients = []
        tasks = []
        
        for i in range(3):
            client = JRPCClient("ws://127.0.0.1:19100")
            
            class DynamicClientClass:
                def __init__(self, idx):
                    self.idx = idx
                
                def get_id(self):
                    return self.idx
            
            client.add_class(DynamicClientClass(i), f"Client{i}")
            clients.append(client)
            tasks.append(asyncio.create_task(client.connect()))
        
        # Wait for all connections
        for _ in range(50):
            await asyncio.sleep(0.1)
            connected_count = sum(1 for c in clients if c.connected)
            if connected_count == 3:
                break
        
        assert len(server.remotes) == 3, "Server should have 3 remotes"
        
        # Cleanup
        for client in clients:
            await client.disconnect()
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_call_reaches_all_clients(self, server):
        """T4.4: call[fn] should reach all clients with that method."""
        clients = []
        tasks = []
        
        # Create clients with a common method
        for i in range(2):
            client = JRPCClient("ws://127.0.0.1:19100")
            
            class CommonClient:
                def __init__(self, idx):
                    self.idx = idx
                
                def common_method(self):
                    return f"client_{self.idx}"
            
            client.add_class(CommonClient(i), "CommonClient")
            clients.append(client)
            tasks.append(asyncio.create_task(client.connect()))
        
        # Wait for all connections and setup
        for _ in range(50):
            await asyncio.sleep(0.1)
            if (len(server.remotes) == 2 and 
                server.call and 
                'CommonClient.common_method' in server.call):
                break
        
        # Call common method - should reach both clients
        results = await server.call['CommonClient.common_method']()
        
        assert len(results) == 2, "Should have results from both clients"
        values = list(results.values())
        assert 'client_0' in values, "Should have result from client 0"
        assert 'client_1' in values, "Should have result from client 1"
        
        # Cleanup
        for client in clients:
            await client.disconnect()
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


class TestConcurrentCalls:
    """Tests for concurrent RPC calls."""
    
    @pytest.mark.asyncio
    async def test_concurrent_calls_to_server(self, client):
        """T4.6: Multiple simultaneous calls should all return correctly."""
        # Make 10 concurrent calls
        tasks = [
            client.server['TestClass.add'](i, i * 2)
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        expected = [i + i * 2 for i in range(10)]
        assert results == expected, "All concurrent calls should return correct results"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
