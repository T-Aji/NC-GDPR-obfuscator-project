import pytest
import pandas as pd
from obfuscator.obfuscate_pii import obfuscate_pii


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


def test_obfuscate_pii(sample_dataframe):
    """Test obfuscation of PII fields."""
    pii_fields = ["name", "email_address"]
    obfuscated_df = obfuscate_pii(sample_dataframe, pii_fields)

    # Assertions
    # Ensure PII fields are obfuscated
    assert all(obfuscated_df["name"] == "***")
    assert all(obfuscated_df["email_address"] == "***")
    # Non-PII fields should remain unchanged
    assert all(obfuscated_df["student_id"] == sample_dataframe["student_id"])


def test_obfuscate_pii_with_missing_columns(sample_dataframe):
    """Test obfuscation when specified PII fields are missing."""
    obfuscated_df = obfuscate_pii(sample_dataframe, ["non_existent_column"])

    # Assertions
    # DataFrame should remain unchanged
    assert obfuscated_df.equals(sample_dataframe)
