"""
Pytest configuration and fixtures for JRPC tests.
"""
import pytest
import asyncio
import sys
import os

# Ensure the parent package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def jrpc2_instance():
    """Create a fresh JRPC2 instance for testing."""
    from jrpc_oo.JRPC2 import JRPC2
    return JRPC2()


@pytest.fixture
def expose_class_instance():
    """Create a fresh ExposeClass instance for testing."""
    from jrpc_oo.ExposeClass import ExposeClass
    return ExposeClass()
