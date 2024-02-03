# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""This module is for setting and validating schemas for the API endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, confloat, conint, constr, field_validator, model_validator


# pylint: disable=too-few-public-methods
class MessageIn(BaseModel):
    """
    Represents incoming message data.

    Attributes:
        message (str): The message content.
        email (Optional[EmailStr]): The email associated with the message (optional).
        phone (Optional[str]): The phone number associated with the message (optional).

    Methods:
        email_or_phone_valid(cls, values):
        Validates that at least one of email or phone is specified.
    """

    message: str
    email: Optional[EmailStr] = None
    phone: Optional[constr(pattern=r'^\d{3}-\d{2}-\d{7}$')] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "I am intersting in getting a loan. Please contact me",
                    "email": "email@example.com",
                    "phone": "972-52-1234567",
                }
            ]
        }
    }

    @model_validator(mode="before")
    @classmethod
    def email_or_phone_valid(cls, values):
        """
        Validate that at least one of email or phone is specified.

        Args:
            values (dict): A dictionary of values containing 'email' and 'phone'.

        Raises:
            ValueError: If neither 'email' nor 'phone' is specified.
        """
        if "email" not in values and "phone" not in values:
            raise ValueError("At least one of email or phone must be specified")
        return values


# pylint: disable=too-few-public-methods
class MessageOut(MessageIn):
    """
    Represents outgoing message data with additional attributes.

    Attributes:
        message_id (int): The message ID.
        account_id: conint(ge=0, le=999999999999): The account ID.
    """

    message_id: int
    account_id: conint(ge=0, le=999999999999)


# pylint: disable=too-few-public-methods
class MessageScore(BaseModel):
    """
    Represents a message's score data.

    Attributes:
        message_id (int): The message ID.
        account_id: conint(ge=0, le=999999999999): The account ID.
        message (str): The message content.
        created_at (datetime): The timestamp when the message was created.
        score confloat(ge=0, le=1): The score associated with the message.

    Methods:
        score_valid(cls, value): Validates that the score is within the range [0, 1].
    """

    message_id: int
    account_id: conint(ge=0, le=999999999999)
    message: str
    created_at: datetime
    score: confloat(ge=0, le=1)
