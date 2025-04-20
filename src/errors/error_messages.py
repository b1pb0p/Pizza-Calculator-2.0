class ErrorMessages:
    INVALID_FERMENTATION = (
        "Invalid fermentation time combination: " 
        "the time at the given temperatures may be too long or unsupported.\n"
        "Please check the room and fridge fermentation durations."
                            )
    NO_CALCULATOR_FOUND = "No calculator found for: {}"
    MISMATCH_FERMENTATION = "Invalid configuration: {} fermentation is not 0"
    INDEX_OUT_OF_BOUNDS = "Index {} is out of bounds for the given data range."
    TEMPERATURE_NOT_FOUND = "Temperature {} not found in temperature value range."
    UNKNOWN_YEAST_TYPE = "Yeast type '{}' not found in configuration yeast types: {}"
    MISSING_TEMPERATURES = "Missing temperature values: at least one temperature must be set for fermentation."




