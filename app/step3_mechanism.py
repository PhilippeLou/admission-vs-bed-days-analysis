import altair as alt
import pandas as pd
import streamlit as st
from theme import BROWN_LIGHT, BROWN_SOFT, BROWN_MID, BROWN_DEEP, BROWN_DARK, BROWN_DARKEST, ACCENT

SEVERITY_ORDER = ["Minor", "Moderate", "Major", "Extreme"]
ADMISSION_ORDER = ["Newborn", "Elective", "Urgent", "Emergency", "Trauma"]
AGE_ORDER = ["0 to 17", "18 to 29", "30 to 49", "50 to 69", "70 or Older"]


def render(df):
    st.header("3. The Mechanism: What Drives Length of Stay")
    st.markdown(
        """
The paradox in Section 2 shows *which* diagnoses carry a disproportionate bed-day
burden. This section asks *why* — what patient- and case-level factors actually
push length of stay up. Three candidates: how severe the illness is, how old the
patient is, and how the patient was admitted (planned vs. emergency).
"""
    )

    # --- Severity of Illness: box plot built from pre-aggregated quartiles ---
    # (Altair caps inline datasets at 5,000 rows; this dataset has 70,000+, so we
    # summarize to one row per severity level instead of passing raw records.)
    st.subheader("Severity of illness is the strongest driver")
    sev_raw = df.dropna(subset=["APR Severity of Illness Description", "Length of Stay"])

    sev_stats = (
        sev_raw.groupby("APR Severity of Illness Description", observed=True)["Length of Stay"]
        .quantile([0.05, 0.25, 0.5, 0.75, 0.95])
        .unstack()
        .reindex(SEVERITY_ORDER)
        .reset_index()
    )
    sev_stats.columns = ["Severity", "p05", "q1", "median", "q3", "p95"]

    color_scale = alt.Scale(domain=SEVERITY_ORDER, range=[BROWN_LIGHT, BROWN_SOFT, BROWN_DEEP, ACCENT])
    base_sev = alt.Chart(sev_stats).encode(
        x=alt.X("Severity:N", sort=SEVERITY_ORDER, title=None)
    )

    whiskers = base_sev.mark_rule(color=BROWN_MID).encode(
        y=alt.Y("p05:Q", title="Length of Stay (days)"), y2="p95:Q"
    )
    box = base_sev.mark_bar(size=45).encode(
        y="q1:Q",
        y2="q3:Q",
        color=alt.Color("Severity:N", scale=color_scale, legend=None),
        tooltip=["Severity", "p05", "q1", "median", "q3", "p95"],
    )
    median_tick = base_sev.mark_tick(color="white", thickness=2, size=45).encode(y="median:Q")

    chart_sev = (whiskers + box + median_tick).properties(
        title="Length of Stay by Severity of Illness (5th–95th percentile range, box = middle 50%)",
        height=350,
    )
    st.altair_chart(chart_sev, use_container_width=True)
    st.caption(
        "Each box shows the middle 50% of stays for that severity level, with the white tick "
        "marking the median and the thin line spanning the 5th-95th percentile range. Not "
        "only does the typical stay grow with severity, but the spread widens too — "
        "'Extreme' cases are both longer on average and far more unpredictable in duration."
    )

    col1, col2 = st.columns(2)

    # --- Age Group: line chart, since age groups are ordinal and this shows the trend ---
    with col1:
        age_los = (
            df.groupby("Age Group", observed=True)["Length of Stay"]
            .mean()
            .reindex(AGE_ORDER)
            .reset_index()
        )
        age_los.columns = ["Age Group", "Avg Length of Stay"]
        age_los["order"] = range(len(age_los))

        line = (
            alt.Chart(age_los)
            .mark_line(color=BROWN_DEEP, strokeWidth=3, point=alt.OverlayMarkDef(size=80, color=BROWN_DARKEST))
            .encode(
                x=alt.X("Age Group:N", sort=AGE_ORDER, title=None),
                y=alt.Y("Avg Length of Stay:Q", title="Average Length of Stay (days)"),
                tooltip=["Age Group", "Avg Length of Stay"],
            )
            .properties(title="Average LOS Rises Steadily with Age", height=300)
        )
        st.altair_chart(line, use_container_width=True)

    # --- Admission Type: single-layer dot plot (lighter to render than a lollipop) ---
    with col2:
        adm_los = (
            df.dropna(subset=["Type of Admission"])
            .groupby("Type of Admission", observed=True)["Length of Stay"]
            .mean()
            .reindex(ADMISSION_ORDER)
            .dropna()
            .reset_index()
        )
        adm_los.columns = ["Type of Admission", "Avg Length of Stay"]

        dot_chart = (
            alt.Chart(adm_los)
            .mark_circle(size=260, color=BROWN_DARK, opacity=0.9)
            .encode(
                y=alt.Y("Type of Admission:N", sort=ADMISSION_ORDER, title=None),
                x=alt.X("Avg Length of Stay:Q", title="Average Length of Stay (days)"),
                tooltip=["Type of Admission", "Avg Length of Stay"],
            )
            .properties(title="Average LOS by Admission Type", height=300)
        )
        st.altair_chart(dot_chart, use_container_width=True)

    # --- Combined view: severity x admission type heatmap ---
    st.subheader("Severity and admission type together")
    combo = (
        df.dropna(subset=["APR Severity of Illness Description", "Type of Admission"])
        .groupby(["Type of Admission", "APR Severity of Illness Description"], observed=True)["Length of Stay"]
        .mean()
        .reset_index()
    )
    combo.columns = ["Type of Admission", "Severity", "Avg Length of Stay"]

    chart_heat = (
        alt.Chart(combo)
        .mark_rect()
        .encode(
            x=alt.X("Severity:N", sort=SEVERITY_ORDER, title=None),
            y=alt.Y("Type of Admission:N", sort=ADMISSION_ORDER, title=None),
            color=alt.Color(
                "Avg Length of Stay:Q",
                scale=alt.Scale(range=[BROWN_LIGHT, BROWN_DARKEST]),
                title="Avg LOS (days)",
            ),
            tooltip=["Type of Admission", "Severity", "Avg Length of Stay"],
        )
        .properties(title="Average Length of Stay: Admission Type × Severity", height=280)
    )
    st.altair_chart(chart_heat, use_container_width=True)

    st.info(
        "Severity of illness has the strongest individual effect on length of stay, and "
        "it compounds with admission type: an emergency or trauma admission classified as "
        "'Extreme' severity results in by far the longest average stays. Elective admissions, "
        "even at high severity, tend to stay shorter — likely because they're scheduled and "
        "prepared for in advance rather than reactive. The next section breaks this down "
        "further by demographic group to see who is most affected."
    )