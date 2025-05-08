"""
calculators.py

Defines an abstract base class for calculating ingredient weights in a pizza dough recipe.
"""

from abc import ABC, abstractmethod
from src.recipe import PizzaRecipe


class PizzaCalculator(ABC):
    """
    Abstract base class for calculating ingredient weights based on a PizzaRecipe.

    Subclasses must implement `calculate_yeast_percentage` to define specific yeast logic.
    """

    @staticmethod
    def calculate_flour_weight(recipe: 'PizzaRecipe') -> float:
        """Calculates the flour weight based on the total dough weight and hydration percentages."""
        total_percentage = 1 + ((recipe.hydration + recipe.oil_percentage + recipe.salt_percentage) / 100)
        return (recipe.number_of_balls * recipe.ball_weight) / total_percentage

    @staticmethod
    def _calculate_ingredient_weight(recipe: 'PizzaRecipe', percentage: float) -> float:
        """Returns the weight of an ingredient given its percentage and flour weight."""
        return recipe.flour_weight * percentage / 100

    @staticmethod
    def calculate_water_weight(recipe: 'PizzaRecipe') -> float:
        """Returns the water weight based on hydration percentage."""
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.hydration)

    @staticmethod
    def calculate_oil_weight(recipe: 'PizzaRecipe') -> float:
        """Returns the oil weight based on oil percentage."""
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.oil_percentage)

    @staticmethod
    def calculate_salt_weight(recipe: 'PizzaRecipe') -> float:
        """Returns the salt weight based on salt percentage."""
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.salt_percentage)

    @staticmethod
    def calculate_yeast_weight(recipe: 'PizzaRecipe') -> float:
        """Returns the yeast weight based on yeast percentage."""
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.yeast_percentage)

    @staticmethod
    @abstractmethod
    def calculate_yeast_percentage(recipe: 'PizzaRecipe') -> float:
        """
        Calculates the appropriate yeast percentage for the given recipe.

        Subclasses must implement this method based on specific fermentation conditions.

        Args:
            recipe (PizzaRecipe): The pizza recipe instance.

        Returns:
            float: The calculated yeast percentage.
        """
        pass
