# !/usr/bin/env python

"""pytest fixtures for the Messages API endpoints tests"""

import pytest
from httpx import AsyncClient
from src import main

BASE_URL = "http://localhost:8000/api/v1"


pytest_plugins = ["tests.test_api.setup_messages"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
async def async_test_app(anyio_backend, base_url):
    """Create an AsyncAPI test client"""
    async with AsyncClient(app=main.app, base_url=base_url) as async_client:
        print("Async Client is ready for testing")
        yield async_client
