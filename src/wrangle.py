import pandas as pd
from ingestion import ingest_ers_adoption, ingest_usgs_pesticide
from normalization import normalize_state, normalize_crop

def build_merged_dataset(ers_path, usgs_path):
    ers = ingest_ers_adoption(ers_path)
    usgs = ingest_usgs_pesticide(usgs_path)

    # normalize
    ers["state"] = ers["state"].apply(normalize_state)
    ers["crop"] = ers["crop"].apply(normalize_crop)

    usgs["State"] = usgs["State"].apply(normalize_state)
    usgs["crop"] = usgs["crop"].apply(normalize_crop)

    # aggregate pesticide use across compounds
    pest_total = (
        usgs
        .groupby(["Year", "State", "crop"], as_index=False)["pesticide_use"]
        .sum()
        .rename(columns={
            "Year": "year",
            "State": "state",
            "pesticide_use": "pesticide_total"
        })
    )

    merged = ers.merge(
        pest_total,
        on=["year", "state", "crop"],
        how="inner"
    )

    return merged


if __name__ == "__main__":
    merged = build_merged_dataset(
        "data/raw/biotech-crops-all-tables-2024.csv",
        "data/raw/usgs_pesticide_use.txt"
    )

    merged.to_csv("data/processed/merged_ers_usgs.csv", index=False)
    print("Saved merged dataset:", merged.shape)