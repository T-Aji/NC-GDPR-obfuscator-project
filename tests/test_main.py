import pytest
import json
import boto3
from moto import mock_aws
from obfuscator.main import obfuscator
import io


@pytest.fixture
def mock_s3():
    """Fixture to mock AWS S3 bucket."""
    with mock_aws():
        s3_client = boto3.client("s3", region_name="eu-west-2")
        bucket_name = "test-bucket"

        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )

        # Upload a sample CSV file to the mock S3 bucket
        s3_client.put_object(
            Bucket=bucket_name,
            Key="file.csv",
            Body=b"id,name,email\n1,John Doe,john.doe@example.com\n",
        )
        yield bucket_name


def test_obfuscator_valid_input(mock_s3):
    """
    Test that the script produces the correct output when given valid input.
    """
    # Simulate valid JSON input
    json_input = json.dumps(
        {
            "file_to_obfuscate": f"s3://{mock_s3}/file.csv",
            "pii_fields": ["name", "email"],
        }
    )

    # Run the obfuscator function
    output_bytes = obfuscator(json_input)

    # Check the type of the output
    assert isinstance(output_bytes, io.BytesIO)

    # Check the contents of the output
    output_content = output_bytes.getvalue()
    assert b"***,***" in output_content  # Check PII fields are obfuscated


def test_obfuscator_invalid_json(capsys):
    """
    Test that the script exits with an error if the JSON input is invalid.
    """
    with pytest.raises(SystemExit) as e:
        # Simulate invalid JSON input
        obfuscator("invalid-json")

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Invalid JSON input" in captured.out


def test_obfuscator_missing_s3_uri(capsys):
    """
    Test that the script exits with an error
    if the JSON input is missing the S3 URI.
    """
    with pytest.raises(SystemExit) as e:
        # Simulate JSON input missing the S3 URI
        obfuscator(json.dumps({"pii_fields": ["name", "email"]}))

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Missing required S3 file location" in captured.out


def test_obfuscator_invalid_s3_uri(capsys):
    """Test that the script exits with an error if the S3 URI is invalid."""
    with pytest.raises(SystemExit) as e:
        # Simulate JSON input with an invalid S3 URI
        obfuscator(
            json.dumps(
                {"file_to_obfuscate": "invalid-uri", "pii_fields": ["name", "email"]}
            )
        )

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Invalid S3 URI format" in captured.out


def test_obfuscator_unsupported_file_format(capsys, mock_s3):
    """
    Test that the script exits with an error if the file format is unsupported.
    """
    # Create a text file in s3
    s3_client = boto3.client("s3", region_name="eu-west-2")
    s3_client.put_object(
        Bucket="test-bucket",
        Key="file.txt",
        Body=b"id,name,email\n1,John Doe,john.doe@example.com\n",
    )

    with pytest.raises(SystemExit) as e:
        # Simulate JSON input with an unsupported file format
        obfuscator(
            json.dumps(
                {
                    "file_to_obfuscate": f"s3://{mock_s3}/file.txt",
                    "pii_fields": ["name", "email"],
                }
            )
        )

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Unsupported file format" in captured.out
