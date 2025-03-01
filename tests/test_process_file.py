import pytest
import json
import io
import boto3
from moto import mock_aws
from src.main import process_s3_file


@pytest.fixture(scope="function")
def mock_s3_bucket():
    """Fixture to create and return a mock S3 bucket."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        bucket_name = "mock-bucket"
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        yield s3, bucket_name


@mock_aws
def test_process_s3_file_csv(mock_s3_bucket):
    """Test end-to-end processing of a CSV file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.csv"
    csv_data = """
    id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com
    """
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_data)

    json_input = json.dumps(
        {
            "file_to_obfuscate": f"s3://{bucket_name}/{object_key}",
            "pii_fields": ["name", "email"],
        }
    )

    byte_stream = process_s3_file(json_input)
    output_content = byte_stream.getvalue().decode("utf-8")

    assert "***" in output_content
    assert "1" in output_content


@mock_aws
def test_process_s3_file_json(mock_s3_bucket):
    """Test end-to-end processing of a JSON file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.json"
    json_data = """
    [{"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}]
    """
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=json_data)

    json_input = json.dumps(
        {
            "file_to_obfuscate": f"s3://{bucket_name}/{object_key}",
            "pii_fields": ["name", "email"],
        }
    )

    byte_stream = process_s3_file(json_input)
    output_content = byte_stream.getvalue().decode("utf-8")

    assert "***" in output_content
    assert "1" in output_content


@mock_aws
def test_process_s3_file_parquet(mock_s3_bucket):
    """Test end-to-end processing of a Parquet file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.parquet"
    import pyarrow as pa
    import pyarrow.parquet as pq

    data = [
        pa.array([1, 2]),
        pa.array(["Alice", "Bob"]),
        pa.array(["alice@example.com", "bob@example.com"]),
    ]
    table = pa.Table.from_arrays(data, ["id", "name", "email"])
    with io.BytesIO() as f:
        pq.write_table(table, f)
        f.seek(0)
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=f.read())

    json_input = json.dumps(
        {
            "file_to_obfuscate": f"s3://{bucket_name}/{object_key}",
            "pii_fields": ["name", "email"],
        }
    )

    byte_stream = process_s3_file(json_input)
    # validate that it is parquet.
    try:
        pq.read_table(io.BytesIO(byte_stream.getvalue()))
    except Exception as e:
        assert False, f"Parquet file is invalid: {e}"


@mock_aws
def test_process_s3_file_empty(mock_s3_bucket):
    """Test processing an empty file from S3."""
    s3, bucket_name = mock_s3_bucket
    for file_format in ["csv", "json", "parquet"]:
        object_key = f"empty.{file_format}"
        s3.put_object(Bucket=bucket_name, Key=object_key, Body="")

        json_input = json.dumps(
            {
                "file_to_obfuscate": f"s3://{bucket_name}/{object_key}",
                "pii_fields": ["name", "email"],
            }
        )

        byte_stream = process_s3_file(json_input)
        assert isinstance(byte_stream, io.BytesIO)
        assert byte_stream.getvalue()


def test_process_s3_file_invalid_input_json():
    """Test handling of invalid JSON input."""
    invalid_json = "{"
    with pytest.raises(ValueError, match="Invalid JSON input"):
        process_s3_file(invalid_json)


def test_process_s3_file_missing_fields():
    """Test handling of JSON input missing required fields."""
    missing_fields_json = json.dumps({"pii_fields": ["name"]})
    with pytest.raises(ValueError, match="Missing required S3 file location"):
        process_s3_file(missing_fields_json)


@mock_aws
def test_process_s3_file_nonexistent_key(mock_s3_bucket):
    """Test handling of nonexistent S3 keys."""
    s3, bucket_name = mock_s3_bucket
    object_key = "nonexistent.csv"

    json_input = json.dumps(
        {
            "file_to_obfuscate": f"s3://{bucket_name}/{object_key}",
            "pii_fields": ["name", "email"],
        }
    )

    with pytest.raises(RuntimeError, match="Error processing S3 file:"):
        process_s3_file(json_input)


@mock_aws
def test_process_s3_file_no_pii_fields(mock_s3_bucket):
    """Test processing a file without specifying PII fields."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.csv"
    csv_data = """
    id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com
    """
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_data)

    json_input = json.dumps({"file_to_obfuscate": f"s3://{bucket_name}/{object_key}"})

    byte_stream = process_s3_file(json_input)
    output_content = byte_stream.getvalue().decode("utf-8")

    assert "Alice" in output_content
    assert "bob@example.com" in output_content


@mock_aws
def test_process_s3_file_invalid_s3_uri(mock_s3_bucket):
    """Test handling of invalid S3 URI format."""
    json_input = json.dumps(
        {"file_to_obfuscate": "invalid-uri", "pii_fields": ["name"]}
    )

    with pytest.raises(ValueError, match="Invalid S3 URI format"):
        process_s3_file(json_input)
