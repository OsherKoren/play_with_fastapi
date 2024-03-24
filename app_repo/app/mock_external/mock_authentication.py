# !/usr/bin/env python

"""This module mocks authentication and authorization. Not implemented yet in this project."""

import random

from databases.interfaces import Record

from app.db import db_manager


async def get_current_user() -> Record | None:
    """
    Retrieves a mock current user.

    This function simulates retrieving the current user by randomly selecting an account
    and returning it. It's a mock implementation for demonstration purposes.

    Returns:
        The randomly selected account object.
    """

    random_account = random.randint(1, 5)
    return await db_manager.get_account(account_id=random_account)
