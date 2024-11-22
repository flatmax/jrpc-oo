#!/usr/bin/env python3
"""
Example JSON-RPC client using Calculator service
"""
import asyncio
from jrpc_client import JRPCClient


async def main():
    client = JRPCClient()
    try:
        # Access Calculator methods using dictionary style
        calc = client['Calculator']
        
        a, b = 5, 3
        result = await calc.add(a, b)
        print(f"add({a}, {b}) = {{'1': {result}}}")
        
        a, b = 10, 4
        result = await calc.subtract(a, b)
        print(f"subtract({a}, {b}) = {{'2': {result}}}")
        
        a, b = 6, 7
        result = await calc.multiply(a, b)
        print(f"multiply({a}, {b}) = {{'3': {result}}}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
