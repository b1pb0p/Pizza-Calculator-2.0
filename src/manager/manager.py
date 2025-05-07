import json
import os

from datetime import datetime
from tkinter import filedialog, messagebox

from src.recipe import PizzaRecipe
from src.errors import ErrorMessages
from src.configuration import Configuration
from src.calculators import NeapolitanCalculator


class RecipeManager:
    """
    Manages saving, loading, and constructing pizza recipes using JSON or TXT formats.
    Supports interaction with GUI dialogs and calculator selection by pizza style.
    """

    @staticmethod
    def select_saving_path(file_extension):
        """
        Opens a dialog for the user to select a folder to save a file.
        Ensures a unique filename based on the current date.

        Args:
            file_extension (str): The desired file extension (e.g., ".json", ".txt").

        Returns:
            tuple: A tuple (file_path, base_filename) or (None, None) if canceled.
        """
        folder_path = filedialog.askdirectory(title=f"Choose Folder to Save Recipe output {file_extension}")
        if not folder_path:
            messagebox.showinfo("No Folder Selected", "No folder was selected.")
            return None, None

        os.makedirs(folder_path, exist_ok=True)

        base_filename = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(folder_path, f"{base_filename}{file_extension}")

        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(folder_path, f"{base_filename}_{counter}{file_extension}")
            counter += 1

        return file_path, base_filename

    @staticmethod
    def save_recipe_as_txt(recipe):
        """
        Saves a given recipe as a plain text file.

        Args:
            recipe (PizzaRecipe): The pizza recipe instance to save.
        """
        file_path, _ = RecipeManager.select_saving_path(".txt")

        if file_path is None:
            return None

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(recipe))

    @staticmethod
    def save_recipe_as_json(recipe):
        """
        Saves a given recipe as a JSON file with relevant attributes.

        Args:
            recipe (PizzaRecipe): The pizza recipe instance to save.
        """
        file_path, base_filename = RecipeManager.select_saving_path(".json")

        if file_path is None:
            return None

        data = {
            "info": f"{base_filename}",
            "base_recipe": {
                "pizza_style": "Neo-Neapolitan",
                "salt_percentage": recipe.salt_percentage,
                "oil_percentage": recipe.oil_percentage,
                "yeast_type": recipe.yeast_type,
                "hydration": recipe.hydration,
                "ball_weight": recipe.ball_weight,
                "number_of_balls": recipe.number_of_balls,
                "room_temperature": recipe.room_temperature,
                "room_fermentation": int(recipe.room_fermentation),
                "fridge_temperature": recipe.fridge_temperature,
                "fridge_fermentation": int(recipe.fridge_fermentation),
            }
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_recipe(use_default=False):
        """
        Loads a pizza recipe either from a file or from a default configuration.

        Args:
            use_default (bool): If True, loads the default recipe. Otherwise, opens a file dialog.

        Returns:
            PizzaRecipe or None: A constructed PizzaRecipe or None if loading fails.
        """
        if use_default:
            return RecipeManager._load_default_recipe()
        return RecipeManager._load_recipe_from_user_selection()

    @staticmethod
    def _load_default_recipe():
        """
        Loads the default recipe from configuration settings.

        Returns:
            PizzaRecipe: A recipe created from the default configuration.
        """
        configuration_file = Configuration()
        default_recipe = configuration_file.get_base_recipe()
        return RecipeManager.to_recipe(default_recipe)

    @staticmethod
    def _load_recipe_from_user_selection():
        """
        Prompts the user to select a JSON recipe file and loads it.

        Returns:
            PizzaRecipe or None: The loaded PizzaRecipe or None if cancelled or invalid.
        """
        recipe_path = filedialog.askopenfilename(
            title="Select Recipe File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not recipe_path:
            messagebox.showinfo("No File Selected", "No file was selected.")
            return None

        try:
            with open(recipe_path, 'r') as file:
                data = json.load(file)
                base = data.get('base_recipe', {})
                return RecipeManager.to_recipe(base)
        except Exception as e:
            messagebox.showerror("Error Loading Recipe", f"An error occurred: {e}")
            return None

    @staticmethod
    def get_pizza_calculator(pizza_style: str):
        """
        Returns the appropriate calculator class for a given pizza style.

        Args:
            pizza_style (str): The name of the pizza style.

        Returns:
            BaseCalculator: An instance of a calculator class for the specified style.

        Raises:
            ValueError: If no matching calculator is found.
        """
        calculators = {
            "Neo-Neapolitan": NeapolitanCalculator,
        }

        calculator_class = calculators.get(pizza_style)
        if not calculator_class:
            raise ValueError(ErrorMessages.NO_CALCULATOR_FOUND.format(pizza_style))

        return calculator_class()

    @staticmethod
    def to_recipe(base_recipe):
        """
        Constructs a PizzaRecipe from a base recipe dictionary.

        Args:
            base_recipe (dict): A dictionary with the necessary recipe parameters.

        Returns:
            PizzaRecipe: An instance of PizzaRecipe based on the given data.
        """
        calculator = RecipeManager.get_pizza_calculator(base_recipe["pizza_style"])
        return PizzaRecipe(calculator, base_recipe)
