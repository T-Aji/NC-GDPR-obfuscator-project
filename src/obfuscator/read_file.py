import pandas as pd
import boto3
import pyarrow
import pyarrow.parquet as pq
import io
import logging
from pandas.errors import EmptyDataError
from botocore.exceptions import ClientError


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def read_file(bucket_name: str, object_key: str, file_format: str) -> pd.DataFrame:
    """Reads a file from S3 and returns the appropriate DataFrame.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key of the object in the S3 bucket.
        file_format (str): The format of the file (csv, json, parquet).

    Returns:
        pd.DataFrame: The DataFrame containing the file data.

    Raises:
        ValueError: If the file format is unsupported.
        RuntimeError: If there is an error reading the file from S3.
    """
    if file_format not in ["csv", "json", "parquet"]:
        raise ValueError(f"Unsupported file format: {file_format}")
    s3_client = boto3.client("s3")
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_data = response["Body"].read()
        file_buffer = io.BytesIO(file_data)

        if file_format == "csv":
            return pd.read_csv(file_buffer)
        elif file_format == "json":
            return pd.read_json(file_buffer)
        elif file_format == "parquet":
            return pq.read_table(file_buffer).to_pandas()
    except (EmptyDataError, pyarrow.lib.ArrowInvalid, ValueError):
        logger.warning(f"Empty {file_format} file: {bucket_name}/{object_key}")
        return pd.DataFrame()
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.error(f"File not found: {bucket_name}/{object_key}")
        else:
            logger.error(f"S3 Client Error: {e}")
        raise RuntimeError(f"S3 Client Error: {e}")
    except Exception as e:
        logger.error(f"Error reading {file_format} file from S3: {e}")
        raise RuntimeError(f"Error reading {file_format} file from S3: {e}")
