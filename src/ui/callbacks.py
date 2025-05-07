import dearpygui.dearpygui as dpg

from src.data import DataExtractor
from src.manager import RecipeManager
from .proofing_handler import ProofingHandler
from .ui_enums import ProofingType, ProofingMode, IngredientType


class CallbackHandler:
    """
    Handles various callbacks triggered by UI interaction, modifying the recipe
    object and updating the interface accordingly.
    """

    def __init__(self, recipe):
        """
        Initialize the callback handler
        :param recipe: The recipe object to update
        """
        self._recipe = recipe
        self._data_extractor = DataExtractor()
        self._proof_handler = ProofingHandler(self._recipe)

        # Cache values and methods to avoid repeated attribute access.
        self._temperature_value_range = self._data_extractor.temperature_value_range
        self._get_sorted_durations_by_temperature = self._data_extractor.get_sorted_durations_by_temperature

    def update_output(self):
        """Updates the UI output text area with the current string representation of the recipe."""
        dpg.set_value("output_text", str(self._recipe))

    def general_update(self, app_data, user_data):
        """
        Generic update callback for any simple recipe attribute modified via the UI
        :param app_data: The new value from the UI (number, string, etc.)
        :param user_data: The name of the recipe attribute to update (string).
        """
        setattr(self._recipe, user_data, app_data)
        self.update_output()

    def temperature_update(self, app_data, proofing_type: ProofingType):
        """
        Called when temperature input is changed. Updates recipe and corresponding
        fermentation time based on closest valid temperature
        :param app_data: New temperature value from the UI
        :param proofing_type: ProofingType enum (e.g., room or fridge).
        """
        temperature = float(app_data)
        fermentation = int(dpg.get_value(proofing_type.value["fermentation"]))

        self._apply_proofing_adjustments(proofing_type, temperature, fermentation)
        self.update_output()

    def fermentation_update(self, app_data, proofing_type: ProofingType):
        """
        Called when fermentation duration is changed manually
        :param app_data: New fermentation value from UI
        :param proofing_type: ProofingType enum.
        """
        setattr(self._recipe, proofing_type.value["fermentation"], float(app_data))
        self.update_output()

    def save_callback(self):
        """Triggered when the user presses the 'Save' button. Saves current recipe to JSON."""
        RecipeManager.save_recipe_as_json(self._recipe)

    def export_callback(self):
        """Triggered when the user presses the 'Export' button. Saves current recipe as text."""
        RecipeManager.save_recipe_as_txt(self._recipe)

    def load_callback(self):
        """Loads a previously saved recipe. Updates all UI elements and recipe fields accordingly."""
        new_recipe = RecipeManager.load_recipe(use_default=False)

        if new_recipe is None:
            return

        self._recipe.__dict__.update(new_recipe.__dict__)  # Copy data into the current recipe instance.

        self._update_ui_ingredient_elements()
        self._update_proofing_inputs()
        self.update_output()

    def _update_ui_ingredient_elements(self):
        """Update ingredient UI elements"""
        for ingredient in IngredientType:
            dpg.set_value(ingredient.name, getattr(self._recipe, ingredient.name))

    def _update_proofing_inputs(self):
        """Update temperature/fermentation inputs."""
        for proofing_type in ProofingType:
            temperature = getattr(self._recipe, proofing_type.value["temperature"])
            fermentation = getattr(self._recipe, proofing_type.value["fermentation"])

            if temperature != 0 and fermentation != 0:
                self._apply_proofing_adjustments(proofing_type, temperature, fermentation)

        self.proofing_mode_setup_callback()

    def _apply_proofing_adjustments(self, proofing_type: ProofingType, temperature, fermentation):
        """
        Adjusts recipe temperature and fermentation values to match the nearest valid values,
        and updates UI accordingly
        :param proofing_type: Type of proofing (room/fridge)
        :param temperature: User-provided temperature input
        :param fermentation: User-provided fermentation duration.
        """
        temperature_tag = proofing_type.value["temperature"]
        fermentation_tag = proofing_type.value["fermentation"]

        selected_temperature = float(min(self._temperature_value_range, key=lambda x: abs(x - temperature)))
        durations = self._get_sorted_durations_by_temperature(selected_temperature)
        default_value = int(min(durations, key=lambda x: abs(x - fermentation)))

        setattr(self._recipe, temperature_tag, selected_temperature)
        setattr(self._recipe, fermentation_tag, float(default_value))
        dpg.configure_item(fermentation_tag, items=durations, default_value=default_value)

    def _update_proofing_mode(self, first_type, second_type, show_first, show_second):
        """
        Toggles visibility of proofing UI items and optionally resets their stored values
        :param first_type: ProofingType to show/hide first
        :param second_type: ProofingType to show/hide second
        :param show_first: Boolean flag whether to show first_type
        :param show_second: Boolean flag whether to show second_type.
        """
        self._proof_handler.toggle_proof_item(first_type, show_first)
        self._proof_handler.toggle_proof_item(second_type, show_second)
        self._proof_handler.store_proofing_values(first_type, reset=not show_first)
        self._proof_handler.store_proofing_values(second_type, reset=not show_second)

    def proofing_mode_callback(self, proofing_mode: ProofingMode):
        """
        Called when user selects a new proofing mode (dual/room-only/fridge-only).
        Adjusts which proofing inputs are visible and active
        :param proofing_mode: A ProofingMode enum indicating the desired UI configuration.
        """
        if proofing_mode == ProofingMode.dual_proofing_mode:
            self._update_proofing_mode(ProofingType.room, ProofingType.fridge, True, True)
        elif proofing_mode == ProofingMode.room_proofing_only_mode:
            self._update_proofing_mode(ProofingType.room, ProofingType.fridge, True, False)
        else:
            self._update_proofing_mode(ProofingType.fridge, ProofingType.room, True, False)

        if dpg.does_item_exist("output_text"):
            self.update_output()

    def proofing_mode_setup_callback(self):
        """Initializes the UI proofing state based on current recipe proofing configuration."""
        self._proof_handler.update_proofing_mode_from_recipe()
