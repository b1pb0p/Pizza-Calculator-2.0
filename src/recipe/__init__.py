"""
The recipe package defines the structure and utilities for pizza recipes.

Modules:
- recipe.py: Core PizzaRecipe class encapsulating ingredient amounts and proofing details.
- utilities.py: Helper functions for recipe-related calculations and formatting.
"""

from .recipe import PizzaRecipe
from .utilities import auto_property
