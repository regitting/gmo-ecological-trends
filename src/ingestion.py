import pandas as pd
import re

def read_delimited_text(path: str) -> pd.DataFrame:
    """
    Read USGS-style .txt files (tab- or pipe-delimited).
    """
    try:
        df = pd.read_csv(path, sep="\t")
        if df.shape[1] > 1:
            return df
    except Exception:
        pass

    return pd.read_csv(path, sep=None, engine="python")


def ingest_ers_adoption(csv_path: str) -> pd.DataFrame:
    """
    Ingest USDA ERS GMO adoption data.
    Expected columns: Attribute, State, Year, Value
    """
    df = pd.read_csv(csv_path, encoding="cp1252")
    df.columns = [c.strip().lower() for c in df.columns]

    df = df.rename(columns={"value": "adoption_percent"})

    # Extract trait
    df["trait"] = df["attribute"].str.extract(r"^(.*?)\s*\(")[0]
    df["trait"] = df["trait"].str.replace(" only", "", regex=False).str.strip()

    # Extract crop
    df["crop"] = df["attribute"].str.extract(
        r"percent of all (.*?) planted", flags=re.IGNORECASE
    )[0].str.lower().str.strip()

    return df[["year", "state", "crop", "trait", "adoption_percent"]]


def ingest_usgs_pesticide(txt_path: str) -> pd.DataFrame:
    """
    Ingest USGS state-level pesticide use data (wide format).
    """
    df = read_delimited_text(txt_path)

    id_cols = ["State", "Year", "Units", "Compound"]
    crop_cols = [c for c in df.columns if c not in id_cols]

    long_df = df.melt(
        id_vars=id_cols,
        value_vars=crop_cols,
        var_name="crop",
        value_name="pesticide_use"
    )

    long_df["crop"] = long_df["crop"].str.lower().str.strip()

    return long_df[["Year", "State", "crop", "Compound", "Units", "pesticide_use"]]