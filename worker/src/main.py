# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

import os

from fastapi import FastAPI

from .lifecycle import lifespan

print("PYTHONPATH: ", os.environ.get("PYTHONPATH"))


app = FastAPI(title="Message worker App", version="1.0", lifespan=lifespan)
