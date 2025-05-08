"""
neapolitan_calculator.py

Implements NeapolitanCalculator, a subclass of PizzaCalculator,
specialized for Neapolitan-style dough using config-based yeast percentage lookup.
"""

from src.recipe import PizzaRecipe
from src.data import DataExtractor
from src.errors import ErrorMessages
from .calculator import PizzaCalculator


class NeapolitanCalculator(PizzaCalculator):
    """
    Calculator for Neapolitan-style pizza dough.

    Uses a data-driven approach to compute yeast percentage based on fermentation parameters.
    """

    @staticmethod
    def calculate_yeast_percentage(recipe: 'PizzaRecipe') -> float:
        """Calculate yeast percentage based on fermentation time and temperature."""
        data_extractor = DataExtractor()
        _get_duration_column = data_extractor.get_closest_duration_column

        NeapolitanCalculator._validate_fermentation_conditions(recipe)

        if recipe.room_fermentation == 0:
            duration_column = _get_duration_column(recipe.fridge_fermentation, recipe.fridge_temperature)
        elif recipe.fridge_fermentation == 0:
            duration_column = _get_duration_column(recipe.room_fermentation, recipe.room_temperature)
        else:
            duration_column = NeapolitanCalculator._get_combined_duration_column(recipe, data_extractor)

        return data_extractor.get_yeast_percentage(recipe.yeast_type, duration_column)

    @staticmethod
    def _validate_fermentation_conditions(recipe: 'PizzaRecipe'):
        """
        Validates that fermentation durations are consistent with specified temperatures.

        Raises:
            ValueError: If fermentation duration is set but temperature is missing.
        """
        if recipe.room_temperature == 0 and recipe.room_fermentation != 0:
            raise ValueError(ErrorMessages.MISMATCH_FERMENTATION.format("Room"))
        elif recipe.fridge_temperature == 0 and recipe.fridge_fermentation != 0:
            raise ValueError(ErrorMessages.MISMATCH_FERMENTATION.format("Fridge"))
        elif recipe.room_temperature == 0 and recipe.fridge_temperature == 0:
            raise ValueError(ErrorMessages.MISSING_TEMPERATURES)

    @staticmethod
    def _get_combined_duration_column(recipe: 'PizzaRecipe', data_extractor: 'DataExtractor') -> int:
        """
        Combines room and fridge fermentation durations to compute an effective column index.

        Args:
            recipe (PizzaRecipe): The recipe containing fermentation data.
            data_extractor (DataExtractor): Helper to extract yeast percentage data.

        Returns:
            int: Index of the column corresponding to the combined fermentation duration.

        Raises:
            ValueError: If the intermediate data is invalid or cannot be converted.
        """
        _get_duration_column = data_extractor.get_closest_duration_column

        room_duration_column = _get_duration_column(recipe.room_fermentation, recipe.room_temperature)
        temperature_row_index = data_extractor.get_temperature_row_index(recipe.fridge_temperature, strict=False)
        room_fermentation_value_at_fridge = data_extractor.get_cell_value(temperature_row_index, room_duration_column)

        try:
            room_fermentation_value_at_fridge = float(room_fermentation_value_at_fridge)
        except ValueError:
            raise ValueError(ErrorMessages.INVALID_FERMENTATION)

        combined_fermentation_duration = room_fermentation_value_at_fridge + recipe.fridge_fermentation
        return _get_duration_column(combined_fermentation_duration, recipe.fridge_temperature)
