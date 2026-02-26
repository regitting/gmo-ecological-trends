from __future__ import annotations

from curses.panel import panel
from pathlib import Path
import pandas as pd
from . import ingestion

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
ANALYSIS = DATA / "analysis"


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def build_panel() -> pd.DataFrame:
    required = [
        "acreage_yield.csv",
        "gmo_adoption.csv",
        "erosion.csv",
        "pesticides_le.csv",
    ]

    missing = [f for f in required if not (PROCESSED / f).exists()]

    if missing:
        ingestion.run_all()

    ay = load("acreage_yield.csv")
    adopt = load("gmo_adoption.csv")
    erosion = load("erosion.csv")
    pest = load("pesticides_le.csv")

    panel = ay.merge(adopt, on=["year", "crop"], how="left")
    panel = panel.merge(erosion, on=["year", "state"], how="left")

    pest_total = (
        pest.groupby(["year", "state", "crop"], as_index=False)["pesticide_kg"]
        .sum()
        .rename(columns={"pesticide_kg": "pesticide_kg_total"})
    )

    panel = panel.merge(pest_total, on=["year", "state", "crop"], how="left")
    panel["pesticide_kg_per_ha"] = panel["pesticide_kg_total"] / panel["hectares"]

    if "ht_pct" in panel.columns:
        panel["ht_hectares_est"] = panel["hectares"] * (panel["ht_pct"] / 100.0)
    if "ir_pct" in panel.columns:
        panel["ir_hectares_est"] = panel["hectares"] * (panel["ir_pct"] / 100.0)

    panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2019)]

    panel_collapsed = (
        panel
        .groupby(["year", "state", "crop"], as_index=False)
        .mean(numeric_only=True)
    )

    panel.to_csv(PROCESSED / "panel.csv", index=False)
    panel_collapsed.to_csv(ANALYSIS / "panel_collapsed.csv", index=False)
    
    return panel


if __name__ == "__main__":
    df = build_panel()
    print(f"panel.csv written: {len(df)} rows")