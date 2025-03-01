import pytest
import pandas as pd
import pyarrow.parquet as pq
import io
from src.write_file import write_file
from src.obfuscate_pii import obfuscate_pii


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame with PII fields."""
    return pd.DataFrame(
        {
            "student_id": [1234, 5678],
            "name": ["John Smith", "Jane Doe"],
            "email_address": ["j.smith@example.com", "j.doe@example.com"],
        }
    )


@pytest.fixture
def obfuscated_dataframe(sample_dataframe):
    """Fixture to provide an obfuscated DataFrame."""
    return obfuscate_pii(sample_dataframe, ["name", "email_address"])


def test_write_csv_to_bytes(obfuscated_dataframe):
    """Test converting an obfuscated DataFrame to a CSV byte stream."""
    byte_stream = write_file(obfuscated_dataframe, "csv")

    # Assertions
    assert isinstance(byte_stream, io.BytesIO)
    content = byte_stream.getvalue().decode("utf-8")
    assert "***" in content  # Ensure obfuscated values are present
    assert "student_id" in content  # Ensure non-PII fields are present


def test_write_json_to_bytes(obfuscated_dataframe):
    """Test converting an obfuscated DataFrame to a JSON byte stream."""
    byte_stream = write_file(obfuscated_dataframe, "json")
    assert isinstance(byte_stream, io.BytesIO)
    content = byte_stream.getvalue().decode("utf-8")
    assert "***" in content
    assert "student_id" in content
    # Check that it is valid json
    import json

    for line in content.splitlines():
        json.loads(line)


def test_write_parquet_to_bytes(obfuscated_dataframe):
    """Test converting an obfuscated DataFrame to a Parquet byte stream."""
    byte_stream = write_file(obfuscated_dataframe, "parquet")
    assert isinstance(byte_stream, io.BytesIO)
    # Try read the parquet file to validate it.
    try:
        pq.read_table(byte_stream)
    except Exception:
        assert False, "Parquet file created is invalid"


def test_write_empty_dataframe():
    """Test writing an empty DataFrame."""
    df = pd.DataFrame()
    for fmt in ["csv", "json", "parquet"]:
        byte_stream = write_file(df, fmt)
        assert isinstance(byte_stream, io.BytesIO)
        assert byte_stream.getvalue()


def test_write_dataframe_different_types():
    """Test writing a DataFrame with different data types."""
    df = pd.DataFrame(
        {"id": [1, 2, 3], "value": [3.14, 2.71, 1.61], "flag": [True, False, True]}
    )
    for fmt in ["csv", "json", "parquet"]:
        byte_stream = write_file(df, fmt)
        assert isinstance(byte_stream, io.BytesIO)
        content = byte_stream.getvalue()
        # Basic check for data representation in the output
        if fmt == "csv":
            assert "1,3.14,True" in content.decode("utf-8")
        elif fmt == "json":
            assert "3.14" in content.decode("utf-8")
        elif fmt == "parquet":
            try:
                pq.read_table(byte_stream)
            except Exception:
                assert False, "Parquet file created is invalid"
