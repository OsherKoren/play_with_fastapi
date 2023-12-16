# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Sub-package for mocking external user of this service application"""

from . import authentication, kafka_consumer
from .authentication import get_current_user
from .kafka_consumer import consume_messages, set_consumer

__all__ = ["authentication", "kafka_consumer"]
