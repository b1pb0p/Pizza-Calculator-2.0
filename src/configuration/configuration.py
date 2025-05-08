"""
configuration.py

Singleton Configuration class for loading and managing settings from JSON files.
Provides centralized access to yeast parameters, UI layout, fonts, icons, and viewport settings.
"""

import json
from pathlib import Path


class Configuration:
    """Loads and exposes config data for recipe logic and UI layout."""

    _instance = None
    _ROOT = Path(__file__).resolve()
    _ASSETS_ROOT = _ROOT.parents[2] / "assets"
    _RELATIVE_ROOT = _ROOT.parents[0]
    _PIZZA_CONFIGURATION_PATH = rf"neapolitan_config.json"
    _UI_CONFIGURATION_PATH = rf"ui_config.json"

    def __new__(cls):
        """Ensures that only one instance of Configuration exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initializes configuration data from JSON files if not already initialized."""
        if self._initialized:
            return

        self._pizza_data = self._load_config(self._PIZZA_CONFIGURATION_PATH)
        self._ui_data = self._load_config(self._UI_CONFIGURATION_PATH)

        self._yeast_table_parameters = self._pizza_data["yeast_table_parameters"]
        self._base_recipe = self._pizza_data["base_recipe"]

        self._fonts_data = self._ui_data["fonts"]
        self._icons_data = self._ui_data["icons"]
        self._viewport_data = self._ui_data["viewport"]

        self._initialized = True

    def _load_config(self, configuration_path):
        """
        Load a JSON config file and return its data.

        Args:
            configuration_path (str): Relative path to the JSON config file.

        Returns:
            dict: Parsed configuration data.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = self._RELATIVE_ROOT / configuration_path
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_yeast_table_filename(self):
        """Returns the filename of the yeast table."""
        return self._yeast_table_parameters["yeast_table_filename"]

    def get_yeast_table_filepath(self):
        """Returns the full path to the yeast table file."""
        return Path(__file__).parent.parent / rf"data\{self.get_yeast_table_filename()}"

    def get_yeast_types(self):
        """Returns the list of yeast types."""
        return self._yeast_table_parameters["yeast_types"]

    def get_temperature_column(self):
        """Returns the name of the temperature column in the yeast table."""
        return self._yeast_table_parameters["temperature_column"]

    def get_selective_temperature_row_range(self):
        """Returns the lower and upper bounds for the temperature row range."""
        return (
            self._yeast_table_parameters["lower_range_temperature_row"],
            self._yeast_table_parameters["upper_range_temperature_row"]
        )

    def get_duration_column_range(self):
        """Returns the range of duration column indices."""
        return (
            self._yeast_table_parameters["first_duration_column"],
            self._yeast_table_parameters["last_duration_column"]
        )

    def get_base_recipe(self):
        """Returns the base pizza recipe dictionary."""
        return self._base_recipe

    def get_base_recipe_value(self, key):
        """
        Returns the value of a specific key in the base recipe.

        Args:
            key (str): The key whose value is to be retrieved.

        Returns:
            Any: Value associated with the key.
        """
        return self._base_recipe[key]

    def get_fonts_directory(self):
        """Returns the relative path to the fonts' directory."""
        return Path(self._fonts_data["relative_path_directory"])

    def get_font(self, font_type):
        """
        Returns the font file path and size for a given font type.

        Args:
            font_type (str): Font identifier key.

        Returns:
            tuple[Path, int]: Font file path and font size.
        """
        font = self._fonts_data[font_type]
        return self._ASSETS_ROOT / self.get_fonts_directory() / font["filename"], font["size"]

    def get_fonts(self):
        """Returns a tuple containing all configured fonts."""
        return self.get_font("title_font"), self.get_font("default_font"), self.get_font("secondary_title_font")

    def get_icons_directory(self):
        """Returns the relative path to the icons' directory."""
        return Path(self._icons_data["relative_path_directory"])

    def get_icon(self, icon_type):
        """
        Returns the full path to a specific icon.

        Args:
            icon_type (str): Icon identifier key.

        Returns:
            str: Full file path to the icon.
        """
        return str(self._ASSETS_ROOT / self.get_icons_directory() / self._icons_data[icon_type])

    def get_application_icons(self):
        """Returns the small and large application icons."""
        return self.get_icon("small_icon"), self.get_icon("large_icon")

    def get_action_icons(self):
        """Returns save, load, and export action icons."""
        return self.get_icon("save_icon"), self.get_icon("load_icon"), self.get_icon("export_icon")

    def get_application_title(self):
        """Returns the application window title."""
        return self._viewport_data["application_title"]

    def get_viewport_width(self):
        """Returns the width of the application viewport."""
        return self._viewport_data["width"]

    def get_viewport_height(self):
        """Returns the height of the application viewport."""
        return self._viewport_data["height"]

    def get_viewport_position(self):
        """Returns the screen position of the viewport."""
        return self._viewport_data["viewport_position"]

    def get_viewport_data(self):
        """Returns a tuple of application title, width, height, and position."""
        return (self.get_application_title(),
                self.get_viewport_width(),
                self.get_viewport_height(),
                self.get_viewport_position())

    def get_action_buttons_dimensions(self):
        """Returns the dimensions for action/menu buttons."""
        return self._icons_data["menu_button_dimensions"]
