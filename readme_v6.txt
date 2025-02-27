Here’s a comprehensive `README.md` file for the **GDPR Obfuscator Project**, following best practices and incorporating the recommendations from the project brief and test suite.

---

# GDPR Obfuscator Tool

## Overview
The **GDPR Obfuscator Tool** is a Python library designed to anonymize Personally Identifiable Information (PII) in CSV files stored in AWS S3. It ensures compliance with GDPR regulations by replacing sensitive fields with obfuscated values (e.g., `"***"`). The tool is designed to be integrated into Python workflows and deployed within the AWS ecosystem.

---

## Features
- **Read CSV files from S3**: Fetch CSV files from an AWS S3 bucket.
- **Obfuscate PII fields**: Replace specified PII fields with `"***"`.
- **Generate byte-stream output**: Return the obfuscated data as a byte stream compatible with `boto3.S3.PutObject`.
- **Handle edge cases**: Gracefully handle empty files, invalid formats, and missing fields.
- **UTF-8 support**: Process files with special characters and non-ASCII text.
- **Performance optimized**: Handle files up to 1MB with a runtime of less than 1 minute.

---

## Installation
To install the GDPR Obfuscator Tool, clone the repository and install the required dependencies:

```bash
git clone https://github.com/your-username/gdpr-obfuscator.git
cd gdpr-obfuscator
pip install -r requirements.txt
```

### Dependencies
- Python 3.8+
- `boto3` (AWS SDK for Python)
- `pandas` (Data manipulation)
- `pytest` (Testing framework)
- `moto` (Mock AWS services for testing)

---

## Usage

### Input JSON Format
The tool is invoked with a JSON string containing:
- `file_to_obfuscate`: The S3 URI of the CSV file to process.
- `pii_fields`: A list of fields to obfuscate.

Example JSON input:
```json
{
  "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
  "pii_fields": ["name", "email_address"]
}
```

### Example Code
```python
from gdpr_obfuscator import process_s3_file

# JSON input
json_input = '''
{
  "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
  "pii_fields": ["name", "email_address"]
}
'''

# Process the file
output_bytes = process_s3_file(json_input)

# Save the output to a file (for demonstration purposes)
with open("output.csv", "wb") as f:
    f.write(output_bytes.getvalue())
```

---

## Deployment
The tool is designed to be deployed within the AWS ecosystem. It can be integrated into workflows using services like:
- **AWS Lambda**: Deploy the tool as a serverless function.
- **AWS Step Functions**: Orchestrate the tool as part of a larger workflow.
- **Apache Airflow**: Use the tool in a data pipeline.

### AWS Lambda Deployment
1. Package the tool and its dependencies:
   ```bash
   pip install -r requirements.txt --target ./package
   cd package
   zip -r ../gdpr-obfuscator.zip .
   cd ..
   zip -g gdpr-obfuscator.zip gdpr_obfuscator/*.py
   ```

2. Upload the ZIP file to AWS Lambda and configure the handler as `gdpr_obfuscator.process_s3_file`.

3. Set up environment variables for AWS credentials (if not using IAM roles):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

---

## Testing
The tool includes a comprehensive test suite to ensure reliability and correctness. To run the tests:

```bash
pytest tests/ -v
```

### Test Coverage
- **Reading CSV files from S3**: Valid, empty, and invalid files.
- **Obfuscation logic**: Mixed data types, numeric PII, missing columns.
- **Byte-stream output**: CSV format, empty DataFrames.
- **Edge cases**: UTF-8 encoded data, large files, missing S3 files.

---

## Error Handling
The tool handles the following errors gracefully:
- **Invalid JSON input**: Raises a `ValueError` with a descriptive message.
- **Missing S3 file**: Raises a `RuntimeError` if the specified file does not exist.
- **Empty CSV files**: Returns an empty DataFrame.
- **Unsupported file formats**: Raises a `ValueError` for non-CSV files (future support for JSON and Parquet).

---

## Performance
The tool is optimized to handle files up to 1MB with a runtime of less than 1 minute. Performance tests are included in the test suite to validate this requirement.

---

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write tests for your changes.
4. Submit a pull request.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments
- **AWS SDK for Python (boto3)**: For interacting with AWS S3.
- **Pandas**: For efficient data manipulation.
- **Moto**: For mocking AWS services in tests.

---

## Contact
For questions or feedback, please contact:
- **Your Name**: your.email@example.com
- **Project Repository**: [GitHub](https://github.com/your-username/gdpr-obfuscator)

---

This `README.md` provides a clear and concise guide to the project, ensuring that users and contributors can easily understand, use, and extend the tool.