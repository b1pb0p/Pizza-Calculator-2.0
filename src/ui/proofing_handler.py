"""
proofing_handler.py

This file contains the ProofingHandler class, which manages proofing settings for a pizza recipe,
including room and cold (fridge) proofing. It handles UI visibility toggling, value updates,
and syncing with the recipe model.
"""

import dearpygui.dearpygui as dpg

from src.configuration import Configuration
from .ui_enums import ProofingType, ProofingMode


class ProofingHandler:
    """
    Manages proofing settings for a pizza recipe including room and cold (fridge) proofing.
    Handles UI visibility toggling, value updates, and syncing with the recipe model.
    """

    def __init__(self, recipe):
        """
        Initializes the ProofingHandler.

        Args:
            recipe (PizzaRecipe): The recipe object that stores fermentation and temperature values.
        """
        self._recipe = recipe
        self._configuration = Configuration()

    def store_proofing_values(self, proofing_type: ProofingType, reset=False):
        """
        Stores proofing values (temperature and fermentation time) into the recipe.

        Args:
            proofing_type (ProofingType): The type of proofing (room or fridge).
            reset (bool): If True, resets the values to 0. Otherwise, updates the values from the UI.
        """
        temperature_tag = proofing_type.value["temperature"]
        fermentation_tag = proofing_type.value["fermentation"]

        if reset:
            temperature = 0.0
            fermentation = 0.0
        else:
            temperature = float(dpg.get_value(temperature_tag))
            fermentation = float(dpg.get_value(fermentation_tag))

        setattr(self._recipe, f"_{fermentation_tag}", fermentation)  # Set directly to skip yeast recalculation
        setattr(self._recipe, temperature_tag, temperature)

    def update_proofing_mode_from_recipe(self):
        """
        Updates the proofing mode in the UI based on the current recipe's fermentation settings.
        Determines whether dual proofing, room-only, or fridge-only proofing mode is needed.

        This method will toggle the visibility of relevant proofing items in the UI.
        """
        if not dpg.does_item_exist("proofing_mode"):
            return

        if self._recipe.room_fermentation > 0 and self._recipe.fridge_fermentation > 0:
            room_default_flag = True
            fridge_default_flag = True
            mode = ProofingMode.dual_proofing_mode
        elif self._recipe.room_fermentation > 0:
            room_default_flag = True
            fridge_default_flag = False
            mode = ProofingMode.room_proofing_only_mode
        elif self._recipe.fridge_fermentation > 0:
            room_default_flag = False
            fridge_default_flag = True
            mode = ProofingMode.cold_proofing_only_mode
        else:
            room_default_flag = True
            fridge_default_flag = True
            mode = ProofingMode.dual_proofing_mode

        self.toggle_proof_item(ProofingType.room, room_default_flag)
        self.toggle_proof_item(ProofingType.fridge, fridge_default_flag)

        dpg.set_value("proofing_mode", mode.value)

    @staticmethod
    def toggle_proof_item(proofing_type: ProofingType, show=True):
        """
        Toggles the visibility of proofing items (temperature and fermentation) in the UI.

        Args:
            proofing_type (ProofingType): The type of proofing (room or fridge).
            show (bool): Whether to show or hide the proofing items.
        """
        temperature_tag = proofing_type.value["temperature"]
        fermentation_tag = proofing_type.value["fermentation"]

        dpg.configure_item(temperature_tag, show=show)
        dpg.configure_item(f"{temperature_tag}_label", show=show)
        dpg.configure_item(fermentation_tag, show=show)
        dpg.configure_item(f"{fermentation_tag}_label", show=show)
