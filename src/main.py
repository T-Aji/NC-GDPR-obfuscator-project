import json
import io
import logging
from src.read_file import read_file
from src.obfuscate_pii import obfuscate_pii
from src.write_file import write_file

# def process_s3_file(json_input: str) -> io.BytesIO:
#     """Process file from S3, obfuscate PII fields, and return as a byte stream.
    
#     Args:
#         json_input (str): JSON string containing the S3 URI and PII fields.
    
#     Returns:
#         io.BytesIO: The byte stream of the processed file.
    
#     Raises:
#         ValueError: If the JSON input is invalid or missing required fields.
#         RuntimeError: If there is an error processing the file.
#     """
#     try:
#         input_data = json.loads(json_input)
#         s3_uri = input_data.get("file_to_obfuscate")
#         pii_fields = input_data.get("pii_fields", [])
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Invalid JSON input: {e}")
    
#     if not s3_uri:
#         raise ValueError("Missing required S3 file location.")
    
#     parts = s3_uri.replace("s3://", "").split("/", 1)
#     bucket_name, object_key = parts[0], parts[1]
#     file_format = object_key.split(".")[-1]
    
#     df = read_file(bucket_name, object_key, file_format)
#     obfuscated_df = obfuscate_pii(df, pii_fields)
    
#     return write_file(obfuscated_df, file_format)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_s3_file(json_input: str) -> io.BytesIO:
    """Process file from S3, obfuscate PII fields, and return as a byte stream.
    
    Args:
        json_input (str): JSON string containing the S3 URI and PII fields.
    
    Returns:
        io.BytesIO: The byte stream of the processed file.
    
    Raises:
        ValueError: If the JSON input is invalid or missing required fields.
        RuntimeError: If there is an error processing the file.
    """
    try:
        # Parse JSON input
        input_data = json.loads(json_input)
        s3_uri = input_data.get("file_to_obfuscate")
        pii_fields = input_data.get("pii_fields", [])
        
        # Validate input
        if not s3_uri:
            raise ValueError("Missing required S3 file location.")
        
        # Extract bucket name, object key, and file format
        parts = s3_uri.replace("s3://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError("Invalid S3 URI format.")
        bucket_name, object_key = parts[0], parts[1]
        file_format = object_key.split(".")[-1]
        
        # Validate file format
        if file_format not in ["csv", "json", "parquet"]:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        # Read file from S3
        logger.info(f"Reading file from S3: {s3_uri}")
        df = read_file(bucket_name, object_key, file_format)
        
        # Obfuscate PII fields
        logger.info(f"Obfuscating PII fields: {pii_fields}")
        obfuscated_df = obfuscate_pii(df, pii_fields)
        
        # Write obfuscated data to byte stream
        logger.info(f"Writing obfuscated data to byte stream in {file_format} format")
        return write_file(obfuscated_df, file_format)
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        raise ValueError(f"Invalid JSON input: {e}")
    except ValueError as e:
        # Re-raise ValueError for input validation errors
        logger.error(f"Input validation error: {e}")
        raise
    except Exception as e:
        # Wrap unexpected errors in RuntimeError
        logger.error(f"Error processing S3 file: {e}")
        raise RuntimeError(f"Error processing S3 file: {e}")


if __name__ == "__main__":
    # Example usage
    json_input = '{"file_to_obfuscate": "s3://your-bucket/your-file.csv", "pii_fields": ["name", "email"]}'
    try:
        # Process the file
        output_bytes = process_s3_file(json_input)
        
        # Save the output to a file (for demonstration purposes)
        output_filename = "output.csv"
        with open(output_filename, "wb") as f:
            f.write(output_bytes.getvalue())
        print(f"File processed and saved to {output_filename}")
    except Exception as e:
        print(f"Error: {e}")