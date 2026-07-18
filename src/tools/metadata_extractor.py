import pandas as pd

def extract_metadata(df: pd.DataFrame) -> dict:
    """
    Extract metadata from a pandas DataFrame.
    """

    row_count = len(df)
    column_count = len(df.columns)
    columns = df.columns.tolist()
    data_types = {column: str(dtype) for column, dtype in df.dtypes.items()}
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = df.select_dtypes(exclude="number").columns.tolist()
    missing_values = df.isnull().sum().to_dict()
    sample_data = df.head(5).to_dict(orient="records")

    return {
    "row_count": row_count,
    "column_count": column_count,
    "columns": columns,
    "data_types": data_types,
    "numeric_columns": numeric_columns,
    "categorical_columns": categorical_columns,
    "missing_values": missing_values,
    "sample_data": sample_data,
}