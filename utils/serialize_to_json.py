import json
import pandas as pd
import polars as pl
from decimal import Decimal

def convert_decimals(data):
    """Recursively convert Decimal objects to float."""
    if isinstance(data, dict):
        return {key: convert_decimals(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_decimals(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)  # ou str(data), dependendo do que você precisa
    else:
        return data

def serialize_to_json(data):
    """
    Serialize input data to JSON format.

    Args:
        data (list, dict, pd.DataFrame, pl.DataFrame, str): Input data to be serialized.

    Returns:
        str: JSON representation of the input data or empty string if input is empty string.
    """
    # Handle empty string case

    # if data == "":
    #     return ""

    if data is None:
        return ""

    if isinstance(data, (list, dict)):
        # Convert Decimal types to float
        data = convert_decimals(data)
        return json.dumps(data)

    elif isinstance(data, pd.DataFrame):
        # Convert Decimal types in the DataFrame to float
        data = data.applymap(lambda x: float(x) if isinstance(x, Decimal) else x)
        return data.to_json(orient='records')

    elif isinstance(data, pl.DataFrame):
        # Convert Decimal types in the Polars DataFrame to float
        data = data.with_columns(
            [pl.col(column).cast(pl.Float64) for column in data.columns if data[column].dtype == pl.Decimal]
        )
        return data.write_json()

    elif isinstance(data, (str, int, float)):
        return str(data)

    else:
        raise ValueError("Unsupported data type")
