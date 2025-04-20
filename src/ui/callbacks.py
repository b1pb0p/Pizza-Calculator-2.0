import dearpygui.dearpygui as dpg
from src.manager.manager import RecipeManager


class CallbackHandler:
    """
    Handles various callbacks triggered by UI interaction, modifying the recipe
    object and updating the interface accordingly.
    """

    def __init__(self, recipe, data_extractor):
        """
        Initialize the callback handler
        :param recipe: The recipe object to update
        :param data_extractor: An instance used to extract temperature-duration data.
        """
        self._recipe = recipe
        self._data_extractor = data_extractor

    def get_sorted_durations_by_temperature(self, temperature):
        """
        Get a sorted list of unique durations (as strings) for a given temperature
        :param temperature: The temperature to retrieve durations for.
        :return: List of duration strings, sorted and unique.
        """
        return [str(int(duration)) for duration in
                sorted(set(self._data_extractor.get_duration_range_by_temperature(temperature)))]

    def update_output(self):
        """
        Updates the UI output text area with the current string representation of the recipe.
        """
        dpg.set_value("output_text", str(self._recipe))

    def general_update(self, app_data, user_data):
        """
        General callback for updating recipe attributes from UI changes
        :param app_data: New value from UI
        :param user_data: The name of the recipe attribute to update.
        """
        setattr(self._recipe, user_data, app_data)
        self.update_output()

    def temperature_update(self, app_data, is_fridge):
        """
        Handles updates to temperature input. Adjusts temperature and updates
        the corresponding fermentation time options
        :param app_data: New temperature value from UI
        :param is_fridge: Boolean flag for fridge or room temperature.
        """
        selected_temperature = float(min(
            self._data_extractor.temperature_value_range, key=lambda x: abs(x - float(app_data))))
        durations = self.get_sorted_durations_by_temperature(selected_temperature)
        if is_fridge:
            self._recipe.fridge_temperature = selected_temperature
            dpg.configure_item("fridge_fermentation", items=[(int(duration)) for duration in durations])
        else:
            self._recipe.room_temperature = selected_temperature
            dpg.configure_item("room_fermentation", items=[(int(duration)) for duration in durations])
        self.update_output()

    def fermentation_update(self, app_data, is_fridge):
        """
        Handles updates to fermentation duration
        :param app_data: New fermentation time from UI
        :param is_fridge: Boolean flag for fridge or room fermentation.
        """
        if is_fridge:
            self._recipe.fridge_fermentation = float(app_data)
        else:
            self._recipe.room_fermentation = float(app_data)
        self.update_output()

    def save_callback(self):
        """
        Triggers saving the current recipe as a JSON file.
        """
        RecipeManager.save_recipe_as_json(self._recipe)

    def export_callback(self):
        """
        Triggers exporting the current recipe as a formatted text file.
        """
        RecipeManager.save_recipe_as_txt(self._recipe)
