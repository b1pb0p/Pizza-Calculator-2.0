
def auto_property(attr, recalculate_function_name=None):
    private = f"_{attr}"

    def getter(self):
        return getattr(self, private)

    def setter(self, value):
        if value != getattr(self, private):
            setattr(self, private, value)

            if recalculate_function_name:
                getattr(self, recalculate_function_name)()

    return property(getter, setter)
