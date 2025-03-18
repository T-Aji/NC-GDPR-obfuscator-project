# GDPR Obfuscator

The **GDPR Obfuscator** is a Python library designed to help you obfuscate personally identifiable information (PII) in files stored in AWS S3. It supports CSV, JSON, and Parquet file formats and ensures compliance with GDPR requirements by replacing sensitive data with `***`.

## Example
Given a CSV file with the following content:
```csv
name,email,phone
John Doe,john@example.com,123-456-7890
```
The GDPR Obfuscator can replace the `name` and `email` fields with `***`:
```csv
name,email,phone
***,***,123-456-7890
```

### Features

- **Obfuscation of PII**: Replace specified fields in your data with `***`.
- **Multiple File Formats**: Supports CSV, JSON, and Parquet files.
- **AWS S3 Integration**: Seamlessly reads and writes files from/to S3 buckets.
- **CLI Support**: Includes a command-line interface for easy integration into workflows.
- **Modular Design**: Easily extendable to support additional file formats or obfuscation methods.

## Table of Contents

- [Setup](#setup)
- [Usage](#usage)
  - [As a Python Library](#as-a-python-library)
  - [As a Command-Line Tool](#as-a-command-line-tool)
- [Configuration](#configuration)
  - [Input JSON Format](#input-json-format)
  - [AWS Credentials](#aws-credentials)
  - [IAM Permissions](#iam-permissions)
- [Testing](#testing)
  - [Example Test Cases](#example-test-cases)
- [Deployment](#deployment)
  - [AWS Lambda](#aws-lambda)
- [Performance](#performance)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Setup

### System Requirements

- **Python 3.7 or higher** (Recommended: Python 3.9+)

### Installation

You have two main options for installing the GDPR Obfuscator:

1.  **Remote Installation (GitHub Direct Install):**
    ```bash
    pip install git+https://github.com/T-Aji/NC-GDPR-obfuscator-project.git
    ```
    This method is best for quickly installing the latest stable version directly from GitHub.
2.  **Local Installation (Development & Lambda Packaging):**
    ```bash
    git clone https://github.com/T-Aji/NC-GDPR-obfuscator-project.git
    cd NC-GDPR-obfuscator-project
    pip install .
    ```
    This method is best for development, customization, and AWS Lambda deployment since it allows manual packaging.

## Usage

### As a Python Library

```python
import json
from obfuscator.process_file import process_s3_file
import boto3

# JSON input specifying the S3 file and PII fields
json_input = {
    "file_to_obfuscate": "s3://my-bucket/path/to/file.csv",
    "pii_fields": ["name", "email"]
}

# Process the file and get the obfuscated byte stream
output_bytes = process_s3_file(json.dumps(json_input))

# Save the obfuscated file to a new S3 location
s3_client = boto3.client("s3")
s3_client.put_object(Bucket="my-bucket", Key="path/to/obfuscated_file.csv", Body=output_bytes)

# Or save the obfuscated file locally
with open("path/to/obfuscated_file.csv", "wb") as f:
    f.write(output_bytes)
```

### As a Command-Line Tool

The GDPR Obfuscator also includes a CLI for easy integration into scripts or workflows:

```bash
obfuscator '{"file_to_obfuscate": "s3://my-bucket/path/to/file.csv", "pii_fields": ["name", "email"], "output_s3": "s3://my-bucket/obfuscated_file.csv"}'
```

The obfuscated file will be saved in the specified S3 location or locally as `output.csv` (or the appropriate format based on the input file) in the current working directory.

## Configuration

### Input JSON Format

```json
{
    "file_to_obfuscate": "s3://my-bucket/path/to/file.csv",
    "pii_fields": ["field1", "field2"],
    "output_s3": "s3://my-bucket/obfuscated_file.csv"
}
```

- **`file_to_obfuscate`**: The S3 URI of the file to process.
- **`pii_fields`**: A list of fields to obfuscate.
- **`output_s3`**: (Optional) The S3 URI to save the obfuscated file.

### AWS Credentials

The tool uses the `boto3` library to interact with AWS S3. Ensure your AWS credentials are configured using one of the following methods:

- AWS CLI: Run `aws configure` and provide your credentials.
- Environment variables: Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
- IAM roles: If running on AWS infrastructure (e.g., EC2, Lambda), attach an IAM role with the necessary permissions.

### IAM Permissions

To process files in S3, ensure your IAM role or user has the following permissions:

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": ["arn:aws:s3:::your-bucket-name/*"]
}
```

## Testing

1.  Install the development dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Install the package in editable mode (if not already installed):
    ```bash
    pip install -e .
    ```
3.  Run the tests using `pytest`:
    ```bash
    pytest tests/
    ```
- Unit tests are provided, and the code has been tested for security vulnerabilities using `bandit` & `safety`.The tests use moto to mock AWS services.
- To check code coverage: coverage run pytest --cov=obfuscator --cov-report=html tests/

### Example Test Cases

- **Input Validation**: Ensures invalid inputs are handled gracefully.
- **Obfuscation Logic**: Verifies that PII fields are correctly replaced with `***`.
- **File Formats**: Tests CSV, JSON, and Parquet file handling.

### Security Testing

- To run bandit security scans: bandit -r src/ -x tests/
- To run safety dependency checks: safety scan -r requirements.txt

![Tests](about:sanitized)

## Deployment

### AWS Lambda

This tool can be deployed as an AWS Lambda function or Layer.

#### **Deploying as a Lambda Function**
1. Install dependencies locally and package them:
   ```bash
   pip install -r requirements.txt -t package/
   cd package && zip -r ../obfuscator_lambda.zip .
   ```
2. Upload the `obfuscator_lambda.zip` to AWS Lambda.
3. Ensure the function has the correct IAM role for S3 access.
4. Configure any necessary environment variables for your Lambda function.


## Performance

The tool is able to handle files up to **1MB** with a runtime of **less than 1 minute**. Performance tests were conducted locally to validate this requirement.

## Contributing

Contributions to the GDPR Obfuscator are welcome! Here’s how you can help:

1.  **Report Issues**: If you find a bug or have a feature request, please open an issue on GitHub.
2.  **Submit Pull Requests**: Fork the repository, make your changes, and submit a pull request.
3.  **Improve Documentation**: Help us improve the README, docstrings, or other documentation.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feedback, please open an issue on the [GitHub repository](https://github.com/T-Aji/NC-GDPR-obfuscator-project).

