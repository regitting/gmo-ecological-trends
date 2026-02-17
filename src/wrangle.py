# src/wrangle.py
import json
from pathlib import Path

import pandas as pd

# If you get import errors, switch these to: from src.ingestion import ...
from ingestion import ingest_ers_adoption, ingest_usgs_pesticide
from normalization import normalize_state, normalize_crop


def load_config(path: str = "config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_merged_dataset(ers_paths: list[str], usgs_paths: list[str]) -> pd.DataFrame:
    # ---- ERS: read + normalize + concat ----
    ers_frames = []
    for p in ers_paths:
        df = ingest_ers_adoption(p)
        df["state"] = df["state"].apply(normalize_state)
        df["crop"] = df["crop"].apply(normalize_crop)
        ers_frames.append(df)

    ers = pd.concat(ers_frames, ignore_index=True)
    ers = ers.dropna(subset=["year", "state", "crop", "adoption_percent"])

    # ---- USGS: read (wide->long happens in ingest) + normalize + concat ----
    usgs_frames = []
    for p in usgs_paths:
        df = ingest_usgs_pesticide(p)
        # ingest_usgs_pesticide returns columns: Year, State, crop, Compound, Units, pesticide_use
        df["State"] = df["State"].apply(normalize_state)
        df["crop"] = df["crop"].apply(normalize_crop)
        usgs_frames.append(df)

    usgs = pd.concat(usgs_frames, ignore_index=True)
    usgs = usgs.dropna(subset=["Year", "State", "crop", "pesticide_use"])

    # ---- Aggregate pesticide use across compounds ----
    pest_total = (
        usgs.groupby(["Year", "State", "crop"], as_index=False)["pesticide_use"]
        .sum()
        .rename(
            columns={
                "Year": "year",
                "State": "state",
                "pesticide_use": "pesticide_total",
            }
        )
    )

    # ---- Merge on (year, state, crop) ----
    merged = ers.merge(pest_total, on=["year", "state", "crop"], how="inner")

    return merged


def main() -> None:
    cfg = load_config("config.json")

    ers_files = cfg.get("ers_files", [])
    usgs_files = cfg.get("usgs_files", [])
    output_file = cfg.get("output_file", "data/processed/merged_ers_usgs.csv")

    if not ers_files:
        raise ValueError("config.json: 'ers_files' is empty")
    if not usgs_files:
        raise ValueError("config.json: 'usgs_files' is empty")

    # Optional: fail fast if a path is wrong
    for p in ers_files + usgs_files:
        if not Path(p).exists():
            raise FileNotFoundError(f"File not found: {p}")

    merged = build_merged_dataset(ers_files, usgs_files)

    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out, index=False)

    print(f"Saved merged dataset: {merged.shape} -> {out}")


if __name__ == "__main__":
    main()
