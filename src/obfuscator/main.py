import sys
import json
import os
from obfuscator.process_file import process_s3_file


def obfuscator(output_dir=None):
    """Entry point for the CLI."""
    if len(sys.argv) != 2:
        print(
            'Usage: obfuscator \'{"file_to_obfuscate": "s3://my-bucket/file.csv", '
            '"pii_fields": ["name", "email"]}\''
        )
        sys.exit(1)

    json_input = sys.argv[1]  # Get the JSON input from the command line.

    try:
        # Process the file
        output_bytes = process_s3_file(json_input)

        # Determine the output file name based on the input file extension
        input_data = json.loads(json_input)
        s3_uri = input_data.get("file_to_obfuscate")
        file_extension = s3_uri.split(".")[-1]

        # Save the output to a file
        output_filename = f"output.{file_extension}"
        if output_dir:
            output_path = os.path.join(output_dir, output_filename)
        else:
            output_path = output_filename
        with open(output_path, "wb") as f:
            f.write(output_bytes.getvalue())
        print(f"File processed and saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    obfuscator()
