#!/usr/bin/env python3
"""
Test 1: Client-to-Server RPC test client
"""
from jrpc_client import JRPCClient
import time

def run_calculator_tests():
    client = JRPCClient(port=8080)
    
    try:
        if client.connect():
            calc = client['Calculator']
            
            print("\nRunning Calculator Tests:")
            print("-" * 30)
            
            # Test addition
            result = calc.add(5, 3)
            print(f"Client received: 5 + 3 = {result}")
            assert result == 8, f"Addition failed: Expected 8, got {result}"
            
            # Test subtraction
            result = calc.subtract(10, 4)
            print(f"Client received: 10 - 4 = {result}")
            assert result == 6, f"Subtraction failed: Expected 6, got {result}"
            
            # Test multiplication
            result = calc.multiply(6, 7)
            print(f"Client received: 6 * 7 = {result}")
            assert result == 42, f"Multiplication failed: Expected 42, got {result}"
            
            print("\nAll calculator tests passed!")
            
    except Exception as e:
        print(f"Test error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    print("Test 1 - Starting Calculator Client...")
    run_calculator_tests()
