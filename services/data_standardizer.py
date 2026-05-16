import pandas as pd


def standardize_columns(df):
    """
    Standardize dataframe columns and clean text fields.
    """

    # defensive copy
    df = df.copy()

    # normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )

    # clean object/string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA})
        )

    return df