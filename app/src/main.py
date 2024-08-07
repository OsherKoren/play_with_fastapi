# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

from fastapi import FastAPI

from .api import messages
from .lifecycle import lifespan

app = FastAPI(title="Message Gateway App", version="0.1.0", lifespan=lifespan)

app.include_router(messages.health_router, prefix="/api/v1", tags=["health"])
app.include_router(messages.router, prefix="/api/v1", tags=["messages"])
