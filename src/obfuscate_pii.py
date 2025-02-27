import pandas as pd

def obfuscate_pii(dataframe: pd.DataFrame, pii_fields: list) -> pd.DataFrame:
    """Replaces PII fields in the DataFrame with obfuscated ('***') values.
    
    Args:
        dataframe (pd.DataFrame): The DataFrame containing the data.
        pii_fields (list): List of fields to obfuscate.
    
    Returns:
        pd.DataFrame: The DataFrame with obfuscated PII fields.
    """
    obfuscated_df = dataframe.copy()
    for field in pii_fields:
        if field in obfuscated_df.columns:
            obfuscated_df[field] = "***"
    return obfuscated_df