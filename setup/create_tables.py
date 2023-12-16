# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Setup module for creating the tables for the first time in the relevant database"""

import os
import sys

from sqlalchemy import MetaData, create_engine

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from setup.db import (DATABASE_URL, accounts_table, messages_predictions_table,
                      messages_table)

# Create an engine and metadata object
engine = create_engine(DATABASE_URL)
# Create a MetaData instance
metadata = MetaData(bind=engine)

# Include 'messages' table definitions in the metadata defined
metadata.create_all(
    bind=engine, tables=[accounts_table, messages_table, messages_predictions_table]
)


if __name__ == "__main__":
    # Create the tables in the database
    print("Creating tables...")
    metadata.create_all(engine)
    print("Tables created successfully.")
