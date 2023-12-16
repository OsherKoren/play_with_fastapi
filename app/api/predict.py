# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Runs predictions on the messages in the database"""

import random


def predict_score(message: str) -> float:
    """
    Mock predictions on a message and return a random score.

    Args:
        message (str): The message for which to make a score prediction.

    Returns:
        float: A randomly generated score between 0 and 1.
    """
    score = random.random()
    print(f"Predicted score {score} for message {message}")
    return score
