# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

from fastapi import FastAPI

from api import messages
from lifecycle import lifespan

# import logging
# from contextlib import asynccontextmanager
# import asyncio
# import os
# from aiokafka.admin import AIOKafkaAdminClient, NewTopic
# from aiokafka.errors import IncompatibleBrokerVersion, TopicAlreadyExistsError

app = FastAPI(title="Message Gateway App", version="1.0", lifespan=lifespan)

app.include_router(messages.health_router, prefix="/api/v1", tags=["health"])
app.include_router(messages.router, prefix="/api/v1", tags=["messages"])
