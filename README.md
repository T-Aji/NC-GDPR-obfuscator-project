# NC-GDPR-Obfuscator-Project

A general-purpose tool to process data being ingested into AWS and intercept personally identifiable information (PII). This tool ensures compliance with GDPR and other data protection regulations by obfuscating sensitive fields in datasets before they are stored or processed further.

---

## **Features**
- **PII Obfuscation**: Automatically detects and obfuscates specified PII fields (e.g., email, phone numbers) in datasets.
- **Multi-Format Support**: Works with CSV, JSON, and Parquet file formats.
- **AWS S3 Integration**: Seamlessly reads and writes files from/to AWS S3.
- **Command-Line Interface (CLI)**: Easy-to-use CLI for processing files locally or in automated workflows.
- **Customizable Obfuscation**: Define which fields to obfuscate via a JSON configuration.

---

## **Installation**

### Prerequisites
- Python 3.8 or higher
- AWS CLI configured with valid credentials
- Required Python packages: `boto3`, `pandas`, `pyarrow`

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/T-Aji/NC-GDPR-obfuscator-project.git
   cd NC-GDPR-obfuscator-project
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure your AWS credentials are configured:
   ```bash
   aws configure
   ```

---

## **Usage**

### **Command-Line Interface (CLI)**

The tool provides a CLI for processing files. Below are the available commands and options:

#### **Process a File from S3**
```bash
python s3_pii_obfuscator.py --input <input_json_or_file> --output <output_file_path>
```

- `--input`: JSON input as a string or path to a JSON file. The JSON should contain:
  - `file_to_obfuscate`: The S3 URI of the file to process (e.g., `s3://my-bucket/path/to/file.csv`).
  - `pii_fields`: A list of fields to obfuscate (e.g., `["email", "phone"]`).

- `--output`: The path where the processed file will be saved.

#### **Example 1: JSON Input as a String**
```bash
python s3_pii_obfuscator.py \
    --input '{"file_to_obfuscate": "s3://my-bucket/path/to/file.csv", "pii_fields": ["email", "phone"]}' \
    --output output.csv
```

#### **Example 2: JSON Input from a File**
1. Create a JSON file, e.g., `input.json`:
   ```json
   {
       "file_to_obfuscate": "s3://my-bucket/path/to/file.csv",
       "pii_fields": ["email", "phone"]
   }
   ```

2. Run the script:
   ```bash
   python s3_pii_obfuscator.py --input input.json --output output.csv
   ```

---

### **Programmatic Usage**

You can also use the tool programmatically in your Python scripts. Below is an example:

```python
from s3_pii_obfuscator import process_s3_file

# Define the JSON input
json_input = {
    "file_to_obfuscate": "s3://my-bucket/path/to/file.csv",
    "pii_fields": ["email", "phone"]
}

# Process the file
byte_stream = process_s3_file(json.dumps(json_input))

# Save the output to a file
with open("output.csv", "wb") as f:
    f.write(byte_stream.getvalue())
```

---

## **Configuration**

### **Input JSON Format**
The input JSON should have the following structure:
```json
{
    "file_to_obfuscate": "s3://my-bucket/path/to/file.csv",
    "pii_fields": ["email", "phone"]
}
```

- `file_to_obfuscate`: The S3 URI of the file to process.
- `pii_fields`: A list of fields to obfuscate.

---

## **Supported File Formats**
- **CSV**: Comma-separated values.
- **JSON**: Line-delimited JSON (JSONL).
- **Parquet**: Columnar storage format.

---

## **Contributing**

We welcome contributions! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to your fork.
4. Submit a pull request with a detailed description of your changes.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**
- Thanks to the open-source community for providing the tools and libraries that made this project possible.
- Special thanks to the AWS team for their excellent documentation and SDKs.

---

## **Contact**

For questions, feedback, or support, please contact:
- **Your Name**: [your.email@example.com](mailto:your.email@example.com)
- **Project Repository**: [https://github.com/your-username/NC-GDPR-obfuscator-project](https://github.com/your-username/NC-GDPR-obfuscator-project)

---

## **Changelog**

### **v1.0.0 (Initial Release)**
- Initial release of the NC-GDPR Obfuscator.
- Supports CSV, JSON, and Parquet file formats.
- Integrates with AWS S3 for seamless file processing.
- Provides a CLI for easy usage.

---

Thank you for using the NC-GDPR Obfuscator! We hope it helps you achieve GDPR compliance and secure your data effectively. 🚀