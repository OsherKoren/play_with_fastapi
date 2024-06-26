# !/usr/bin/env python

"""This module defines the tables in the database"""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    func,
)

metadata = MetaData()

accounts_table = Table(
    "accounts",
    metadata,
    Column("account_id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String(20)),
    Column("surname", String(20)),
    Column("email", String(50)),
    Column("phone", String(15)),
    Column("birthday", DateTime),
    Column("gender", String(10)),
)

messages_table = Table(
    "messages",
    metadata,
    Column("message_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "account_id", Integer, ForeignKey("accounts.account_id")
    ),  # ForeignKey reference to accounts
    Column("message", String(500)),
    Column("created_at", DateTime, default=func.now()),  # Automatic timestamp column
)

messages_predictions_table = Table(
    "messages_predictions",
    metadata,
    Column(
        "prediction_id", Integer, primary_key=True, autoincrement=True
    ),  # Unique ID for each prediction
    Column(
        "message_id", Integer, ForeignKey("messages.message_id"), unique=True
    ),  # ForeignKey reference to messages
    Column("score", Float),
    Column(
        "predicted_at", DateTime, default=func.now()
    ),  # Timestamp for when the prediction was made
)
