from src.recipe.recipe import PizzaRecipe
from src.data.data_extractor import DataExtractor
from src.errors.error_messages import ErrorMessages
from src.calculators.calculator import PizzaCalculator


class NeapolitanCalculator(PizzaCalculator):
    """
    A calculators for Neapolitan-style pizza dough that determines ingredient proportions,
    particularly the yeast percentage, based on temperature and fermentation durations.

    This calculator uses a configuration file containing yeast percentage mappings based on
    specific room and fridge fermentation settings. It extracts the closest matching values
    to calculate the appropriate amount of yeast.
    """

    @staticmethod
    def calculate_yeast_percentage(recipe: 'PizzaRecipe') -> float:
        """
        Calculate the yeast percentage needed for the recipe based on room and fridge
        fermentation temperature and duration using a pre-defined configuration file.

        The process involves:
        - Finding the temperature row index for both room and fridge fermentation.
        - Finding the closest duration column for room fermentation.
        - Adding fridge fermentation time to the corresponding room fermentation value.
        - Using this combined time to get the appropriate column for fridge fermentation.
        - Finally, retrieving the yeast percentage based on yeast type and the determined column.

        :param recipe: PizzaRecipe instance containing all required parameters.
        :return: Yeast percentage as a float.
        """
        data_extractor = DataExtractor()
        _get_duration_column = data_extractor.get_closest_duration_column

        NeapolitanCalculator._validate_fermentation_conditions(recipe)

        if recipe.room_fermentation == 0:
            duration_column = _get_duration_column(recipe.fridge_fermentation, recipe.fridge_temperature)
        elif recipe.fridge_fermentation == 0:
            duration_column = _get_duration_column(recipe.room_fermentation, recipe.room_temperature)
        else:
            duration_column = NeapolitanCalculator._get_combined_duration(recipe, data_extractor)

        return float(data_extractor.get_yeast_percentage(recipe.yeast_type, duration_column))

    @staticmethod
    def _validate_fermentation_conditions(recipe):
        """Validate the temperature and duration combination for proofing/fermentation."""
        if recipe.room_temperature == 0 and recipe.room_fermentation != 0:
            raise ValueError(ErrorMessages.MISMATCH_FERMENTATION.format("Room"))
        elif recipe.fridge_temperature == 0 and recipe.fridge_fermentation != 0:
            raise ValueError(ErrorMessages.MISMATCH_FERMENTATION.format("Fridge"))
        elif recipe.room_temperature == 0 and recipe.fridge_temperature == 0:
            raise ValueError(ErrorMessages.MISSING_TEMPERATURES)

    @staticmethod
    def _get_combined_duration(recipe, data_extractor):
        """Handle case where both room and fridge fermentation durations are provided."""
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
