# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This module is for querying the database tables
and running sql statements on the database tables.
"""

from .connection import database
from .tables_metadata import messages_predictions_table


async def add_message_score(message_id: int, score: float) -> int:
    """
    Inserts a new message score into the messages_predictions table.

    Args:
        message_id (int): The ID of the message associated with the score.
        score (float): The score to be associated with the message.

    Returns:
        int: The primary key ID of the newly inserted message score.
    """

    query = messages_predictions_table.insert().values(
        message_id=message_id, score=score
    )
    return await database.execute(query=query)
