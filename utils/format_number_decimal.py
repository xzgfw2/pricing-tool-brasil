def format_number_decimal(number, option="perc"):
    if number is None:
        return None
    new_number = float(number) if isinstance(number, str) else number
    signal = "+" if new_number > 0 else "-" if new_number < 0 else ""
    if option == "pp":
        return f"{signal}{abs(new_number):.1f} p.p."
    elif option == "perc":
        return f"{signal}{abs(new_number):.1f}%"
    else:
        return None
