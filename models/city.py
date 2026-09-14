#!/usr/bin/python3
"""City model."""

from models.base_model import BaseModel


class City(BaseModel):
    """Store a city's name and the ID of its state."""

    state_id = ""
    name = ""
