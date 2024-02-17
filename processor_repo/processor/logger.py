# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Utility functions for Kafka"""
import logging
import os

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
log.addHandler(ch)
