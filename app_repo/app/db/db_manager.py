# !/usr/bin/env python

"""
This module is for querying the database tables
and running sql statements on the database tables.
"""

from typing import List, Optional

from databases.interfaces import Record
from sqlalchemy import join, select

from .connection import database
from .tables_metadata import accounts_table, messages_predictions_table, messages_table


async def get_all_messages() -> list[Record]:
    """
    Retrieves all messages from the messages table.

    Returns:
        List[Record]: A list of records, each representing a message.
    """
    query = select(
        [
            messages_table.c.message_id,
            messages_table.c.message,
            messages_table.c.created_at,
            accounts_table.c.account_id,
            accounts_table.c.first_name,
            accounts_table.c.surname,
            accounts_table.c.email,
            accounts_table.c.phone,
            accounts_table.c.birthday,
            accounts_table.c.gender,
        ]
    ).select_from(
        join(
            accounts_table,
            messages_table,
            messages_table.c.account_id == accounts_table.c.account_id,
        )
    )
    return await database.fetch_all(query=query)


async def get_account(account_id: int) -> Record | None:
    """
    Retrieves a single account by its ID.

    Args:
        account_id (int): The ID of the account to retrieve.

    Returns:
        Optional[Record]: A record representing the account, or None if not found.
    """
    query = accounts_table.select(accounts_table.c.account_id == account_id)
    return await database.fetch_one(query=query)


async def get_message(msg_id: int) -> Record | None:
    """
    Retrieves a single message by its ID.

    Args:
        msg_id (int): The ID of the message to retrieve.

    Returns:
        Optional[Record]: A record representing the message, or None if not found.
    """
    query = (
        select(
            [
                messages_table.c.message_id,
                messages_table.c.message,
                messages_table.c.created_at,
                accounts_table.c.account_id,
                accounts_table.c.first_name,
                accounts_table.c.surname,
                accounts_table.c.email,
                accounts_table.c.phone,
                accounts_table.c.birthday,
                accounts_table.c.gender,
            ]
        )
        .select_from(
            join(
                accounts_table,
                messages_table,
                messages_table.c.account_id == accounts_table.c.account_id,
            )
        )
        .where(messages_table.c.message_id == msg_id)
    )
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


async def get_message_score(msg_id: int) -> Record | None:
    """
    Retrieves the score of a specific message by its message ID.

    Args:
        msg_id (int): The ID of the message for which the score is to be retrieved.

    Returns:
        Optional[Record]: A record representing the message score, or None if not found.
    """
    query = (
        select(
            [
                messages_table.c.message_id,
                messages_table.c.message,
                messages_table.c.created_at,
                messages_predictions_table.c.score,
                messages_predictions_table.c.predicted_at,
                accounts_table.c.account_id,
                accounts_table.c.first_name,
                accounts_table.c.surname,
                accounts_table.c.email,
                accounts_table.c.phone,
                accounts_table.c.birthday,
                accounts_table.c.gender,
            ]
        )
        .select_from(
            join(
                accounts_table,
                join(
                    messages_table,
                    messages_predictions_table,
                    messages_table.c.message_id
                    == messages_predictions_table.c.message_id,
                ),
            )
        )
        .where(messages_table.c.message_id == msg_id)
    )
    return await database.fetch_one(query=query)


async def get_messages_scores() -> list[Record]:
    """
    Retrieves all messages with scores and account details.

    Returns:
        List[Record]: A list of records,
        each representing a message with scores and account details.
    """
    query = select(
        [
            messages_table.c.message_id,
            messages_table.c.message,
            messages_table.c.created_at,
            messages_predictions_table.c.score,
            messages_predictions_table.c.predicted_at,
            accounts_table.c.account_id,
            accounts_table.c.first_name,
            accounts_table.c.surname,
            accounts_table.c.email,
            accounts_table.c.phone,
            accounts_table.c.birthday,
            accounts_table.c.gender,
        ]
    ).select_from(
        join(
            accounts_table,
            join(
                messages_table,
                messages_predictions_table,
                messages_table.c.message_id == messages_predictions_table.c.message_id,
            ),
        )
    )
    return await database.fetch_all(query=query)


async def filter_messages_scores(threshold: float) -> list[Record]:
    """
    Retrieve records with scores equal to or greater than the specified threshold
    along with associated message and account details.

    Args:
        threshold (float): The minimum score threshold for filtering.

    Returns:
        List[Record]: A list of records representing high scorers with details.
    """
    query = (
        select(
            [
                messages_table.c.message_id,
                messages_table.c.message,
                messages_table.c.created_at,
                messages_predictions_table.c.score,
                messages_predictions_table.c.predicted_at,
                accounts_table.c.account_id,
                accounts_table.c.first_name,
                accounts_table.c.surname,
                accounts_table.c.email,
                accounts_table.c.phone,
                accounts_table.c.birthday,
                accounts_table.c.gender,
            ]
        )
        .select_from(
            join(
                accounts_table,
                join(
                    messages_table,
                    messages_predictions_table,
                    messages_table.c.message_id
                    == messages_predictions_table.c.message_id,
                ),
            )
        )
        .where(messages_predictions_table.c.score >= threshold)
    )
    return await database.fetch_all(query=query)
