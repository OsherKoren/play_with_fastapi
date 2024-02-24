# !/usr/bin/env python

"""Runs predictions on the messages in the database"""

import logging
import random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def predict_score(message: str | bytes) -> float:
    """
    Mock predictions on a message and return a random score.

    Args:
        message (str | bytes): The message for which to make a score prediction.

    Returns:
        float: A randomly generated score between 0 and 1.
    """
    score = random.random()  # Mock prediction model
    logger.info("Predicted score: %s for message %s", score, message)
    return score
