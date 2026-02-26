from __future__ import annotations
import re
import pandas as pd

ACRES_TO_HECTARES = 0.40468564224

def clean_state(s: str) -> str:
    """
    Normalize state names to a consistent title case.
    e.g., 'NORTH DAKOTA' -> 'North Dakota'
    """
    if s is None:
        return s
    s = str(s).strip()
    s = re.sub(r"\s+", " ", s)
    return s.title()

def parse_numeric_value(x) -> float | None:
    """
    NASS/USGS files sometimes use commas or (D), (Z) etc.
    Returns float or None.
    """
    if x is None:
        return None
    s = str(x).strip()
    if s in {"(D)", "(Z)", "D", "Z", ""}:
        return None
    # remove commas
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None

def pick_col(df: pd.DataFrame, candidates: list[str]) -> str:
    """
    Find first column existing in df among candidates.
    """
    cols = set(df.columns)
    for c in candidates:
        if c in cols:
            return c
    raise KeyError(f"None of these columns exist: {candidates}. Found: {list(df.columns)}")

def standardize_nass(df: pd.DataFrame, crop: str, metric: str) -> pd.DataFrame:
    """
    Standardize a NASS QuickStats export to:
      year, state, crop, value
    metric: 'area' or 'yield'
    """
    year_col = pick_col(df, ["Year", "year", "YEAR"])
    state_col = pick_col(df, ["State", "state", "STATE", "State Name", "state_name"])
    value_col = pick_col(df, ["Value", "value", "VALUE"])

    out = df[[year_col, state_col, value_col]].copy()
    out.columns = ["year", "state", "value_raw"]
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["state"] = out["state"].map(clean_state)
    out["value"] = out["value_raw"].map(parse_numeric_value)
    out = out.drop(columns=["value_raw"])
    out["crop"] = crop

    # Keep only valid years/states/values
    out = out.dropna(subset=["year", "state", "value"])

    if metric == "area":
        # NASS area exports are in acres for these queries
        out.rename(columns={"value": "acres_harvested"}, inplace=True)
        out["hectares"] = out["acres_harvested"] * ACRES_TO_HECTARES
        out = out[["year", "state", "crop", "acres_harvested", "hectares"]]
    elif metric == "yield":
        # Yield usually BU / ACRE for corn/soy
        out.rename(columns={"value": "yield_bu_per_acre"}, inplace=True)
        # Convert to BU/HA for a consistent per-hectare rate
        out["yield_bu_per_ha"] = out["yield_bu_per_acre"] / ACRES_TO_HECTARES
        out = out[["year", "state", "crop", "yield_bu_per_acre", "yield_bu_per_ha"]]
    else:
        raise ValueError("metric must be 'area' or 'yield'")

    return out