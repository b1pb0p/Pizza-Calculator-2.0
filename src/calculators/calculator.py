"""
calculators.py
This file contains the pizza calculators base class with methods to calculate ingredient weights.
"""

from abc import ABC, abstractmethod
from src.recipe.recipe import PizzaRecipe


class PizzaCalculator(ABC):
    """
    Abstract base class responsible for calculating ingredient weights
    for a given PizzaRecipe instance. Subclasses must implement yeast weight logic.
    """

    @staticmethod
    def calculate_flour_weight(recipe: 'PizzaRecipe') -> float:
        """
        Calculates the flour weight based on the desired dough ball weight and number of balls.
        The method accounts for the percentage of hydration, oil, and salt.

        :param recipe: PizzaRecipe object containing hydration, oil, salt percentages, and dough info.
        :return: Calculated flour weight in grams.
        """
        total_percentage = 1 + ((recipe.hydration + recipe.oil_percentage + recipe.salt_percentage) / 100)
        return (recipe.number_of_balls * recipe.ball_weight) / total_percentage

    @staticmethod
    def _calculate_ingredient_weight(recipe: 'PizzaRecipe', percentage: float) -> float:
        """
        Core utility method to calculate an ingredient's weight based on flour weight and a given percentage.

        This is used internally by specific ingredient calculation methods such as water, oil, salt, and yeast.

        :param recipe: PizzaRecipe object that contains the flour weight
        :param percentage: The percentage (hydration, oil, salt, or yeast) to apply to the flour weight.
        :return: Calculated weight in grams.
        """
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
        Abstract method to calculate the yeast weight based on the recipe's fermentation
        conditions and flour weight. This must be implemented by subclasses depending
        on the yeast type and proofing time/temperature.

        :param recipe: PizzaRecipe object containing flour weight and fermentation details.
        :return: Calculated yeast weight in grams.
        """
        pass
