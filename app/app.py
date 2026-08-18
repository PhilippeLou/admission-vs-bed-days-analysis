"""
Hospital Inpatient Discharges Analysis — 2021 SPARCS Data
Story flow modeled on OWID's "Plastic Pollution" narrative:
  1. Volume overview
  2. The paradox — admissions vs. bed-days
  3. Mechanism — what drives length of stay
  4. Breakdown — LOS/severity by demographic group
  5. Zoom-in — one diagnosis category deep dive
"""

import pandas as pd
import altair as alt
import streamlit as st

from clean_data import load_and_clean

st.set_page_config(page_title="Inpatient Discharges Analysis", layout="wide")

# ---------- Load data ----------
@st.cache_data
def get_data():
    return load_and_clean("../data/discharges_raw.csv")

df = get_data()

st.title("Not All Admissions Are Equal")
st.caption("An inpatient discharge & length-of-stay analysis — NY SPARCS 2021 data")

# ==========================================================
# STEP 1: VOLUME OVERVIEW
# ==========================================================
st.header("1. The Volume Overview")
st.write(
    f"In 2021, this dataset recorded **{len(df):,} inpatient discharges** "
    f"across **{df['Hospital County'].nunique()} counties** and "
    f"**{df['Facility Name'].nunique()} facilities**."
)

col1, col2 = st.columns(2)

with col1:
    admissions_by_type = (
        df["Type of Admission"].value_counts().reset_index()
    )
    admissions_by_type.columns = ["Type of Admission", "Count"]

    chart1 = (
        alt.Chart(admissions_by_type)
        .mark_bar()
        .encode(
            x=alt.X("Count:Q", title="Number of Discharges"),
            y=alt.Y("Type of Admission:N", sort="-x", title=None),
            tooltip=["Type of Admission", "Count"],
            color=alt.value("#2b6cb0"),
        )
        .properties(title="Discharges by Admission Type", height=250)
    )
    st.altair_chart(chart1, use_container_width=True)

with col2:
    admissions_by_age = (
        df["Age Group"].value_counts().reindex(
            ["0 to 17", "18 to 29", "30 to 49", "50 to 69", "70 or Older"]
        ).reset_index()
    )
    admissions_by_age.columns = ["Age Group", "Count"]

    chart2 = (
        alt.Chart(admissions_by_age)
        .mark_bar()
        .encode(
            x=alt.X("Age Group:N", sort=None, title=None),
            y=alt.Y("Count:Q", title="Number of Discharges"),
            tooltip=["Age Group", "Count"],
            color=alt.value("#38a169"),
        )
        .properties(title="Discharges by Age Group", height=250)
    )
    st.altair_chart(chart2, use_container_width=True)

# Top counties by volume
st.subheader("Where the volume concentrates")
top_counties = (
    df["Hospital County"].value_counts().head(10).reset_index()
)
top_counties.columns = ["Hospital County", "Count"]

chart3 = (
    alt.Chart(top_counties)
    .mark_bar()
    .encode(
        x=alt.X("Count:Q", title="Number of Discharges"),
        y=alt.Y("Hospital County:N", sort="-x", title=None),
        tooltip=["Hospital County", "Count"],
        color=alt.value("#805ad5"),
    )
    .properties(title="Top 10 Counties by Discharge Volume", height=350)
)
st.altair_chart(chart3, use_container_width=True)

st.info(
    "This is the baseline picture — raw volume. But volume alone doesn't tell us "
    "where the real burden on the hospital system lies. The next section looks at "
    "the paradox: does the number of admissions actually match the number of bed-days consumed?"
)