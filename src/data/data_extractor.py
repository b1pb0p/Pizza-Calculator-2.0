import csv
from src.errors.error_messages import ErrorMessages
from src.configuration.configuration import Configuration


class DataExtractor:
    """
    Singleton class to extract yeast data from a CSV file based on temperature, duration, and yeast type.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataExtractor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """ Initializes the DataExtractor """
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

        :return: List of lists representing the CSV data.
        """
        with open(self._yeast_data_file, newline='', encoding='utf-8') as csvfile:
            return list(csv.reader(csvfile))

    def get_cell_value(self, row, column):
        """
        Retrieves the value at a specific row and column (1-based index).

        :param row: Row number.
        :param column: Column number (1-based).
        :return: Value at the specified cell.
        """
        return self._csv_data[row][column]

    def get_temperature_value_range(self):
        """
        Returns a list of temperature strings found in the CSV, within a configured row range.

        :return: List of temperature values as strings.
        """
        column_index = self._temperature_column
        row_start, row_end = self._temperature_range
        reader = self._csv_data

        return [
            float(reader[i][column_index].strip())
            for i in range(row_start, row_end)
            if i < len(reader) and column_index < len(reader[i]) and reader[i][column_index].strip()
        ]

    def get_duration_value_range(self, row_index):
        """
        Returns a list of duration values in a specified row
        :param row_index: Row index (1-based).
        :return: List of durations as strings.
        """
        row_index = row_index
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

    def get_duration_range_by_temperature(self, temperature):
        """
        Retrieves the list of durations available for a given temperature.

        :param temperature: The temperature as a float (e.g., 4.0).
        :return: List of duration values (floats) for the given temperature.
        """
        temperature_row_index = self.get_temperature_row_index(temperature, strict=False)
        return self.get_duration_value_range(temperature_row_index)

    def get_temperature_row_index(self, temperature: float, strict: bool = True) -> int:
        """
        Given a float temperature value, returns the corresponding row index
        within the temperature_value_range list. Adjusts with the start of the temperature row range
        :param temperature: Temperature as float (e.g., 3.9)
        :param strict: If True, only exact match is accepted. If False, the closest match will be used.
        :return: Corresponding row index in the yeast data file
        :raises: ValueError if temperature is not found and strict is True
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

    def get_closest_duration_column(self, duration, temperature):
        """
        Retrieves the column index corresponding to the closest duration value
        for a given temperature.

        :param duration: Duration value as float
        :param temperature: Temperature value as float.
        :return: Closest matching duration column index (0-based).
        """
        temperature_row_index = self.get_temperature_row_index(temperature, strict=False)
        duration_values = self.get_duration_value_range(temperature_row_index)
        closest_duration_column = self._find_closest_duration_column(
            temperature_row_index,
            duration,
            duration_values)

        return closest_duration_column

    def _find_closest_duration_column(self, row, duration, duration_range):
        """
        Finds the closest duration column for a given duration value in a specific row
        :param row: Row index.
        :param duration: Duration value to match (float).
        :param duration_range: List of durations from the row.
        :return: Column index corresponding to the closest duration.
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
        Finds the first non-null column starting from start_col in the specified row
        :param row_index: Row index
        :param start_col: Starting column index.
        :return: Index of first non-null column.
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
        Returns the index of the specified yeast type from the config yeast types list
        :param yeast_type: Name of yeast type.
        :return: Index of the yeast type.
        :raises: ValueError if the yeast type is not found.
        """
        yeast_type_row = self._configuration.get_yeast_types()
        try:
            return yeast_type_row.index(yeast_type)
        except ValueError:
            raise ValueError(ErrorMessages.UNKNOWN_YEAST_TYPE.format(yeast_type, yeast_type_row))

    def get_yeast_percentage(self, yeast_type, duration_column):
        """
        Retrieves the yeast percentage from the CSV for a specific yeast type and duration
        :param yeast_type: Type of yeast (e.g., "IDY", "ADY").
        :param duration_column: Column index (1-based) for duration.
        :return: Yeast percentage as a string.
        """
        yeast_type_row = self.get_yeast_type_index(yeast_type)
        return self.get_cell_value(yeast_type_row, duration_column)

    @property
    def temperature_value_range(self):
        """
        Property for accessing the cached list of temperature values.

        :return: List of temperature values (as strings).
        """
        return self._temperature_value_range

    def get_yeast_types(self):
        """
        Retrieves the list of yeast types defined in the configuration file.

        :return: List of yeast type strings.
        """
        return self._configuration.get_yeast_types()

    @staticmethod
    def _find_closest_duration_value(duration: float, duration_range: list) -> float:
        """
        Finds the closest duration value from the given duration_range list.

        :param duration: Duration value to match (float).
        :param duration_range: List of duration strings or floats.
        :return: Closest matching duration value as float.
        """
        duration_values_floats = [float(d) for d in duration_range]
        closest = min(duration_values_floats, key=lambda val: abs(val - duration))
        return closest
