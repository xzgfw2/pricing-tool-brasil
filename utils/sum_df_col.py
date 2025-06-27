import polars as pl

def sum_df_col(df: pl.DataFrame, column: str) -> str:
    if column in df.columns:
        
        total = df[column].sum()
        formatted_total = f"{total:.2f}"

        return formatted_total
    else:
        return
