"""
The configuration package handles loading and managing app-wide and recipe-specific settings.

Modules:
- configuration.py: Parses and manages configurations from JSON files.

Data:
- neapolitan_config.json: Default settings for Neapolitan recipes.
- ui_config.json: UI layout and behavior settings.
"""

from .configuration import Configuration
