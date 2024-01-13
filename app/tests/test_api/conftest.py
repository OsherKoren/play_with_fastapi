# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""pytest fixtures for the Messages API endpoints tests"""

import pytest
from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app
from app.db.tables_metadata import database

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture
def test_app(scope="session"):
    with TestClient(app) as client:
        print("Client is ready for testing - sync way")
        yield client

@pytest.fixture(scope="session")
async def async_test_app(anyio_backend, base_url):
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url=base_url) as async_client:
            print("Async Client is ready for testing")
            yield async_client


@pytest.fixture(scope="session")
