import pytest
import pandas as pd
import io
import boto3
from moto import mock_aws
from obfuscator.read_file import read_file


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


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame with PII fields."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
            "email": ["alice@example.com", "bob@example.com"],
            "age": [25, 30],
        }
    )


@mock_aws
def test_read_file_csv(mock_s3_bucket):
    """Test reading a CSV file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.csv"

    csv_content = "name,email,age\nAlice,alice@example.com,25\nBob,bob@example.com,30"
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=csv_content)

    df = read_file(bucket_name, object_key, "csv")

    assert isinstance(df, pd.DataFrame), "Expected a pandas DataFrame"
    assert not df.empty, "DataFrame should not be empty"
    assert df.shape == (2, 3), f"Expected shape (2, 3), got {df.shape}"
    assert df.iloc[0]["name"] == "Alice", "First row name should be 'Alice'"
    assert df.iloc[1]["age"] == 30, "Second row age should be 30"


@mock_aws
def test_read_file_json(mock_s3_bucket):
    """Test reading a JSON file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.json"
    json_content = """
    [
        {"name": "Alice", "email": "alice@example.com", "age": 25},
        {"name": "Bob", "email": "bob@example.com", "age": 30}
    ]
    """
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=json_content)

    df = read_file(bucket_name, object_key, "json")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 2  # check rows
    assert len(df.columns) == 3  # check columns
    assert df.loc[0, "name"] == "Alice"
    assert df.loc[1, "age"] == 30


@mock_aws
def test_read_file_parquet(mock_s3_bucket):
    """Test reading a Parquet file from S3."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.parquet"

    import pyarrow as pa
    import pyarrow.parquet as pq

    data = [
        pa.array(["Alice", "Bob"]),
        pa.array(["alice@example.com", "bob@example.com"]),
        pa.array([25, 30]),
    ]
    table = pa.Table.from_arrays(data, ["name", "email", "age"])
    with io.BytesIO() as f:
        pq.write_table(table, f)
        f.seek(0)
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=f.read())

    df = read_file(bucket_name, object_key, "parquet")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.shape == (2, 3)
    assert df.iloc[0]["name"] == "Alice"
    assert df.iloc[1]["age"] == 30


@mock_aws
def test_read_file_empty(mock_s3_bucket):
    """Test reading an empty file from S3 (all formats)."""
    s3, bucket_name = mock_s3_bucket
    for file_format in ["csv", "json", "parquet"]:
        object_key = f"empty.{file_format}"
        s3.put_object(Bucket=bucket_name, Key=object_key, Body="")

        df = read_file(bucket_name, object_key, file_format)
        assert isinstance(df, pd.DataFrame)
        assert df.empty


@mock_aws
def test_read_file_invalid_format(mock_s3_bucket):
    """Test handling of invalid file formats."""
    s3, bucket_name = mock_s3_bucket
    object_key = "test.txt"
    s3.put_object(Bucket=bucket_name, Key=object_key, Body="some text")

    with pytest.raises(ValueError, match="Unsupported file format: txt"):
        read_file(bucket_name, object_key, "txt")


@mock_aws
def test_read_file_nonexistent_key(mock_s3_bucket):
    """Test handling of nonexistent S3 keys."""
    s3, bucket_name = mock_s3_bucket
    object_key = "nonexistent.csv"

    with pytest.raises(RuntimeError, match="S3 Client Error: An error occurred"):
        read_file(bucket_name, object_key, "csv")
