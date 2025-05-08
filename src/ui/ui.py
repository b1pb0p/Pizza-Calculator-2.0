"""
ui.py

This file contains the Ui class, which acts as the main UI controller for the Pizza Recipe
application using DearPyGUI. It initializes and builds the interface, loads recipes,
and connects GUI components through the WidgetHandler class.
"""

import dearpygui.dearpygui as dpg

from .widgets import WidgetHandler
from src.manager import RecipeManager


class Ui:
    """
    Main UI controller for the Pizza Recipe application using DearPyGUI.
    Initializes and builds the interface, loads recipes, and connects the GUI components
    through the WidgetHandler class.
    """

    def __init__(self, recipe=None):
        """
        Initializes the UI context and loads the recipe (default or given).
        Constructs the main window and interface elements.

        Args:
            recipe (PizzaRecipe, optional): Recipe object to initialize the UI with. If None, loads the default recipe.
        """
        dpg.create_context()

        if recipe is None:
            recipe = RecipeManager.load_recipe(use_default=True)

        self._widget_handler = WidgetHandler(recipe)
        self._widget_handler.create_viewport()
        self._widget_handler.create_menu_buttons()
        self._build_main_ui()
        self._widget_handler.show_viewport()

    def _build_main_ui(self):
        """Constructs the main window and populates it with all UI components."""
        with dpg.window(label="Pizza Recipe", tag="Primary Window", collapsed=False, autosize=False):
            self._widget_handler.load_main_input_header()
            self._widget_handler.load_input_widgets()

            dpg.add_separator()

            self._widget_handler.load_proofing_modes_widget()
            self._widget_handler.load_proofing_widgets()

            dpg.add_separator()

            self._widget_handler.load_instructions_header()
            self._widget_handler.load_output_section()
