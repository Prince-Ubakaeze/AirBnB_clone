#!/usr/bin/python3
"""User model."""

from models.base_model import BaseModel


class User(BaseModel):
    """Store a user's account details."""

    email = ""
    password = ""
    first_name = ""
    last_name = ""
