import sys
from obfuscator.process_file import process_s3_file


def obfuscator(json_input):
    """
    Entry point for the CLI.
    Returns a BytesIO object containing the processed file.
    """
    try:
        # Process the file
        output_bytes = process_s3_file(json_input)

        # Return the bytestream
        return output_bytes

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            'Usage: obfuscator \'{"file_to_obfuscate": "s3://my-bucket/file.csv", '
            '"pii_fields": ["name", "email"]}\''
        )
        sys.exit(1)

    json_input = sys.argv[1]  # Get the JSON input from the command line.

    # Run the obfuscator and get the bytestream
    bytestream = obfuscator(json_input)

    # Print the bytestream content (for demonstration)
    print("Processed file content:")
    print(bytestream.getvalue().decode("utf-8"))
