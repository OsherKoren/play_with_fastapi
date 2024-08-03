# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

import os

from fastapi import FastAPI

from .kafka import consumer
from .lifecycle import lifespan

print("PYTHONPATH: ", os.environ.get("PYTHONPATH"))

task = consumer.start_workers()

app = FastAPI(title="Message worker App", version="0.1.0", lifespan=lifespan)
