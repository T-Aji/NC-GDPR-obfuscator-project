import pytest
import json
import os
import sys
import boto3
from moto import mock_aws
from obfuscator.main import obfuscator


@pytest.fixture
def mock_s3():
    """Fixture to mock AWS S3 in the EU West 2 (London) region."""
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


def test_obfuscator_missing_args(capsys):
    """
    Test that the script exits with an error if no arguments are provided.
    """
    with pytest.raises(SystemExit) as e:
        # Simulate no command-line arguments
        sys.argv = ["main.py"]
        obfuscator()

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Usage: obfuscator" in captured.out


def test_obfuscator_invalid_json(capsys):
    """
    Test that the script exits with an error if the JSON input is invalid.
    """
    with pytest.raises(SystemExit) as e:
        # Simulate invalid JSON input
        sys.argv = ["main.py", "invalid-json"]
        obfuscator()

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
        sys.argv = ["main.py", json.dumps({"pii_fields": ["name", "email"]})]
        obfuscator()

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Missing required S3 file location" in captured.out


def test_obfuscator_valid_input(tmpdir, mock_s3):
    """
    Test that the script produces the
    correct output file when given valid input.
    """
    # Create a temporary output directory
    output_dir = tmpdir.mkdir("output")

    # Simulate valid JSON input
    json_input = json.dumps(
        {
            "file_to_obfuscate": f"s3://{mock_s3}/file.csv",
            "pii_fields": ["name", "email"],
        }
    )

    # Simulate command-line arguments
    sys.argv = ["main.py", json_input]

    # Run the obfuscator function
    obfuscator(output_dir)

    # Check that the output file was created
    output_file = os.path.join(output_dir, "output.csv")
    # Debug: Print the output file path
    print(f"Output file path: {output_file}")
    # Debug: List files in the output directory
    print(f"Files in output directory: {os.listdir(output_dir)}")

    assert os.path.exists(output_file), f"Output file not found: {output_file}"

    # Check the contents of the output file
    with open(output_file, "rb") as f:
        file_contents = f.read()
        # Debug: Print the file contents
        print(f"File contents: {file_contents}")
        assert b"***,***" in file_contents  # Check PII fields are obfuscated


def test_obfuscator_invalid_s3_uri(capsys):
    """Test that the script exits with an error if the S3 URI is invalid."""
    with pytest.raises(SystemExit) as e:
        # Simulate JSON input with an invalid S3 URI
        sys.argv = [
            "main.py",
            json.dumps(
                {"file_to_obfuscate": "invalid-uri", "pii_fields": ["name", "email"]}
            ),
        ]
        obfuscator()

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Invalid S3 URI format" in captured.out


def test_obfuscator_unsupported_file_format(capsys):
    """
    Test that the script exits with an error if the file format is unsupported.
    """
    with pytest.raises(SystemExit) as e:
        # Simulate JSON input with an unsupported file format
        sys.argv = [
            "main.py",
            json.dumps(
                {
                    "file_to_obfuscate": "s3://my-bucket/file.txt",
                    "pii_fields": ["name", "email"],
                }
            ),
        ]
        obfuscator()

    # Check the exit code
    assert e.value.code == 1

    # Check the error message
    captured = capsys.readouterr()
    assert "Unsupported file format" in captured.out
