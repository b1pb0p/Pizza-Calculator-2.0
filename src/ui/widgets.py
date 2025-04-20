from pathlib import Path
import dearpygui.dearpygui as dpg
from src.ui.callbacks import CallbackHandler
from src.ui.proof_handler import ProofHandler
from src.data.data_extractor import DataExtractor
from src.configuration.configuration import Configuration


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
            instance.__init__(recipe)  # explicitly call init
        return cls._instances[recipe]

    def __init__(self, recipe):
        """
        Initializes the WidgetHandler with the given recipe and data extractor
        :param recipe: The pizza recipe object that holds the recipe parameters
        """
        self._recipe = recipe
        self._data_extractor = DataExtractor()
        self._configuration = Configuration()
        self._yeast_types = self._data_extractor.get_yeast_types()
        self._callback_handler = CallbackHandler(recipe, self._data_extractor)
        self._update_callback = self._callback_handler.general_update
        self._fermentation_callback = self._callback_handler.fermentation_update
        self._temperature_callback = self._callback_handler.temperature_update
        self._proof_handler = ProofHandler(self._recipe, self._callback_handler)
        self._relative_path = Path(__file__).parent

        self._temperature_range_rounded = self._get_temperature_range_rounded()
        self._get_sorted_durations_by_temperature = self._callback_handler.get_sorted_durations_by_temperature

        self._title_font, self._default_font, self._secondary_title_font = self._get_fonts()

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

            font = self._secondary_title_font

            self._load_number_of_balls_widget(font)
            self._load_ball_weight_widget(font)
            self._load_yeast_type_widget(font)
            self._load_hydration_widget(font)
            self._load_salt_widget(font)
            self._load_oil_widget(font)

    def load_proofing_widgets(self):
        """ Loads the proofing-related widgets, including cold and room proof temperature and fermentation time """
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()

            font = self._secondary_title_font

            self._load_cold_proof_temperature_widget(font)
            self._load_cold_proof_fermentation_widget(font)
            self._load_room_proof_temperature_widget(font)
            self._load_room_proof_fermentation_widget(font)

        self._proof_handler.store_proof_values()

    def _load_number_of_balls_widget(self, font):
        self._labeled_widget("Number of Balls", dpg.add_combo,
                             tag="number_of_balls",
                             items=[str(i) for i in range(1, 11)],
                             default_value=self._recipe.number_of_balls,
                             callback=lambda _, a, u="number_of_balls": self._update_callback(int(a), u),
                             user_data="number_of_balls",
                             font=font)

    def _load_ball_weight_widget(self, font):
        self._labeled_widget("Ball Weight (g)", dpg.add_input_int,
                             tag="ball_weight",
                             default_value=self._recipe.ball_weight,
                             callback=lambda _, a, u="ball_weight": self._update_callback(a, u),
                             user_data="ball_weight",
                             font=font)

    def _load_yeast_type_widget(self, font):
        self._labeled_widget("Yeast Type", dpg.add_combo,
                             tag="yeast_type",
                             items=self._yeast_types,
                             default_value=self._recipe.yeast_type,
                             callback=lambda _, a, u="yeast_type": self._update_callback(a, u),
                             user_data="yeast_type",
                             font=font)

    def _load_hydration_widget(self, font):
        self._labeled_widget("Hydration (%)", dpg.add_input_int,
                             tag="hydration",
                             default_value=self._recipe.hydration,
                             max_value=100,
                             callback=lambda _, a, u="hydration": self._update_callback(a, u),
                             user_data="hydration",
                             font=font)

    def _load_salt_widget(self, font):
        self._labeled_widget("Salt (%)", dpg.add_input_float,
                             tag="salt_percentage",
                             default_value=self._recipe.salt_percentage,
                             max_value=5.0,
                             format="%.1f",
                             callback=lambda _, a, u="salt_percentage": self._update_callback(a, u),
                             user_data="salt_percentage",
                             font=font)

    def _load_oil_widget(self, font):
        self._labeled_widget("Oil (%)", dpg.add_input_float,
                             tag="oil_percentage",
                             default_value=self._recipe.oil_percentage,
                             max_value=5.0,
                             format="%.1f",
                             callback=lambda _, a, u="oil_percentage": self._update_callback(a, u),
                             user_data="oil_percentage",
                             font=font)

    def _load_cold_proof_temperature_widget(self, font):
        self._labeled_widget("Cold Proof temperature (°C)", dpg.add_combo,
                             tag="fridge_temperature",
                             items=self._temperature_range_rounded,
                             default_value=str(round(self._recipe.fridge_temperature, 1)),
                             callback=lambda _, a: self._temperature_callback(a, True),
                             font=font)

    def _load_cold_proof_fermentation_widget(self, font):
        self._labeled_widget("Cold Proof Hours", dpg.add_combo,
                             tag="fridge_fermentation",
                             items=self._get_sorted_durations_by_temperature(self._recipe.fridge_temperature),
                             default_value=str(self._recipe.fridge_fermentation),
                             callback=lambda _, a: self._fermentation_callback(a, True),
                             font=font)

    def _load_room_proof_temperature_widget(self, font):
        self._labeled_widget("Room Proof temperature (°C)", dpg.add_combo,
                             tag="room_temperature",
                             items=self._temperature_range_rounded,
                             default_value=str(round(self._recipe.room_temperature, 1)),
                             callback=lambda _, a: self._temperature_callback(a, False),
                             font=font)

    def _load_room_proof_fermentation_widget(self, font):
        self._labeled_widget("Room Proof Hours", dpg.add_combo,
                             tag="room_fermentation",
                             items=self._get_sorted_durations_by_temperature(self._recipe.room_temperature),
                             default_value=str(self._recipe.room_fermentation),
                             callback=lambda _, a: self._fermentation_callback(a, False),
                             font=font)
        
    def load_proofing_modes_widget(self):
        """ Loads the widget for selecting the proofing modes (room and cold proof) """
        dpg.add_text("Proofing Details", bullet=False, tag="proofing_title")
        dpg.bind_item_font("proofing_title", self._title_font)
        dpg.add_radio_button(items=self._proof_handler.get_proofing_modes(),
                             default_value="Both",
                             callback=lambda _, a: self._proof_handler.toggle_proofing_mode(a),
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
                               width=425,
                               readonly=True)

    def _action_buttons(self, load_callback):
        """
        Loads the action buttons (Save, Load, Export) for the pizza recipe
        :param load_callback: The callback function to load the recipe.
        """
        with dpg.table_row():
            with dpg.group(horizontal=True):
                dpg.add_image_button(label="Save", texture_tag="save_icon",
                                     height=16, width=16, callback=self._callback_handler.save_callback)
                dpg.add_image_button(label="Load", texture_tag="load_icon",
                                     height=16, width=16, callback=load_callback)
                dpg.add_image_button(label="Export", texture_tag="export_icon",
                                     height=16, width=16, callback=self._callback_handler.export_callback)

    def load_output_section(self, load_callback):
        """
        Loads the section for displaying the output and the action buttons (Save, Load, Export)
        :param load_callback: The callback function to load the recipe.
        """
        with dpg.table(header_row=False):
            dpg.add_table_column()
            self._load_output_display()
            self._action_buttons(load_callback)

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

    @staticmethod
    def _labeled_widget(label, widget_fn, tag, font, **kwargs):
        """
        Helper method to create a labeled widget
        :param label: The label text for the widget
        :param widget_fn: The function used to create the widget
        :param tag: The unique tag for the widget
        :param font: The font to be applied to the label
        :param kwargs: Additional arguments to pass to the widget function
        """
        with dpg.table_row():
            dpg.add_text(label, tag=f"{tag}_label")
            widget_fn(tag=tag, **kwargs)
            dpg.bind_item_font(f"{tag}_label", font)

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
