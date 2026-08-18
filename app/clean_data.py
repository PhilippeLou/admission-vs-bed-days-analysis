"""
Data cleaning for the Hospital Inpatient Discharges (SPARCS 2021) dataset.
Handles the '120 +' top-coded Length of Stay values and standardizes column names.
"""

import pandas as pd


def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    # --- Length of Stay: convert '120 +' top-coded value to numeric floor ---
    df["LOS_topcoded"] = df["Length of Stay"].astype(str).str.strip() == "120 +"
    df["Length of Stay"] = (
        df["Length of Stay"].astype(str).str.replace("120 +", "120", regex=False)
    )
    df["Length of Stay"] = pd.to_numeric(df["Length of Stay"], errors="coerce")

    # --- Facility / county redaction: keep an explicit flag instead of dropping rows ---
    df["Facility Redacted"] = df["Facility Name"] == "Redacted for Confidentiality"

    # --- Clean numeric columns stored as text with commas (Total Charges / Total Costs) ---
    # Note: pandas 3.0's Arrow-backed string dtype isn't caught by `dtype == object`,
    # so we always strip commas and coerce to numeric regardless of current dtype.
    for col in ["Total Charges", "Total Costs"]:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Standardize age group ordering (categorical for correct chart sorting) ---
    age_order = ["0 to 17", "18 to 29", "30 to 49", "50 to 69", "70 or Older"]
    df["Age Group"] = pd.Categorical(df["Age Group"], categories=age_order, ordered=True)

    return df


if __name__ == "__main__":
    df = load_and_clean("../data/discharges_raw.csv")
    print("Shape:", df.shape)
    print("Top-coded LOS rows:", df["LOS_topcoded"].sum())
    print("Redacted facility rows:", df["Facility Redacted"].sum())
    print("Total Costs dtype:", df["Total Costs"].dtype)
    print(df[["Length of Stay", "LOS_topcoded", "Facility Redacted", "Total Costs"]].head())