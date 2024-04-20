# !/usr/bin/env python

"""Runs predictions on the messages in the database"""

import random

from src.logger import log


def predict_score(message: str | bytes) -> float:
    """
    Mock predictions on a message and return a random score.

    Args:
        message (str | bytes): The message for which to make a score prediction.

    Returns:
        float: A randomly generated score between 0 and 1.
    """
    score = random.random()  # Mock prediction model
    log.info("Predicted score: %s for message %s", score, message)
    return score
