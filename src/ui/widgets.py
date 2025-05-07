from pathlib import Path

import dearpygui.dearpygui as dpg

from .callbacks import CallbackHandler
from src.data import DataExtractor
from src.configuration import Configuration
from .ui_enums import IngredientType, ProofingType, ProofingMode, get_proofing_modes


class WidgetHandler:
    """
    Manages UI widgets for a given PizzaRecipe instance.
    Ensures only one handler exists per unique recipe object.
    """
    _instances = {}

    def __new__(cls, recipe):
        if recipe not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[recipe] = instance
            instance._initialized = False
        return cls._instances[recipe]

    def __init__(self, recipe):
        """
        Initializes the WidgetHandler with the given recipe and data extractor
        :param recipe: The pizza recipe object that holds the recipe parameters
        """
        if self._initialized:
            return

        self._recipe = recipe
        self._data_extractor = DataExtractor()
        self._configuration = Configuration()
        self._callback_handler = CallbackHandler(recipe)

        self._yeast_types = self._data_extractor.get_yeast_types()

        self._update_callback = self._callback_handler.general_update
        self._fermentation_callback = self._callback_handler.fermentation_update
        self._temperature_callback = self._callback_handler.temperature_update
        self._relative_path = Path(__file__).parent

        self._temperature_range_rounded = self._get_temperature_range_rounded()
        self._get_sorted_durations_by_temperature = self._data_extractor.get_sorted_durations_by_temperature

        self._title_font, self._default_font, self._secondary_title_font = self._get_fonts()

        self._initialized = True

    def _get_fonts(self):
        """
        Load and register fonts from configuration.
        Returns:
            tuple: (title_font, default_font, secondary_title_font)
        """
        with dpg.font_registry():
            title_info, default_info, secondary_info = self._configuration.get_fonts()

            title_font = dpg.add_font(title_info[0], title_info[1])
            default_font = dpg.add_font(default_info[0], default_info[1])
            secondary_font = dpg.add_font(secondary_info[0], secondary_info[1])

            dpg.bind_font(default_font)

            return title_font, default_font, secondary_font

    def _get_temperature_range_rounded(self):
        """
        Returns the temperature range, rounded to 1 decimal place, suitable for temperature-related widgets.
        :return: List of rounded temperature values.
        """
        return [
            str(int(t)) if float(t).is_integer() else str(round(t, 1))
            for t in self._data_extractor.temperature_value_range
        ]

    def load_input_widgets(self):
        """
        Loads the main input widgets for the pizza recipe, including fields like number of balls,
        ball weight, yeast type, etc..
        """
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()

            self._load_number_of_balls_widget()
            self._load_ball_weight_widget()
            self._load_yeast_type_widget()
            self._load_hydration_widget()
            self._load_salt_widget()
            self._load_oil_widget()

    def load_proofing_widgets(self):
        """ Loads the proofing-related widgets, including cold and room proof temperature and fermentation time """
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()

            self._load_cold_proof_temperature_widget()
            self._load_cold_proof_fermentation_widget()
            self._load_room_proof_temperature_widget()
            self._load_room_proof_fermentation_widget()

        # self._proof_handler.store_proof_values()
        # self._proof_handler.update_proofing_mode_from_recipe() # should not be here after updating the load callback
        # self._proof_handler.store_proof_values()
        self._callback_handler.proofing_mode_setup_callback()

    def _load_number_of_balls_widget(self):
        items = [str(i) for i in range(1, 11)]
        self._labeled_ingredient_widget(dpg.add_combo, IngredientType.number_of_balls, castor=int, items=items)

    def _load_ball_weight_widget(self):
        self._labeled_ingredient_widget(dpg.add_input_int, IngredientType.ball_weight)

    def _load_yeast_type_widget(self):
        self._labeled_ingredient_widget(dpg.add_combo, IngredientType.yeast_type, items=self._yeast_types)

    def _load_hydration_widget(self):
        self._labeled_ingredient_widget(dpg.add_input_int, IngredientType.hydration, max_value=100)

    def _load_salt_widget(self):
        ingredient_type = IngredientType.salt_percentage
        self._labeled_ingredient_widget(dpg.add_input_float, ingredient_type, max_value=5.0, format="%.1f")

    def _load_oil_widget(self):
        ingredient_type = IngredientType.oil_percentage
        self._labeled_ingredient_widget(dpg.add_input_float, ingredient_type, max_value=5.0, format="%.1f")

    def _load_cold_proof_temperature_widget(self):
        self._labeled_temperature_widget(ProofingType.fridge)

    def _load_cold_proof_fermentation_widget(self):
        self._labeled_fermentation_widget(ProofingType.fridge)

    def _load_room_proof_temperature_widget(self):
        self._labeled_temperature_widget(ProofingType.room)

    def _load_room_proof_fermentation_widget(self):
        self._labeled_fermentation_widget(ProofingType.room)

    def load_proofing_modes_widget(self):
        """Loads the widget for selecting the proofing modes (room and cold proof)"""
        dpg.add_text("Proofing Details", bullet=False, tag="proofing_title")
        dpg.bind_item_font("proofing_title", self._title_font)
        dpg.add_radio_button(items=get_proofing_modes(),
                             default_value=ProofingMode.dual_proofing_mode.value,
                             callback=lambda _, a: self._callback_handler.proofing_mode_callback(ProofingMode(a)),
                             horizontal=True,
                             tag="proofing_mode")

    def _load_output_display(self):
        """
        Loads the output display widget for showing the current pizza recipe as text.
        """
        with dpg.table_row():
            dpg.add_input_text(tag="output_text",
                               default_value=str(self._recipe),
                               multiline=True,
                               width=-10,
                               readonly=True)

    def _load_action_buttons(self):
        """Loads the action buttons (Save, Load, Export)"""
        with dpg.table_row():
            with dpg.group(horizontal=True):
                width, height = self._configuration.get_action_buttons_dimensions()

                self._add_button("save", width, height, self._callback_handler.save_callback)
                self._add_button("load", width, height, self._callback_handler.load_callback)
                self._add_button("export", width, height, self._callback_handler.export_callback)

    def load_output_section(self):
        """Loads the section for displaying the output and the action buttons (Save, Load, Export)"""
        with dpg.table(header_row=False):
            dpg.add_table_column()
            self._load_output_display()
            self._load_action_buttons()

    def load_main_input_header(self):
        """ Loads the header for the main recipe inputs section """
        dpg.add_text("Main Recipe Inputs", bullet=False, tag="main_title")
        dpg.bind_item_font("main_title", self._title_font)

    def load_instructions_header(self):
        """ Loads the header for the ingredients and proofing instructions section """
        dpg.add_text("Ingredients and Proofing Instructions", bullet=False, tag="instructions_title")
        dpg.bind_item_font("instructions_title", self._title_font)

    def create_viewport(self):
        """ Creates and sets up the application viewport (window) """
        title, width, height, position = self._configuration.get_viewport_data()
        small_icon, large_icon = self._configuration.get_application_icons()

        dpg.create_viewport(title=title, width=width, height=height)
        dpg.set_viewport_pos(position)
        dpg.set_viewport_resizable(False)
        dpg.set_viewport_small_icon(small_icon)
        dpg.set_viewport_large_icon(large_icon)
        dpg.set_viewport_max_width(width)
        dpg.set_viewport_max_height(height)
        dpg.setup_dearpygui()

    def create_menu_buttons(self):
        """ Creates the menu buttons with icons for Save, Load, and Export """
        save_icon_path, load_icon_path, export_icon_path = self._configuration.get_action_icons()

        _, _, _, save_icon_data = dpg.load_image(save_icon_path)
        _, _, _, load_icon_data = dpg.load_image(load_icon_path)
        width, height, _, export_icon_data = dpg.load_image(export_icon_path)

        with dpg.texture_registry():
            dpg.add_static_texture(width=width, height=height, default_value=save_icon_data, tag="save_icon")
            dpg.add_static_texture(width=width, height=height, default_value=load_icon_data, tag="load_icon")
            dpg.add_static_texture(width=width, height=height, default_value=export_icon_data, tag="export_icon")

    def _labeled_ingredient_widget(self, widget_fn, ingredient_type: IngredientType, *, castor=None, **kwargs):
        """
        Create a labeled widget for an ingredient input field
        :param widget_fn: The DearPyGui widget function to call (e.g., dpg.add_input_float)
        :param ingredient_type: The ingredient type (IngredientType)
        :param castor: Optional function to cast the input value before updating
        :param kwargs: Additional keyword arguments passed to the widget.
        """
        label = ingredient_type.value
        tag = ingredient_type.name
        default_value = getattr(self._recipe, tag)
        callback = (lambda _, a, u=tag: self._update_callback(a if castor is None else castor(a), u))

        self._labeled_widget(label, widget_fn, tag, default_value=default_value, callback=callback, **kwargs)

    def _labeled_temperature_widget(self, proofing_type: ProofingType):
        """
        Create a labeled combo box for selecting the proofing temperature
        :param proofing_type: The type of proofing (ProofingType).
        """
        label = proofing_type.value["temperature_label"]
        tag = proofing_type.value["temperature"]
        items = self._temperature_range_rounded
        default_value = str(round(getattr(self._recipe, tag), 1))
        callback = (lambda _, a: self._temperature_callback(a, proofing_type))

        self._labeled_widget(label, dpg.add_combo, tag, default_value, callback, items=items)

    def _labeled_fermentation_widget(self, proofing_type: ProofingType):
        """
        Create a labeled combo box for selecting fermentation time based on temperature
        :param proofing_type: The type of proofing (ProofingType).
        """
        fermentation_label = proofing_type.value["fermentation_label"]
        fermentation_tag = proofing_type.value["fermentation"]
        temperature_tag = proofing_type.value["temperature"]

        temperature = getattr(self._recipe, temperature_tag)
        fermentation = str(int(getattr(self._recipe, fermentation_tag)))

        if temperature <= 0:
            temperature = self._configuration.get_base_recipe_value(temperature_tag)
            fermentation = self._configuration.get_base_recipe_value(fermentation_tag)

        items = self._get_sorted_durations_by_temperature(temperature)
        default_value = str(int(fermentation))

        callback = (lambda _, a: self._fermentation_callback(a, proofing_type))

        self._labeled_widget(fermentation_label, dpg.add_combo, fermentation_tag, default_value, callback, items=items)

    def _labeled_widget(self, label, widget_fn, tag, default_value, callback, **kwargs):
        """
        Create a labeled widget row with a text label and input widget
        :param label: The text to display next to the input
        :param widget_fn: The DearPyGui function to use for creating the widget
        :param tag: Unique tag name for the widget
        :param default_value: The default value shown in the widget
        :param callback: Function to call when the value changes
        :param kwargs: Additional arguments passed to the widget.
        """
        with dpg.table_row():
            dpg.add_text(label, tag=f"{tag}_label")
            widget_fn(tag=tag, user_data=tag, default_value=default_value, callback=callback, width=-10, **kwargs)
            dpg.bind_item_font(f"{tag}_label", self._secondary_title_font)

    @staticmethod
    def _add_button(label, height, width, callback):
        """
        Add an image button with a tooltip
        :param label: Base name for the icon and tooltip (e.g., 'save')
        :param height: Button height in pixels
        :param width: Button width in pixels
        :param callback: Function to call when the button is clicked.
        """
        tag = f"{label}_button"
        label_capitalize = label.capitalize()

        dpg.add_image_button(label=label_capitalize, texture_tag=f"{label}_icon", tag=tag,
                             height=height, width=width, callback=callback)

        with dpg.tooltip(parent=tag):
            dpg.add_text(f"{label_capitalize} recipe")

    @staticmethod
    def show_viewport():
        """
        Displays the application viewport (window), sets the primary window,
        and starts the DearPyGui event loop.
        """
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
