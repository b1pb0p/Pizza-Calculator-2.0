import dearpygui.dearpygui as dpg
from src.ui.widgets import WidgetHandler
from src.manager.manager import RecipeManager


class Ui:
    def __init__(self, recipe=None):
        dpg.create_context()

        if recipe is None:
            recipe = RecipeManager.load_recipe(use_default=True)

        self._recipe = recipe

        self._widget_handler = WidgetHandler(self._recipe)
        self._widget_handler.create_viewport()
        self._widget_handler.create_menu_buttons()
        self._build_main_ui()
        self._widget_handler.show_viewport()

    def _build_main_ui(self):
        with dpg.window(label="Pizza Recipe", tag="Primary Window", collapsed=False, autosize=False):
            self._widget_handler.load_main_input_header()
            self._widget_handler.load_input_widgets()

            dpg.add_separator()

            self._widget_handler.load_proofing_modes_widget()
            self._widget_handler.load_proofing_widgets()

            dpg.add_separator()

            self._widget_handler.load_instructions_header()
            self._widget_handler.load_output_section(self._load_callback)

    def _load_callback(self):
        self._recipe = RecipeManager.load_recipe()
        self._widget_handler = WidgetHandler(self._recipe)
        dpg.delete_item("Primary Window")
        self._build_main_ui()
