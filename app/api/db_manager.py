# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This module is for querying the database tables
and running sql statements on the database tables.
"""

from typing import List, Optional

from databases.interfaces import Record

from .tables_metadata import (accounts_table, database, messages_predictions_table,
                                     messages_table)


async def get_all_messages() -> List[Record]:
    """
    Retrieves all messages from the messages table.

    Returns:
        List[Record]: A list of records, each representing a message.
    """
    query = messages_table.select()
    return await database.fetch_all(query=query)


async def get_account(account_id: int) -> Optional[Record]:
    """
    Retrieves a single account by its ID.

    Args:
        account_id (int): The ID of the account to retrieve.

    Returns:
        Optional[Record]: A record representing the account, or None if not found.
    """
    query = accounts_table.select(accounts_table.c.account_id == account_id)
    return await database.fetch_one(query=query)


async def get_message(msg_id: int) -> Optional[Record]:
    """
    Retrieves a single message by its ID.

    Args:
        msg_id (int): The ID of the message to retrieve.

    Returns:
        Optional[Record]: A record representing the message, or None if not found.
    """
    query = messages_table.select(messages_table.c.message_id == msg_id)
    return await database.fetch_one(query=query)


async def add_message(account_id: int, message: str) -> int:
    """
    Inserts a new message into the messages table.

    Args:
        account_id (int): The account ID associated with the message.
        message (str): The message text.

    Returns:
        int: The ID of the newly inserted message.
    """
    query = (
        messages_table.insert()
        .values(account_id=account_id, message=message)
        .returning(messages_table.c.message_id)
    )
    return await database.execute(query=query)


async def get_message_score(msg_id: int) -> Optional[Record]:
    """
    Retrieves the score of a specific message by its message ID.

    Args:
        msg_id (int): The ID of the message for which the score is to be retrieved.

    Returns:
        Optional[Record]: A record representing the message score, or None if not found.
    """
    query = messages_predictions_table.select(
        messages_predictions_table.c.message_id == msg_id
    )
    return await database.fetch_one(query=query)


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


async def get_all_scores() -> List[Record]:
    """
    Retrieve all scores from the messages_predictions_table.

    Returns:
        List[Record]: A list of records representing the scores.
    """
    query = messages_predictions_table.select()
    return await database.fetch_all(query=query)


async def get_high_scorers(threshold: float) -> List[Record]:
    """
    Retrieve records with scores equal to or greater than the specified threshold.

    Args:
        threshold (float): The minimum score threshold for filtering.

    Returns:
        List[Record]: A list of records representing the high scorers.
    """
    query = messages_predictions_table.select(
        messages_predictions_table.c.score >= threshold
    )
    return await database.fetch_all(query=query)
