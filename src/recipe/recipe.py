"""
recipe.py

This file contains the PizzaRecipe class, which manages the pizza recipe calculations
and properties such as flour weight, yeast percentage, and fermentation details.
"""

from .utilities import auto_property


class PizzaRecipe:
    """A class to manage pizza recipe."""

    salt_percentage = auto_property("salt_percentage", "recalculate_flour_weight")
    oil_percentage = auto_property("oil_percentage", "recalculate_flour_weight")
    hydration = auto_property("hydration", "recalculate_flour_weight")
    ball_weight = auto_property("ball_weight", "recalculate_flour_weight")
    number_of_balls = auto_property("number_of_balls", "recalculate_flour_weight")
    yeast_type = auto_property("yeast_type", "recalculate_yeast_percentage")

    room_temperature = auto_property("room_temperature", "recalculate_yeast_percentage")
    fridge_temperature = auto_property("fridge_temperature", "recalculate_yeast_percentage")
    room_fermentation = auto_property("room_fermentation", "recalculate_yeast_percentage")
    fridge_fermentation = auto_property("fridge_fermentation", "recalculate_yeast_percentage")

    def __init__(self, calculator, base_recipe):
        """
        Initializes the PizzaRecipe with values from the base recipe and a given calculator.

        Args:
            calculator (PizzaCalculator): The calculator for pizza style calculations.
            base_recipe (dict): The base recipe data containing ingredients and fermentation details.
        """
        self._calculator = calculator

        self._salt_percentage = base_recipe['salt_percentage']
        self._oil_percentage = base_recipe['oil_percentage']
        self._hydration = base_recipe['hydration']
        self._ball_weight = base_recipe['ball_weight']
        self._number_of_balls = base_recipe['number_of_balls']
        self._yeast_type = base_recipe['yeast_type']
        self._room_temperature = base_recipe['room_temperature']
        self._fridge_temperature = base_recipe['fridge_temperature']
        self._room_fermentation = base_recipe['room_fermentation']
        self._fridge_fermentation = base_recipe['fridge_fermentation']

        self._flour_weight = None
        self._yeast_percentage = None

        self.recalculate_flour_weight()
        self.recalculate_yeast_percentage()

    def recalculate_flour_weight(self):
        """
        Recalculates the flour weight using the provided calculator.

        This method updates the `_flour_weight` attribute.
        """
        self._flour_weight = self._calculator.calculate_flour_weight(self)

    def recalculate_yeast_percentage(self):
        """
        Recalculates the yeast percentage using the provided calculator.

        This method updates the `_yeast_percentage` attribute.
        """
        self._yeast_percentage = self._calculator.calculate_yeast_percentage(self)

    @property
    def pizza_style_calculator(self):
        """Returns the calculator instance used for the pizza style."""
        return self._calculator

    @property
    def flour_weight(self):
        """Returns the calculated flour weight."""
        return self._flour_weight

    @property
    def yeast_percentage(self):
        """Returns the calculated yeast percentage."""
        return self._yeast_percentage

    def _format_yeast(self):
        """
        Formats the yeast weight to a string with appropriate precision.

        Returns:
            str: The formatted yeast weight as a string.
        """
        formatted = f"{self._calculator.calculate_yeast_weight(self):.3f}".rstrip("0").rstrip(".")
        if "." not in formatted:
            formatted += ".0"
        return formatted

    def __str__(self):
        """
        Returns a string representation of the pizza recipe, including all relevant details.

        Returns:
            str: The string representation of the recipe.
        """
        parts = [
            f"Flour: {round(self._flour_weight)}g",
            f"Water: {round(self._calculator.calculate_water_weight(self))}g",
            f"Salt: {round(self._calculator.calculate_salt_weight(self))}g",
            f"Oil: {round(self._calculator.calculate_oil_weight(self))}g",
            f"Yeast: {self._format_yeast()}g of {self._yeast_type}"
        ]

        if self._fridge_fermentation and self._fridge_temperature:
            parts.append(
                f"Cold Proof: {round(self._fridge_fermentation)} hours at {self._fridge_temperature:.1f}°C"
            )

        if self._room_fermentation and self._room_temperature:
            parts.append(
                f"Room Proof: {round(self._room_fermentation)} hours at {self._room_temperature:.1f}°C"
            )

        parts.append(
            f"Total: {self._number_of_balls} dough balls, each weighing {self._ball_weight}g"
        )

        return "\n".join(parts)
