import json
from pathlib import Path


class Configuration:
    """
    Singleton Configuration class that loads and provides access to JSON config files,
    including yeast table parameters and UI setup.
    """
    _instance = None
    _PIZZA_CONFIGURATION_PATH = rf"neapolitan_config.json"
    _UI_CONFIGURATION_PATH = rf"ui_config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._relative_path = Path(__file__).parent

        self._pizza_data = self._load_config(self._PIZZA_CONFIGURATION_PATH)
        self._ui_data = self._load_config(self._UI_CONFIGURATION_PATH)

        self._yeast_table_parameters = self._pizza_data["yeast_table_parameters"]
        self._base_recipe = self._pizza_data["base_recipe"]

        self._fonts_data = self._ui_data["fonts"]
        self._icons_data = self._ui_data["icons"]
        self._viewport_data = self._ui_data["viewport"]

        self._initialized = True

    def _load_config(self, configuration_path):
        """Load and return the contents of the config file as a dictionary."""
        path = self._relative_path / configuration_path
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_yeast_table_filename(self):
        """Return the filename of the yeast CSV table."""
        return self._yeast_table_parameters["yeast_table_filename"]

    def get_yeast_table_filepath(self):
        """Return the full absolute path to the yeast CSV file."""
        return Path(__file__).parent.parent / rf"data\{self.get_yeast_table_filename()}"

    def get_yeast_types(self):
        """Return the list of supported yeast types."""
        return self._yeast_table_parameters["yeast_types"]

    def get_temperature_column(self):
        """Return the column index where temperature values are stored."""
        return self._yeast_table_parameters["temperature_column"]

    def get_temperature_row_range(self):
        """Return a tuple with the first and last row index for the temperature range."""
        return (
            self._yeast_table_parameters["first_temperature_row"],
            self._yeast_table_parameters["last_temperature_row"]
        )

    def get_selective_temperature_row_range(self):
        """Return a tuple for a specific temperature range (e.g. for slicing)."""
        return (
            self._yeast_table_parameters["lower_range_temperature_row"],
            self._yeast_table_parameters["upper_range_temperature_row"]
        )

    def get_duration_column_range(self):
        """Return a tuple with the first and last column index for duration values."""
        return (
            self._yeast_table_parameters["first_duration_column"],
            self._yeast_table_parameters["last_duration_column"]
        )

    def get_default_room_fermentation(self):
        """Return default coordinates for room fermentation (row, column)."""
        return (
            self._yeast_table_parameters["default_room_temperature_row"],
            self._yeast_table_parameters["default_room_fermentation_column"]
        )

    def get_default_fridge_fermentation(self):
        """Return default coordinates for fridge fermentation (row, column)."""
        return (
            self._yeast_table_parameters["default_fridge_temperature_row"],
            self._yeast_table_parameters["default_fridge_fermentation_column"]
        )

    def get_base_recipe(self):
        """Return the full base recipe dictionary."""
        return self._base_recipe

    def get_recipe_value(self, key):
        """Return a specific value from the base recipe by key."""
        return self._base_recipe[key]

    def get_fonts_directory(self):
        return Path(self._fonts_data["relative_path_directory"])

    def get_font(self, font_type):
        font = self._fonts_data[font_type]
        return self._relative_path.parent / self.get_fonts_directory() / font["filename"], font["size"]

    def get_fonts(self):
        return self.get_font("title_font"),\
               self.get_font("default_font"),\
               self.get_font("secondary_title_font")

    def get_icons_directory(self):
        return Path(self._icons_data["relative_path_directory"])

    def get_icon(self, icon_type):
        return str(self._relative_path.parent / self.get_icons_directory() / self._icons_data[icon_type])

    def get_application_icons(self):
        return self.get_icon("small_icon"), self.get_icon("large_icon")

    def get_action_icons(self):
        return self.get_icon("save_icon"),\
               self.get_icon("load_icon"),\
               self.get_icon("export_icon")

    def get_application_title(self):
        return self._viewport_data["application_title"]

    def get_viewport_width(self):
        return self._viewport_data["width"]

    def get_viewport_height(self):
        return self._viewport_data["height"]

    def get_viewport_position(self):
        return self._viewport_data["viewport_position"]

    def get_viewport_data(self):
        return self.get_application_title(),\
               self.get_viewport_width(),\
               self.get_viewport_height(),\
               self.get_viewport_position()
