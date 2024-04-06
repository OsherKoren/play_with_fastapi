# !/usr/bin/env python

"""This module defines the relevant table in the database"""


from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    func,
)

metadata = MetaData()


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
