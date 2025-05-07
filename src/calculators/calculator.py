"""
calculators.py

Defines the abstract base class for pizza dough ingredient calculations.
Provides utility methods to calculate ingredient weights like flour, water, salt, oil, and yeast.
"""

from abc import ABC, abstractmethod
from src.recipe import PizzaRecipe


class PizzaCalculator(ABC):
    """
    Abstract base class for calculating ingredient weights based on a PizzaRecipe.
    Subclasses must implement their own yeast percentage calculation logic.
    """

    @staticmethod
    def calculate_flour_weight(recipe: 'PizzaRecipe') -> float:
        total_percentage = 1 + ((recipe.hydration + recipe.oil_percentage + recipe.salt_percentage) / 100)
        return (recipe.number_of_balls * recipe.ball_weight) / total_percentage

    @staticmethod
    def _calculate_ingredient_weight(recipe: 'PizzaRecipe', percentage: float) -> float:
        return recipe.flour_weight * percentage / 100

    @staticmethod
    def calculate_water_weight(recipe: 'PizzaRecipe') -> float:
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.hydration)

    @staticmethod
    def calculate_oil_weight(recipe: 'PizzaRecipe') -> float:
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.oil_percentage)

    @staticmethod
    def calculate_salt_weight(recipe: 'PizzaRecipe') -> float:
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.salt_percentage)

    @staticmethod
    def calculate_yeast_weight(recipe: 'PizzaRecipe') -> float:
        return PizzaCalculator._calculate_ingredient_weight(recipe, recipe.yeast_percentage)

    @staticmethod
    @abstractmethod
    def calculate_yeast_percentage(recipe: 'PizzaRecipe') -> float:
        """
        Must be implemented by subclasses to return a suitable yeast percentage
        based on the fermentation conditions.
        """
        pass
