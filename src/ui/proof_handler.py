import dearpygui.dearpygui as dpg


class ProofHandler:
    """
    Manages proofing settings for a pizza recipe including room and cold (fridge) proofing.
    Handles UI visibility toggling, value updates, and syncing with the recipe model.
    """

    def __init__(self, recipe, callback_handler):
        """
        Initializes the ProofHandler
        :param recipe: The recipe object that stores fermentation and temperature values
        :param callback_handler: Handler to update UI output after proofing changes.
        """
        self._recipe = recipe
        self._callback_handler = callback_handler
        self._saved_values = {
            "room_temperature": 0.0,
            "room_fermentation": 0,
            "fridge_temperature": 0.0,
            "fridge_fermentation": 0
        }
        self._proofing_modes = ["Both", "Room proof only", "Cold proof only"]
        self._update_proofing_mode_from_recipe()

    def store_proof_values(self):
        """
        Saves current proofing values from the UI into `_saved_values` for future restoration.
        """
        self._saved_values["room_temperature"] = self._cast_float_to_int_if_whole("room_temperature")
        self._saved_values["room_fermentation"] = int(dpg.get_value("room_fermentation"))
        self._saved_values["fridge_temperature"] = self._cast_float_to_int_if_whole("fridge_temperature")
        self._saved_values["fridge_fermentation"] = int(dpg.get_value("fridge_fermentation"))

    def _toggle_up_proof(self, proof_type):
        """
        Shows and restores proofing fields for the given type (room or fridge)
        :param proof_type: "room" or "fridge"
        """
        fermentation = f"{proof_type}_fermentation"
        temperature = f"{proof_type}_temperature"

        self._toggle_proof_item(proof_type, True)
        dpg.set_value(temperature, self._saved_values[temperature])
        dpg.set_value(fermentation, self._saved_values[fermentation])
        setattr(self._recipe, temperature, self._saved_values[temperature])
        setattr(self._recipe, fermentation, self._saved_values[fermentation])

    def _toggle_down_proof(self, proof_type):
        """
        Hides and resets proofing fields for the given type (room or fridge).
        :param proof_type: "room" or "fridge"
        """
        fermentation = f"{proof_type}_fermentation"
        temperature = f"{proof_type}_temperature"

        self._toggle_proof_item(proof_type, False)
        self._saved_values[fermentation] = int(dpg.get_value(fermentation))
        self._saved_values[temperature] = self._cast_float_to_int_if_whole(temperature)
        setattr(self._recipe, fermentation, 0)
        setattr(self._recipe, temperature, 0)

    def _update_proof_values(self, proof_type, reset_other=True):
        """
        Activates proofing for the given type and optionally disables the other.

        :param proof_type: "room" or "fridge"
        :param reset_other: Whether to deactivate the opposite proof type
        """
        self._toggle_up_proof(proof_type)

        if reset_other:
            self._toggle_down_proof("room" if proof_type == "fridge" else "fridge")

    def toggle_proofing_mode(self, app_data):
        """
        Called when user selects a new proofing mode. Updates UI and recipe accordingly
        :param app_data: One of "Both", "Room proof only", or "Cold proof only"
        """
        if app_data == "Both":
            self.store_proof_values()
            self._update_proof_values("room", reset_other=False)
            self._update_proof_values("fridge", reset_other=False)
        elif app_data == "Room proof only":
            self._update_proof_values("room", reset_other=True)
        else:
            self._update_proof_values("fridge", reset_other=True)

        self._callback_handler.update_output()

    def _update_proofing_mode_from_recipe(self):
        """
        Sets the initial proofing mode based on the recipe's fermentation values.
        """
        if not dpg.does_item_exist("proofing_mode"):
            return

        if self._recipe.room_fermentation > 0 and self._recipe.fridge_fermentation > 0:
            mode = "Both"
        elif self._recipe.room_fermentation > 0:
            mode = "Room proof only"
        elif self._recipe.fridge_fermentation > 0:
            mode = "Cold proof only"
        else:
            mode = "Both"

        dpg.set_value("proofing_mode", mode)
        self.toggle_proofing_mode(mode)

    def get_proofing_modes(self):
        """
        Returns the list of available proofing modes.

        :return: List of mode names
        """
        return self._proofing_modes

    @staticmethod
    def _cast_float_to_int_if_whole(proof_time_tag):
        """
        Retrieves a float value from the UI and returns it as an int if it's a whole number
        :param proof_time_tag: The UI element identifier (string).
        :return: int if value is whole, otherwise float.
        """
        value = float(dpg.get_value(proof_time_tag))
        return int(value) if value.is_integer() else value

    @staticmethod
    def _toggle_proof_item(proof_type, show):
        """
        Shows or hides UI fields for the given proof type.

        :param proof_type: "room" or "fridge"
        :param show: Whether to show (True) or hide (False) the UI elements
        """
        dpg.configure_item(f"{proof_type}_temperature", show=show)
        dpg.configure_item(f"{proof_type}_temperature_label", show=show)
        dpg.configure_item(f"{proof_type}_fermentation", show=show)
        dpg.configure_item(f"{proof_type}_fermentation_label", show=show)
