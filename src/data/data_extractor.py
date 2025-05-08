"""
data_extractor.py

Defines the singleton DataExtractor class responsible for parsing and extracting yeast data
from a CSV file based on temperature, fermentation duration, and yeast type.
Used to determine the appropriate yeast percentage for pizza dough recipes.
"""

import csv

from src.errors import ErrorMessages
from src.configuration import Configuration


class DataExtractor:
    """
    Singleton class to extract yeast data from a CSV file based on temperature, duration, and yeast type.
    """

    _instance = None

    def __new__(cls):
        """Ensures that only one instance of DataExtractor exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(DataExtractor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initializes CSV data, temperature and duration ranges from the configuration."""
        if self._initialized:
            return

        self._configuration = Configuration()
        self._yeast_data_file = self._configuration.get_yeast_table_filepath()
        self._csv_data = self._load_csv()
        self._temperature_column = self._configuration.get_temperature_column()
        self._duration_column_range = self._configuration.get_duration_column_range()
        self._temperature_range = self._configuration.get_selective_temperature_row_range()
        self._temperature_value_range = self.get_temperature_value_range()

        self._initialized = True

    def _load_csv(self):
        """
        Loads and parses the CSV file.

        Returns:
            list[list[str]]: 2D list containing CSV rows and columns.
        """
        with open(self._yeast_data_file, newline='', encoding='utf-8') as csvfile:
            return list(csv.reader(csvfile))

    def get_cell_value(self, row: int, column: int) -> str:
        """
        Retrieves the value at a specific row and column (1-based index).

        Args:
            row (int): Row index.
            column (int): Column index.

        Returns:
            str: Value at the given cell.
        """
        return self._csv_data[row][column]

    def get_temperature_value_range(self) -> list[float]:
        """
        Returns a list of temperature values (as floats) found in the configured row range.

        Returns:
            list[float]: List of temperature values.
        """
        column_index = self._temperature_column
        row_start, row_end = self._temperature_range
        reader = self._csv_data

        return [
            float(reader[i][column_index].strip())
            for i in range(row_start, row_end)
            if i < len(reader) and column_index < len(reader[i]) and reader[i][column_index].strip()
        ]

    def get_duration_value_range(self, row_index: int) -> list[float]:
        """
        Returns a list of duration values in a specified row.

        Args:
            row_index (int): Row index (1-based).

        Returns:
            list[float]: List of duration values.
        """
        column_start, column_end = self._duration_column_range
        reader = self._csv_data

        if row_index >= len(reader):
            return []

        row = reader[row_index]
        return [
            float(row[i].strip())
            for i in range(column_start, column_end)
            if i < len(row) and row[i].strip()
        ]

    def get_duration_range_by_temperature(self, temperature: float) -> list[float]:
        """
        Retrieves the list of durations available for a given temperature.

        Args:
            temperature (float): The temperature value.

        Returns:
            list[float]: List of duration values for the given temperature.
        """
        temperature_row_index = self.get_temperature_row_index(temperature, strict=False)
        return self.get_duration_value_range(temperature_row_index)

    def get_sorted_durations_by_temperature(self, temperature: float) -> list[float]:
        """
        Returns a sorted list of unique durations for a given temperature.

        Args:
            temperature (float): Temperature to retrieve durations for.

        Returns:
            list[float]: Sorted and unique duration values.
        """
        return [int(duration) for duration in
                sorted(set(self.get_duration_range_by_temperature(temperature)))]

    def get_temperature_row_index(self, temperature: float, strict: bool = True) -> int:
        """
        Given a temperature value, returns the corresponding row index within the temperature range.

        Args:
            temperature (float): Temperature value.
            strict (bool): If True, only exact match is accepted. If False, the closest match is allowed.

        Returns:
            int: Row's index in the CSV file.

        Raises:
            ValueError: If temperature is not found and strict is True.
        """
        temperature_str = f"{temperature:.1f}"

        if temperature_str in self._temperature_value_range:
            local_index = self._temperature_value_range.index(temperature)
        elif not strict:
            closest_temp = min(self._temperature_value_range, key=lambda x: abs(x - temperature))
            local_index = self._temperature_value_range.index(closest_temp)
        else:
            raise ValueError(ErrorMessages.TEMPERATURE_NOT_FOUND.format(temperature_str))

        return self._temperature_range[0] + local_index

    def get_closest_duration_column(self, duration: float, temperature: float) -> int:
        """
        Retrieves the column index corresponding to the closest duration value for a given temperature.

        Args:
            duration (float): Duration value.
            temperature (float): Temperature value.

        Returns:
            int: Closest matching duration column index.
        """
        temperature_row_index = self.get_temperature_row_index(temperature, strict=False)
        duration_values = self.get_duration_value_range(temperature_row_index)
        closest_duration_column = self._find_closest_duration_column(
            temperature_row_index,
            duration,
            duration_values)

        return closest_duration_column

    def _find_closest_duration_column(self, row: int, duration: float, duration_range: list[float]) -> int:
        """
        Finds the closest duration column for a given duration value in a specific row.

        Args:
            row (int): Row index.
            duration (float): Duration value to match.
            duration_range (list[float]): List of durations from the row.

        Returns:
            int: Column index corresponding to the closest duration.
        """
        duration_values_floats = [float(d) for d in duration_range]
        closest_diff = min(abs(val - duration) for val in duration_values_floats)
        closest_relative_index = [
                       i for i, val in enumerate(duration_values_floats)
                       if abs(val - duration) == closest_diff
                   ][-1]
        offset_column = self._get_null_offset(row, self._duration_column_range[0])
        return closest_relative_index + offset_column

    def _get_null_offset(self, row_index: int, start_col: int) -> int:
        """
        Finds the first non-null column starting from start_col in the specified row.

        Args:
            row_index (int): Row index.
            start_col (int): Starting column index.

        Returns:
            int: Index of first non-null column.

        Raises:
            IndexError: If the row index is out of bounds.
        """
        reader = self._csv_data

        if row_index >= len(reader):
            raise IndexError(ErrorMessages.INDEX_OUT_OF_BOUNDS.format(row_index))

        row = reader[row_index]
        for i in range(start_col, len(row)):
            if row[i].strip():
                return i

        return 0

    def get_yeast_type_index(self, yeast_type):
        """
        Returns the index of the specified yeast type.

        Args:
            yeast_type (str): Name of the yeast type.

        Returns:
            int: Index of the yeast type.

        Raises:
            ValueError: If the yeast type is not found.
        """
        yeast_type_row = self._configuration.get_yeast_types()
        try:
            return yeast_type_row.index(yeast_type)
        except ValueError:
            raise ValueError(ErrorMessages.UNKNOWN_YEAST_TYPE.format(yeast_type, yeast_type_row))

    def get_yeast_percentage(self, yeast_type, duration_column) -> float:
        """
        Retrieves the yeast percentage from the CSV for a specific yeast type and duration.

        Args:
            yeast_type (str): Type of yeast.
            duration_column (int): Column index for duration.

        Returns:
            float: Yeast percentage value.
        """
        yeast_type_row = self.get_yeast_type_index(yeast_type)
        return float(self.get_cell_value(yeast_type_row, duration_column))

    @property
    def temperature_value_range(self) -> list[float]:
        """
        Property for accessing the cached list of temperature values.

        Returns:
            list[float]: List of temperature values.
        """
        return self._temperature_value_range

    def get_yeast_types(self):
        """
        Retrieves the list of yeast types from the configuration.

        Returns:
            list[str]: List of yeast types.
        """
        return self._configuration.get_yeast_types()
