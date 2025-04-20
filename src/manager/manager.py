import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from src.recipe.recipe import PizzaRecipe
from src.errors.error_messages import ErrorMessages
from src.configuration.configuration import Configuration
from src.calculators.neapolitan_calculator import NeapolitanCalculator


class RecipeManager:

    @staticmethod
    def select_saving_path(file_extension):
        folder_path = filedialog.askdirectory(title=f"Choose Folder to Save Recipe output {file_extension}")
        if not folder_path:
            return

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
        file_path, _ = RecipeManager.select_saving_path(".txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(recipe))

    @staticmethod
    def save_recipe_as_json(recipe):
        file_path, base_filename = RecipeManager.select_saving_path(".json")

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
                "room_fermentation": recipe.room_fermentation,
                "fridge_temperature": recipe.fridge_temperature,
                "fridge_fermentation": recipe.fridge_fermentation,
            }
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_recipe(use_default=False):
        if use_default:
            return RecipeManager._load_default_recipe()
        return RecipeManager._load_recipe_from_user_selection()

    @staticmethod
    def _load_default_recipe():
        configuration_file = Configuration()
        default_recipe = configuration_file.get_base_recipe()
        return RecipeManager.to_recipe(default_recipe)

    @staticmethod
    def _load_recipe_from_user_selection():
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
        calculators = {
            "Neo-Neapolitan": NeapolitanCalculator,
        }

        calculator_class = calculators.get(pizza_style)
        if not calculator_class:
            raise ValueError(ErrorMessages.NO_CALCULATOR_FOUND.format(pizza_style))

        return calculator_class()

    @staticmethod
    def to_recipe(base_recipe):
        calculator = RecipeManager.get_pizza_calculator(base_recipe["pizza_style"])
        return PizzaRecipe(calculator, base_recipe)
