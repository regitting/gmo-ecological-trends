from __future__ import annotations

from pathlib import Path
import pandas as pd

from .normalization import (
    standardize_nass,
    parse_numeric_value,
    clean_state,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> pd.DataFrame:
    """
    Reads CSV-like files that may be UTF-8 or UTF-16 (common for Tableau/Excel exports).
    """
    try:
        return pd.read_csv(path, dtype=str)
    except UnicodeDecodeError:
        return pd.read_csv(path, dtype=str, encoding="utf-16")


def ingest_ers_biotech() -> pd.DataFrame:
    """
    Ingests USDA ERS biotech adoption tables in the format:
      Attribute, State, Year, Value, Table

    Outputs:
      year, crop, ht_pct, ir_pct

    The output is intended to be national adoption by crop-year.
    """
    candidates = (
        list(RAW.glob("biotech-crops-all-tables-2024.csv"))
        + list(RAW.glob("biotech-crops-all-tables-*.csv"))
    )
    if not candidates:
        raise FileNotFoundError("No biotech-crops-all-tables-*.csv found in data/raw/")

    df = read_csv(candidates[0])

    required = {"Attribute", "State", "Year", "Value", "Table"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"ERS biotech file missing columns: {sorted(missing)}")

    tmp = df[["Attribute", "State", "Year", "Value", "Table"]].copy()
    tmp.columns = ["attribute", "state", "year", "value_raw", "table"]

    tmp["year"] = pd.to_numeric(tmp["year"], errors="coerce").astype("Int64")
    tmp["pct"] = tmp["value_raw"].map(parse_numeric_value)
    tmp["attribute"] = tmp["attribute"].astype(str).str.strip()
    tmp["state"] = tmp["state"].astype(str).str.strip()
    tmp["table"] = tmp["table"].astype(str).str.strip()

    tmp = tmp.drop(columns=["value_raw"]).dropna(subset=["year", "pct", "attribute", "state", "table"])
    tmp = tmp[(tmp["year"] >= 2000) & (tmp["year"] <= 2019)]

    state_l = tmp["state"].str.lower()
    tmp = tmp[
        state_l.isin({"u.s.", "us", "u.s", "united states", "all", "total"})
        | state_l.str.contains("united states", na=False)
        | state_l.str.contains(r"\bu\.?s\.?\b", na=False)
    ].copy()

    def norm_crop(table: str, attr: str) -> str | None:
        t = str(table).lower()
        a = str(attr).lower()
        if "corn" in t or "corn" in a:
            return "corn"
        if "soy" in t or "soybean" in t or "soy" in a or "soybean" in a:
            return "soybeans"
        return None

    tmp["crop"] = [norm_crop(t, a) for t, a in zip(tmp["table"], tmp["attribute"])]
    tmp = tmp.dropna(subset=["crop"])

    def trait_bucket(attr: str) -> str | None:
        a = str(attr).lower()
        if "herbicide" in a:
            return "ht"
        if "insect" in a or "bt" in a:
            return "ir"
        return None

    tmp["bucket"] = tmp["attribute"].map(trait_bucket)
    tmp = tmp.dropna(subset=["bucket"])

    wide = (
        tmp.pivot_table(index=["year", "crop"], columns="bucket", values="pct", aggfunc="mean")
        .reset_index()
        .rename(columns={"ht": "ht_pct", "ir": "ir_pct"})
    )

    wide.to_csv(PROCESSED / "gmo_adoption.csv", index=False)
    return wide


def ingest_usgs_pesticides_le() -> pd.DataFrame:
    """
    Ingests USGS pesticide-use estimates in the 'le' wide format:
      State_FIPS_code, State, Compound, Year, Units, Corn, Soybeans, ...

    Outputs a long table:
      year, state, crop, compound, pesticide_kg
    """
    path = RAW / "le_usgs_presticide_use.txt"
    if not path.exists():
        raise FileNotFoundError("data/raw/le_usgs_presticide_use.txt not found")

    df = pd.read_csv(path, sep="\t", dtype=str)

    required = {"State", "Compound", "Year", "Units"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in le file: {sorted(missing)}")

    crop_cols = [c for c in df.columns if c not in {"State_FIPS_code", "State", "Compound", "Year", "Units"}]
    if not crop_cols:
        raise ValueError("No crop columns detected in le pesticide file")

    out = df.melt(
        id_vars=["State", "Compound", "Year", "Units"],
        value_vars=crop_cols,
        var_name="crop_raw",
        value_name="value_raw",
    )

    out["year"] = pd.to_numeric(out["Year"], errors="coerce").astype("Int64")
    out["state"] = out["State"].map(clean_state)
    out["compound"] = out["Compound"].astype(str).str.strip()
    out["units"] = out["Units"].astype(str).str.strip()
    out["pesticide_kg"] = out["value_raw"].map(parse_numeric_value)

    out = out.drop(columns=["State", "Compound", "Year", "Units", "value_raw"])
    out = out.dropna(subset=["year", "state", "compound", "pesticide_kg"])
    out = out[(out["year"] >= 2000) & (out["year"] <= 2019)]

    def norm_crop(c: str) -> str | None:
        c = str(c).strip().lower()
        if c == "corn":
            return "corn"
        if c == "soybeans":
            return "soybeans"
        return None

    out["crop"] = out["crop_raw"].map(norm_crop)
    out = out.drop(columns=["crop_raw"]).dropna(subset=["crop"])

    out.to_csv(PROCESSED / "pesticides_le.csv", index=False)
    return out

def ingest_nass() -> pd.DataFrame:
    """
    Ingests NASS acreage and yield CSVs and writes:
      data/processed/acreage_yield.csv
    """
    corn_area = standardize_nass(
        read_csv(RAW / "corn_area_state_2000_2019.csv"),
        crop="corn",
        metric="area",
    )
    corn_yield = standardize_nass(
        read_csv(RAW / "corn_yield_state_2000_2019.csv"),
        crop="corn",
        metric="yield",
    )

    soy_area = standardize_nass(
        read_csv(RAW / "soy_area_state_2000_2019.csv"),
        crop="soybeans",
        metric="area",
    )
    soy_yield = standardize_nass(
        read_csv(RAW / "soy_yield_state_2000_2019.csv"),
        crop="soybeans",
        metric="yield",
    )

    corn = corn_area.merge(
        corn_yield, on=["year", "state", "crop"], how="inner"
    )
    soy = soy_area.merge(
        soy_yield, on=["year", "state", "crop"], how="inner"
    )

    out = pd.concat([corn, soy], ignore_index=True)
    out = out[(out["year"] >= 2000) & (out["year"] <= 2019)]

    out.to_csv(PROCESSED / "acreage_yield.csv", index=False)
    return out

def ingest_erosion() -> pd.DataFrame:
    path = RAW / "soil_erosion.csv"
    if not path.exists():
        raise FileNotFoundError("data/raw/soil_erosion.csv not found")

    df = None
    encodings = ("utf-16", "utf-16le", "utf-8-sig", "latin1")

    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, errors="strict") as f:
                first = f.readline()
            sep = "\t" if first.count("\t") >= 3 else ","
            df = pd.read_csv(path, dtype=str, encoding=enc, sep=sep)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        with open(path, "r", errors="ignore") as f:
            first = f.readline()
        sep = "\t" if first.count("\t") >= 3 else ","
        df = pd.read_csv(path, dtype=str, sep=sep)

    if df.shape[1] == 1:
        df = pd.read_csv(path, dtype=str, sep=None, engine="python")

    required = ["Area", "Erosion Type", "Estimate Type", "Rate Category", "Year", "Estimate"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"soil_erosion.csv missing columns: {missing}")

    tmp = df[required].copy()
    tmp.columns = ["state", "erosion_type", "estimate_type", "rate_category", "year", "estimate_raw"]

    tmp["state"] = tmp["state"].astype(str).str.strip()

    tmp["erosion_type"] = tmp["erosion_type"].astype(str).str.strip().str.lower()
    tmp["estimate_type"] = tmp["estimate_type"].astype(str).str.strip().str.lower()
    tmp["rate_category"] = tmp["rate_category"].astype(str).str.strip().str.lower()

    tmp["year"] = (
        tmp["year"].astype(str).str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )
    tmp["year"] = pd.to_numeric(tmp["year"], errors="coerce")

    tmp["erosion_sheet_rill_ton_acre_yr"] = pd.to_numeric(
        tmp["estimate_raw"].astype(str).str.strip(),
        errors="coerce"
    )

    US_STATES = {
        "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia",
        "Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
        "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire",
        "New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
        "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington",
        "West Virginia","Wisconsin","Wyoming"
    }

    m_state = tmp["state"].isin(US_STATES)
    m_year = tmp["year"].between(2000, 2019)
    m_type = tmp["erosion_type"].str.contains("sheet", na=False) & tmp["erosion_type"].str.contains("rill", na=False)
    m_est = tmp["estimate_type"].str.contains("erosion", na=False) & tmp["estimate_type"].str.contains("rate", na=False)
    m_rate = tmp["rate_category"].str.contains("total", na=False)

    tmp = tmp[m_state & m_year & m_type & m_est & m_rate].copy()
    tmp = tmp.dropna(subset=["year", "state", "erosion_sheet_rill_ton_acre_yr"])
    tmp["year"] = tmp["year"].astype(int)

    out = tmp[["year", "state", "erosion_sheet_rill_ton_acre_yr"]].sort_values(["year", "state"])
    out.to_csv(PROCESSED / "erosion.csv", index=False)
    return out

def run_all() -> None:
    ingest_ers_biotech()
    ingest_usgs_pesticides_le()
    ingest_nass()
    ingest_erosion()
    print("processed files written to data/processed/")


if __name__ == "__main__":
    run_all()