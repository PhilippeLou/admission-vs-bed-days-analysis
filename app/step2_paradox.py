import altair as alt
import streamlit as st
from theme import BROWN_SOFT, BROWN_DARKEST, BROWN_LIGHT, ACCENT


def render(df):
    st.header("2. The Paradox: Admissions vs. Bed-Days")
    st.markdown(
        """
A diagnosis that shows up often in admissions isn't necessarily the one that occupies
hospital beds the longest. To see where the real burden lies, we compare each
diagnosis's **share of total admissions** against its **share of total bed-days**
(the sum of every patient's length of stay for that diagnosis).

If a diagnosis's bed-day share is much larger than its admission share, it means
patients with that condition are disproportionately occupying capacity relative to
how often they're admitted — the opposite is true when the admission share is larger.
"""
    )

    diag = (
        df.groupby("CCSR Diagnosis Description", observed=True)
        .agg(admissions=("Length of Stay", "count"), bed_days=("Length of Stay", "sum"))
        .reset_index()
    )
    diag["share_admissions"] = diag["admissions"] / diag["admissions"].sum() * 100
    diag["share_beddays"] = diag["bed_days"] / diag["bed_days"].sum() * 100
    diag["gap"] = diag["share_beddays"] - diag["share_admissions"]

    top_diag = diag.sort_values("admissions", ascending=False).head(12).copy()

    compare = top_diag.melt(
        id_vars="CCSR Diagnosis Description",
        value_vars=["share_admissions", "share_beddays"],
        var_name="Measure",
        value_name="Share (%)",
    )
    compare["Measure"] = compare["Measure"].map(
        {"share_admissions": "Share of Admissions", "share_beddays": "Share of Bed-Days"}
    )

    chart_paradox = (
        alt.Chart(compare)
        .mark_bar()
        .encode(
            y=alt.Y("CCSR Diagnosis Description:N", sort=top_diag["CCSR Diagnosis Description"].tolist(), title=None),
            x=alt.X("Share (%):Q"),
            color=alt.Color(
                "Measure:N",
                scale=alt.Scale(
                    domain=["Share of Admissions", "Share of Bed-Days"],
                    range=[BROWN_SOFT, BROWN_DARKEST],
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            yOffset="Measure:N",
            tooltip=["CCSR Diagnosis Description", "Measure", "Share (%)"],
        )
        .properties(title="Share of Admissions vs. Share of Bed-Days (Top 12 Diagnoses by Volume)", height=450)
    )
    st.altair_chart(chart_paradox, use_container_width=True)

    st.subheader("Where the gap is biggest")
    gap_top = diag[diag["admissions"] >= 100].sort_values("gap", ascending=False).head(5)
    gap_bottom = diag[diag["admissions"] >= 100].sort_values("gap").head(5)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Disproportionate bed-day burden** (occupies more capacity than its admission share implies)")
        chart_gap_top = (
            alt.Chart(gap_top)
            .mark_bar()
            .encode(
                x=alt.X("gap:Q", title="Bed-day share minus admission share (pts)"),
                y=alt.Y("CCSR Diagnosis Description:N", sort="-x", title=None),
                tooltip=["CCSR Diagnosis Description", "admissions", "bed_days", "gap"],
                color=alt.value(ACCENT),
            )
            .properties(height=250)
        )
        st.altair_chart(chart_gap_top, use_container_width=True)

    with col4:
        st.markdown("**Low burden relative to volume** (common admissions, quick stays)")
        chart_gap_bottom = (
            alt.Chart(gap_bottom)
            .mark_bar()
            .encode(
                x=alt.X("gap:Q", title="Bed-day share minus admission share (pts)"),
                y=alt.Y("CCSR Diagnosis Description:N", sort="x", title=None),
                tooltip=["CCSR Diagnosis Description", "admissions", "bed_days", "gap"],
                color=alt.value(BROWN_LIGHT),
            )
            .properties(height=250)
        )
        st.altair_chart(chart_gap_bottom, use_container_width=True)

    st.info(
        "**Septicemia** stands out as the clearest example of the paradox: it is not the most "
        "frequent diagnosis, but it consumes a disproportionately large share of hospital "
        "bed-days. Several mental health conditions show the same pattern. Meanwhile, common "
        "admissions like newborn deliveries and osteoarthritis take up beds only briefly. "
        "The next section digs into *why* — what actually drives a long length of stay."
    )