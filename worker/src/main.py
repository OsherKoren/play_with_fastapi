# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

from fastapi import FastAPI
from src.lifecycle import lifespan

app = FastAPI(title="Message worker App", version="1.0", lifespan=lifespan)
