import pytest
import pandas as pd
import json
import io
import time
import sys
import boto3
from moto import mock_aws
from src.v6 import read_csv_from_s3, obfuscate_pii, write_csv_to_bytes, process_s3_file


@pytest.fixture(scope="function")
def mock_s3_bucket():
    """Fixture to create and return a mock S3 bucket."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        bucket_name = "mock-bucket"
        
        # Create the mock S3 bucket
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
        )
        yield s3, bucket_name  # Provide S3 client & bucket name to tests


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame with PII fields."""
    return pd.DataFrame({
        "student_id": [1234, 5678],
        "name": ["John Smith", "Jane Doe"],
        "email_address": ["j.smith@example.com", "j.doe@example.com"],
    })


@pytest.fixture
def obfuscated_dataframe(sample_dataframe):
    """Fixture to provide an obfuscated DataFrame."""
    return obfuscate_pii(sample_dataframe, ["name", "email_address"])


@mock_aws
def test_read_csv_from_s3(mock_s3_bucket):
    """Test reading a CSV file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "mock-file.csv"
    
    # Upload a CSV file to the mock S3 bucket
    csv_data = "student_id,name,email_address\n1234,John Smith,j.smith@example.com\n"
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_data)
    
    # Read the CSV file from S3
    df = read_csv_from_s3(bucket_name, object_key)
    
    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert "name" in df.columns
    assert df.iloc[0]["name"] == "John Smith"


@mock_aws
def test_read_csv_from_s3_empty_file(mock_s3_bucket):
    """Test reading an empty CSV file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "empty.csv"
    
    # Upload an empty CSV file to the mock S3 bucket
    s3.put_object(Bucket=bucket_name, Key=object_key, Body="")
    
    # Read the CSV file from S3
    df = read_csv_from_s3(bucket_name, object_key)
    
    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert df.empty  # Ensure an empty DataFrame is returned


def test_obfuscate_pii(sample_dataframe):
    """Test obfuscation of PII fields."""
    pii_fields = ["name", "email_address"]
    obfuscated_df = obfuscate_pii(sample_dataframe, pii_fields)
    
    # Assertions
    assert all(obfuscated_df["name"] == "***")  # Ensure PII fields are obfuscated
    assert all(obfuscated_df["email_address"] == "***")
    assert all(obfuscated_df["student_id"] == sample_dataframe["student_id"])  # Non-PII fields should remain unchanged


def test_obfuscate_pii_with_missing_columns(sample_dataframe):
    """Test obfuscation when specified PII fields are missing."""
    obfuscated_df = obfuscate_pii(sample_dataframe, ["non_existent_column"])
    
    # Assertions
    assert obfuscated_df.equals(sample_dataframe)  # DataFrame should remain unchanged


def test_write_csv_to_bytes(obfuscated_dataframe):
    """Test converting an obfuscated DataFrame to a CSV byte stream."""
    byte_stream = write_csv_to_bytes(obfuscated_dataframe)
    
    # Assertions
    assert isinstance(byte_stream, io.BytesIO)
    content = byte_stream.getvalue().decode("utf-8")
    assert "***" in content  # Ensure obfuscated values are present
    assert "student_id" in content  # Ensure non-PII fields are present


def test_process_s3_file(mock_s3_bucket):
    """Test end-to-end processing of a CSV file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "mock-file.csv"
    
    # Upload a CSV file to the mock S3 bucket
    csv_data = "student_id,name,email_address\n1234,John Smith,j.smith@example.com\n"
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_data)
    
    # Prepare JSON input
    json_input = json.dumps({
        "file_to_obfuscate": f"s3://{bucket_name}/{object_key}",
        "pii_fields": ["name", "email_address"]
    })
    
    # Process the file
    byte_stream = process_s3_file(json_input)
    output_content = byte_stream.getvalue().decode("utf-8")
    
    # Assertions
    assert "***" in output_content  # Ensure PII fields are obfuscated
    assert "1234" in output_content  # Ensure non-PII fields are present


def test_process_s3_file_invalid_json():
    """Test handling of invalid JSON input."""
    invalid_json = "{"
    with pytest.raises(ValueError, match="Invalid JSON input"):
        process_s3_file(invalid_json)


def test_process_s3_file_missing_fields():
    """Test handling of JSON input missing required fields."""
    missing_fields_json = json.dumps({"pii_fields": ["name"]})
    with pytest.raises(ValueError, match="Missing required S3 file location"):
        process_s3_file(missing_fields_json)


def test_performance_large_file(mock_s3_bucket):
    """Test performance with a large CSV file (1MB)."""
    s3, bucket_name = mock_s3_bucket
    object_key = "large_test.csv"
    
    # Create a large CSV file (1MB)
    large_csv_data = "student_id,name,email_address\n" + ("1234,John Smith,j.smith@example.com\n" * 20000)
    
    # Upload the large CSV file to the mock S3 bucket
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=large_csv_data)
    
    # Prepare JSON input
    json_input = json.dumps({
        "file_to_obfuscate": f"s3://{bucket_name}/{object_key}",
        "pii_fields": ["name", "email_address"]
    })
    
    # Measure runtime
    start_time = time.time()
    byte_stream = process_s3_file(json_input)
    end_time = time.time()
    
    # Assertions
    assert isinstance(byte_stream, io.BytesIO)
    assert (end_time - start_time) < 60  # Runtime should be less than 1 minute

def test_obfuscate_pii_mixed_data_types():
    df = pd.DataFrame({
        "name": ["Alice", 123, None, "Bob"],
        "email": ["alice@example.com", "bob@example.com", None, 42],
        "age": [25, 30, 35, 40]
    })
    obfuscated_df = obfuscate_pii(df, ["name", "email"])

    assert all(obfuscated_df["name"].apply(lambda x: x == "***" if x is not None else True))
    assert all(obfuscated_df["email"].apply(lambda x: x == "***" if x is not None else True))
    assert obfuscated_df.loc[2, "name"] is None
    assert obfuscated_df.loc[2, "email"] is None
    assert all(obfuscated_df["age"] == df["age"])