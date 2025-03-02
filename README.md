# GDPR Obfuscator

The **GDPR Obfuscator** is a Python library designed to help you obfuscate personally identifiable information (PII) in files stored in AWS S3. It supports CSV, JSON, and Parquet file formats and ensures compliance with GDPR requirements by replacing sensitive data with `***`.

## Features
- **Obfuscation of PII**: Replace specified fields in your data with `***`.
- **Multiple File Formats**: Supports CSV (MVP), JSON, and Parquet files.
- **AWS S3 Integration**: Seamlessly reads and writes files from/to S3 buckets.
- **CLI Support**: Includes a command-line interface for easy integration into workflows.
- **Modular Design**: Easily extendable to support additional file formats or obfuscation methods.

---

## Installation

You can install the GDPR Obfuscator via `pip`:

```bash
pip install obfuscator
```

Alternatively, you can install it directly from the source:

```bash
git clone https://github.com/T-Aji/NC-GDPR-obfuscator-project.git
cd NC-GDPR-obfuscator-project
pip install .
```

---

## Usage

### As a Python Library

You can use the GDPR Obfuscator as a library in your Python code:

```python
from obfuscator import process_s3_file

# JSON input specifying the S3 file and PII fields
json_input = {
    "file_to_obfuscate": "s3://my-bucket/path/to/file.csv",
    "pii_fields": ["name", "email"]
}

# Process the file and get the obfuscated byte stream
output_bytes = process_s3_file(json.dumps(json_input))

# Save the obfuscated file to a new S3 location
import boto3
s3_client = boto3.client("s3")
s3_client.put_object(Bucket="my-bucket", Key="path/to/obfuscated_file.csv", Body=output_bytes)
```

### As a Command-Line Tool

The GDPR Obfuscator also includes a CLI for easy integration into scripts or workflows:

```bash
obfuscator '{"file_to_obfuscate": "s3://my-bucket/path/to/file.csv", "pii_fields": ["name", "email"]}'
```

The obfuscated file will be saved locally as `output.csv` (or the appropriate format based on the input file).

---

## Configuration

### Input JSON Format

The tool expects a JSON input with the following structure:

```json
{
    "file_to_obfuscate": "s3://my-bucket/path/to/file.csv",
    "pii_fields": ["field1", "field2"]
}
```

- **`file_to_obfuscate`**: The S3 URI of the file to process.
- **`pii_fields`**: A list of fields to obfuscate.

### AWS Credentials

The tool uses the `boto3` library to interact with AWS S3. Ensure your AWS credentials are configured using one of the following methods:
- AWS CLI: Run `aws configure` and provide your credentials.
- Environment variables: Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
- IAM roles: If running on AWS infrastructure (e.g., EC2, Lambda), attach an IAM role with the necessary permissions.

---

## Testing

The GDPR Obfuscator includes a suite of unit tests to ensure functionality and reliability. To run the tests:

1. Install the development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the tests using `pytest`:
   ```bash
   pytest tests/
   ```

### Example Test Cases
- **Input Validation**: Ensures invalid inputs are handled gracefully.
- **Obfuscation Logic**: Verifies that PII fields are correctly replaced with `***`.
- **File Formats**: Tests CSV, JSON, and Parquet file handling.

---

## Contributing

We welcome contributions to the GDPR Obfuscator! Here’s how you can help:

1. **Report Issues**: If you find a bug or have a feature request, please open an issue on GitHub.
2. **Submit Pull Requests**: Fork the repository, make your changes, and submit a pull request.
3. **Improve Documentation**: Help us improve the README, docstrings, or other documentation.

### Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/gdpr-obfuscator.git
   cd gdpr-obfuscator
   ```

2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run tests and linting:
   ```bash
   pytest tests/
   flake8 src/
   ```

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Support

For questions, issues, or feedback, please open an issue on the [GitHub repository](https://github.com/your-repo/gdpr-obfuscator).

---

## Acknowledgments

- **Author**: Tolu Ajibade
- **Inspiration**: GDPR compliance requirements for data anonymization.
- **Tools Used**: `boto3`, `pandas`, `pyarrow`, `pytest`.

---

