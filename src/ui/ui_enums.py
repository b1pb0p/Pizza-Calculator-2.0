"""
ui_enums.py

Defines tag Enums for ingredients and proofing steps in the pizza recipe app.
"""

from enum import Enum


class IngredientType(Enum):
    """Tags for ingredients fields."""
    salt_percentage = "Salt (%)"
    oil_percentage = "Oil (%)"
    yeast_type = "Yeast Type"
    hydration = "Hydration (%)"
    number_of_balls = "Number of Balls"
    ball_weight = "Ball Weight (g)"


class ProofingType(Enum):
    """Proofing types"""
    room = {
        "temperature_label": "Room Proof temperature (°C)",
        "fermentation_label": "Room Proof Hours",
        "temperature": "room_temperature",
        "fermentation": "room_fermentation"
    }
    fridge = {
        "temperature_label": "Cold Proof temperature (°C)",
        "fermentation_label": "Cold Proof Hours",
        "temperature": "fridge_temperature",
        "fermentation": "fridge_fermentation"
    }


class ProofingMode(Enum):
    """Recipe proofing modes"""
    dual_proofing_mode = "Both"
    room_proofing_only_mode = "Room proof only"
    cold_proofing_only_mode = "Cold proof only"


def get_proofing_modes():
    """Returns the list of available proofing modes."""
    return [mode.value for mode in ProofingMode]
