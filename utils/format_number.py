def format_number(value):
    if isinstance(value, (int, float)):
        return "{:,.2f}".format(value)

    elif isinstance(value, str):
        value = value.strip()
        if value.replace('.', '', 1).isdigit() and (value.count('.') <= 1):
            try:
                number = float(value)
                return "{:,.2f}".format(number)
            except ValueError:
                return "Invalid value"
    return "Invalid value"
