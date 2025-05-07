"""
The data package provides access to external reference data used in pizza calculations.

Modules:
- data_extractor.py: Handles parsing of CSV data for yeast and fermentation calculations.

Data:
- neapolitan_yeast_table.csv: Lookup table for yeast percentages based on temperature and time.
"""

from .data_extractor import DataExtractor
