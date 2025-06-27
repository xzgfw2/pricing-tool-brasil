def calculation_division(df, column1, column2):
    if column1 in df.columns and column2 in df.columns:

        value1 = round(float(df[column1].sum()), 2)
        value2 = round(float(df[column2].sum()), 2)

        return round(value1 / value2, 2) if value2 != 0 else None  # Preverni divisão por zero
    else:
        return
