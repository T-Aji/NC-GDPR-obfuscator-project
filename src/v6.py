import boto3
import pandas as pd
import io
import json
import logging
from pandas.errors import EmptyDataError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_csv_from_s3(bucket_name: str, object_key: str) -> pd.DataFrame:
    """Read a CSV file from S3 and return a DataFrame."""
    s3_client = boto3.client("s3")
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_data = response["Body"].read()
        return pd.read_csv(io.BytesIO(file_data))
    except EmptyDataError:
        logger.warning(f"Empty CSV file: {bucket_name}/{object_key}")
        return pd.DataFrame()  # Return an empty DataFrame for empty files
    except Exception as e:
        logger.error(f"Error reading CSV file from S3: {e}")
        raise RuntimeError(f"Error reading CSV file from S3: {e}")
    
def obfuscate_pii(dataframe: pd.DataFrame, pii_fields: list) -> pd.DataFrame:
    """Obfuscate specified PII fields in the DataFrame."""
    obfuscated_df = dataframe.copy()
    for field in pii_fields:
        if field in obfuscated_df.columns:
            obfuscated_df[field] = "***"
    return obfuscated_df

def write_csv_to_bytes(dataframe: pd.DataFrame) -> io.BytesIO:
    """Convert a DataFrame to a CSV byte stream."""
    buffer = io.BytesIO()
    dataframe.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

def process_s3_file(json_input: str) -> io.BytesIO:
    """Process a CSV file from S3, obfuscate PII fields, and return a byte stream."""
    try:
        input_data = json.loads(json_input)
        s3_uri = input_data.get("file_to_obfuscate")
        pii_fields = input_data.get("pii_fields", [])
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        raise ValueError(f"Invalid JSON input: {e}")
    
    if not s3_uri:
        logger.error("Missing required S3 file location.")
        raise ValueError("Missing required S3 file location.")
    
    try:
        parts = s3_uri.replace("s3://", "").split("/", 1)
        bucket_name, object_key = parts[0], parts[1]
        
        df = read_csv_from_s3(bucket_name, object_key)
        obfuscated_df = obfuscate_pii(df, pii_fields)
        
        return write_csv_to_bytes(obfuscated_df)
    except Exception as e:
        logger.error(f"Error processing S3 file: {e}")
        raise RuntimeError(f"Error processing S3 file: {e}")