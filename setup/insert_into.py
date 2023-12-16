# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Setup module for inserting sample data into the accounts table."""

import json
import os
import sys
from datetime import datetime
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as SQLAlchemySession

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from setup.db import DATABASE_URL, accounts_table

# Creating an engine
engine = create_engine(DATABASE_URL)
Session = SQLAlchemySession(bind=engine)
session = Session()

# Read data from JSON file
with open("accounts.json", "r", encoding="utf-8") as file:
    accounts_data = json.load(file)

# Convert string dates to datetime objects
for account in accounts_data:
    account["birthday"] = datetime.strptime(account["birthday"], "%Y-%m-%d")


def insert_accounts(session: SQLAlchemySession, accounts_data: List[dict]) -> None:
    """
    Insert data into the accounts table.

    Args:
        session (Session): SQLAlchemy session object.
        accounts_data (List[dict]): List of dictionaries representing account data to be inserted.

    Returns:
        None
    """
    print("Inserting accounts...")
    for account in accounts_data:
        insert_stmt = accounts_table.insert().values(**account)
        session.execute(insert_stmt)
    session.commit()
    print("Accounts inserted successfully.")


if __name__ == "__main__":
    insert_accounts(session, accounts_data)
