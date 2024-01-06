# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Tests for the Messages API endpoints"""

import pytest


def test_root(test_app, base_url):
    """Test the get root endpoint"""
    response = test_app.get(f"{base_url}/messages")
    assert response.status_code == 200
    assert response.json() == "Messages Prediction Services"


@pytest.mark.anyio
async def test_root_async(async_test_app, base_url):
    """Test the get root endpoint - async"""
    endpoint = f"{base_url}/messages/"
    response = await async_test_app.get(endpoint)
    assert response.status_code == 200
    assert response.json() == "Messages Prediction Services"
