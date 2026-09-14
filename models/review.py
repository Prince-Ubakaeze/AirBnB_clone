#!/usr/bin/python3
"""Review model."""

from models.base_model import BaseModel


class Review(BaseModel):
    """Store a user's written review of a place."""

    place_id = ""
    user_id = ""
    text = ""
