import io
import pandas as pd

def write_file(dataframe: pd.DataFrame, file_format: str) -> io.BytesIO:
    """Convert a DataFrame to a byte stream in the specified format.
    
    Args:
        dataframe (pd.DataFrame): The DataFrame to convert.
        file_format (str): The format to convert to (csv, json, parquet).
    
    Returns:
        io.BytesIO: The byte stream of the converted DataFrame.
    
    Raises:
        ValueError: If the output format is unsupported.
        RuntimeError: If there is an error writing to bytes.
    """
    buffer = io.BytesIO()

    try:
        if file_format == "csv":
            dataframe.to_csv(buffer, index=False)
        elif file_format == "json":
            dataframe.to_json(buffer, orient="records", lines=True)
        elif file_format == "parquet":
            dataframe.to_parquet(buffer, index=False)
        else:
            raise ValueError(f"Unsupported output format: {file_format}")
        
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise RuntimeError(f"Error writing {file_format} to bytes: {e}")
