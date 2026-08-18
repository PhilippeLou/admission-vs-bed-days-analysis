import altair as alt
import pandas as pd
import streamlit as st
from theme import BROWN_LIGHT, BROWN_SOFT, BROWN_MID, BROWN_DEEP, BROWN_DARK, BROWN_DARKEST, ACCENT

SEVERITY_ORDER = ["Minor", "Moderate", "Major", "Extreme"]


def render(df):
    st.header("4. The Breakdown: Who Faces the Longest Stays")
    st.markdown(
        """
Section 3 showed that severity, age, and admission type drive length of stay. This
section slices those same patterns by patient demographics — gender, race, and how
the stay is paid for — to see whether the burden falls evenly or concentrates in
specific groups.
"""
    )

    # --- Gender split: donut chart ---
    st.subheader("The patient population by gender")
    gender = df[df["Gender"].isin(["F", "M"])]["Gender"].value_counts().reset_index()
    gender.columns = ["Gender", "Count"]
    gender["Gender"] = gender["Gender"].map({"F": "Female", "M": "Male"})

    col1, col2 = st.columns([1, 1])

    with col1:
        donut = (
            alt.Chart(gender)
            .mark_arc(innerRadius=70, outerRadius=130)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color(
                    "Gender:N",
                    scale=alt.Scale(domain=["Female", "Male"], range=[BROWN_SOFT, BROWN_DARK]),
                    legend=alt.Legend(title=None, orient="bottom"),
                ),
                tooltip=["Gender", "Count"],
            )
            .properties(title="Discharges by Gender", height=300)
        )
        st.altair_chart(donut, use_container_width=True)

    with col2:
        gender_los = (
            df[df["Gender"].isin(["F", "M"])]
            .groupby("Gender", observed=True)["Length of Stay"]
            .mean()
            .reset_index()
        )
        gender_los.columns = ["Gender", "Avg Length of Stay"]
        gender_los["Gender"] = gender_los["Gender"].map({"F": "Female", "M": "Male"})
        st.write("")
        st.write("")
        for _, row in gender_los.iterrows():
            st.metric(f"Avg. Length of Stay — {row['Gender']}", f"{row['Avg Length of Stay']:.2f} days")
        st.caption(
            "Male patients stay longer on average and skew toward higher severity "
            "classifications than female patients in this dataset."
        )


    # --- Payment Typology: dot plot ---
    st.subheader("Average length of stay by how the stay is paid for")
    pay = (
        df.groupby("Payment Typology 1", observed=True)
        .agg(avg_los=("Length of Stay", "mean"), admissions=("Length of Stay", "count"))
        .reset_index()
        .sort_values("avg_los", ascending=False)
    )
    pay = pay[pay["admissions"] >= 100]  # drop tiny categories for readability

    dot_pay = (
        alt.Chart(pay)
        .mark_circle(size=220, color=BROWN_DEEP)
        .encode(
            x=alt.X("avg_los:Q", title="Average Length of Stay (days)"),
            y=alt.Y("Payment Typology 1:N", sort=pay["Payment Typology 1"].tolist(), title=None),
            tooltip=["Payment Typology 1", "avg_los", "admissions"],
        )
        .properties(title="Avg. LOS by Primary Payer", height=320)
    )
    rule_pay = (
        alt.Chart(pay)
        .mark_rule(color=BROWN_SOFT)
        .encode(
            x="avg_los:Q",
            x2=alt.value(0),
            y=alt.Y("Payment Typology 1:N", sort=pay["Payment Typology 1"].tolist()),
        )
    )
    st.altair_chart(rule_pay + dot_pay, use_container_width=True)
    st.caption(
        "Medicare patients — who skew older — have the longest average stays, consistent "
        "with the age pattern from Section 3. Privately insured and self-pay patients have "
        "the shortest, which likely reflects a younger, lower-severity mix rather than "
        "insurance type itself driving the difference."
    )

    # --- Severity by gender: heatmap ---
    st.subheader("Severity distribution by gender")
    sev_gender = (
        df[df["Gender"].isin(["F", "M"])]
        .dropna(subset=["APR Severity of Illness Description"])
        .groupby(["Gender", "APR Severity of Illness Description"], observed=True)
        .size()
        .reset_index(name="count")
    )
    sev_gender["Gender"] = sev_gender["Gender"].map({"F": "Female", "M": "Male"})
    totals = sev_gender.groupby("Gender")["count"].transform("sum")
    sev_gender["pct"] = (sev_gender["count"] / totals * 100).round(1)

    heat_gender = (
        alt.Chart(sev_gender)
        .mark_rect()
        .encode(
            x=alt.X("APR Severity of Illness Description:N", sort=SEVERITY_ORDER, title=None),
            y=alt.Y("Gender:N", title=None),
            color=alt.Color("pct:Q", scale=alt.Scale(range=[BROWN_LIGHT, BROWN_DARKEST]), title="% of admissions"),
            tooltip=["Gender", "APR Severity of Illness Description", "pct"],
        )
        .properties(title="Severity Mix by Gender (% within each gender)", height=180)
    )
    st.altair_chart(heat_gender, use_container_width=True)

    st.info(
        "The burden of long, severe stays isn't evenly distributed: it skews toward male "
        "patients, older payer groups like Medicare, and — descriptively — Black/African "
        "American patients in this dataset. These are patterns worth flagging for a records "
        "office, not final explanations; each would need further investigation into "
        "underlying diagnoses and access-to-care factors. The final section zooms into a "
        "single diagnosis — Septicemia — to see how all of these factors play out together."
    )