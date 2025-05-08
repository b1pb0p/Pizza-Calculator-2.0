"""
utilities.py

This file contains utility methods for the PizzaRecipe class.
"""


def auto_property(attr, recalculate_function_name=None):
    """
    Creates a property with a getter and setter that automatically recalculates a related function
    when the property value is set.

    Args:
        attr (str): The name of the attribute to be managed by the property.
        recalculate_function_name (str, optional): The name of the function to call for recalculation
            when the property value changes. Defaults to None.

    Returns:
        property: The property with custom getter and setter methods.
    """
    private = f"_{attr}"

    def getter(self):
        return getattr(self, private)

    def setter(self, value):
        if value != getattr(self, private):
            setattr(self, private, value)

            if recalculate_function_name:
                getattr(self, recalculate_function_name)()

    return property(getter, setter)
