import pytest
import time
import os
import json
import pandas as pd
import pyarrow.parquet as pq
import boto3
from moto import mock_aws
from src.main import process_s3_file

# Fixture to create test files
@pytest.fixture(scope="module")
def setup_test_files():
    """Create test files (CSV, JSON, Parquet) of approximately 1MB."""
    csv_file = "test_file.csv"
    json_file = "test_file.json"
    parquet_file = "test_file.parquet"
    
    # Generate a 1MB CSV file
    data = {
        "id": range(1, 15651),  # Increased rows to ~15650 for ~1MB
        "name": ["John Doe"] * 15650,
        "email": ["john.doe@example.com"] * 15650,
        "course": ["Software Engineering"] * 15650,
        "graduation_date": ["2024-03-31"] * 15650,
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    
    # Generate a 1MB JSON file
    json_data = [
        {
            "id": i,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "course": "Software Engineering",
            "graduation_date": "2024-03-31",
        }
        for i in range(1, 7801)  # ~7800 rows for ~1MB
    ]
    with open(json_file, "w") as f:
        json.dump(json_data, f)
    
    # Generate a 1MB Parquet file
    # Parquet is highly compressed, so we need more rows to reach ~1MB
    parquet_data = {
        "id": range(1, 191001),  # Increased rows to ~191,000 for ~1MB
        "name": ["John Doe"] * 191000,
        "email": ["john.doe@example.com"] * 191000,
        "course": ["Software Engineering"] * 191000,
        "graduation_date": ["2024-03-31"] * 191000,
    }
    parquet_df = pd.DataFrame(parquet_data)
    parquet_df.to_parquet(parquet_file, index=False)
    
    # Validate file sizes
    csv_size_mb = os.path.getsize(csv_file) / (1024 * 1024)
    json_size_mb = os.path.getsize(json_file) / (1024 * 1024)
    parquet_size_mb = os.path.getsize(parquet_file) / (1024 * 1024)
    
    print(f"Generated file sizes: CSV={csv_size_mb:.2f} MB, JSON={json_size_mb:.2f} MB, Parquet={parquet_size_mb:.2f} MB")
    
    yield csv_file, json_file, parquet_file
    
    # Clean up test files
    os.remove(csv_file)
    os.remove(json_file)
    os.remove(parquet_file)

# Fixture to mock AWS S3
@pytest.fixture(scope="module")
def mock_s3(setup_test_files):
    """Mock AWS S3 and upload test files to a mock bucket."""
    with mock_aws():
        s3_client = boto3.client("s3", region_name="eu-west-2")
        bucket_name = "test-bucket"
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}                    
        )
        
        csv_file, json_file, parquet_file = setup_test_files
        
        # Upload test files to the mock S3 bucket
        s3_client.upload_file(csv_file, bucket_name, csv_file)
        s3_client.upload_file(json_file, bucket_name, json_file)
        s3_client.upload_file(parquet_file, bucket_name, parquet_file)
        
        yield bucket_name

# Helper function to calculate file size in MB
def get_file_size_mb(file_path):
    """Calculate the size of a file in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

# Performance test for CSV files
def test_csv_performance(mock_s3, setup_test_files):
    """Test the performance of processing a 1MB CSV file."""
    csv_file, _, _ = setup_test_files
    json_input = json.dumps({
        "file_to_obfuscate": f"s3://{mock_s3}/{csv_file}",
        "pii_fields": ["name", "email"]
    })
    
    start_time = time.time()
    process_s3_file(json_input)
    end_time = time.time()
    
    runtime = end_time - start_time
    file_size_mb = get_file_size_mb(csv_file)
    print(f"CSV Processing Time: {file_size_mb:.2f} MB in {runtime:.2f} seconds")
    assert runtime < 60, "CSV processing took longer than 60 seconds."

# Performance test for JSON files
def test_json_performance(mock_s3, setup_test_files):
    """Test the performance of processing a 1MB JSON file."""
    _, json_file, _ = setup_test_files
    json_input = json.dumps({
        "file_to_obfuscate": f"s3://{mock_s3}/{json_file}",
        "pii_fields": ["name", "email"]
    })
    
    start_time = time.time()
    process_s3_file(json_input)
    end_time = time.time()
    
    runtime = end_time - start_time
    file_size_mb = get_file_size_mb(json_file)
    print(f"JSON Processing Time: {file_size_mb:.2f} MB in {runtime:.2f} seconds")
    assert runtime < 60, "JSON processing took longer than 60 seconds."

# Performance test for Parquet files
def test_parquet_performance(mock_s3, setup_test_files):
    """Test the performance of processing a 1MB Parquet file."""
    _, _, parquet_file = setup_test_files
    json_input = json.dumps({
        "file_to_obfuscate": f"s3://{mock_s3}/{parquet_file}",
        "pii_fields": ["name", "email"]
    })
    
    start_time = time.time()
    process_s3_file(json_input)
    end_time = time.time()
    
    runtime = end_time - start_time
    file_size_mb = get_file_size_mb(parquet_file)
    print(f"Parquet Processing Time: {file_size_mb:.2f} MB in {runtime:.2f} seconds")
    assert runtime < 60, "Parquet processing took longer than 60 seconds."