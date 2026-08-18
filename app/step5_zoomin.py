import altair as alt
import pandas as pd
import streamlit as st
from theme import BROWN_LIGHT, BROWN_SOFT, BROWN_MID, BROWN_DEEP, BROWN_DARK, BROWN_DARKEST, ACCENT

SEVERITY_ORDER = ["Minor", "Moderate", "Major", "Extreme"]
AGE_ORDER = ["0 to 17", "18 to 29", "30 to 49", "50 to 69", "70 or Older"]


def render(df):
    st.header("5. Zoom-In: Septicemia")
    st.markdown(
        """
Section 2 flagged Septicemia as the clearest example of the paradox: not the most
common diagnosis, but the one consuming the largest disproportionate share of bed-days.
This section takes a closer look at what a Septicemia admission actually looks like —
who it affects, how severe it tends to be, and what it costs the hospital system.
"""
    )

    sep = df[df["CCSR Diagnosis Description"] == "SEPTICEMIA"].copy()
    total_admissions = len(df)
    total_beddays = df["Length of Stay"].sum()

    share_admissions = len(sep) / total_admissions * 100
    share_beddays = sep["Length of Stay"].sum() / total_beddays * 100
    avg_cost_sep = sep["Total Costs"].mean()
    avg_cost_all = df["Total Costs"].mean()
    mortality_rate = (sep["Patient Disposition"] == "Expired").mean() * 100

    # --- Headline metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Share of admissions", f"{share_admissions:.1f}%")
    m2.metric("Share of bed-days", f"{share_beddays:.1f}%", delta=f"+{share_beddays - share_admissions:.1f} pts")
    m3.metric("Avg. cost per stay", f"${avg_cost_sep:,.0f}", delta=f"+{(avg_cost_sep/avg_cost_all - 1)*100:.0f}% vs. overall avg")
    m4.metric("In-hospital mortality", f"{mortality_rate:.1f}%")

    st.caption(
        f"Septicemia makes up {share_admissions:.1f}% of admissions but {share_beddays:.1f}% "
        f"of bed-days — the clearest confirmation of the paradox from Section 2, now isolated."
    )

    col1, col2 = st.columns(2)

    # --- Length of stay distribution: histogram ---
    with col1:
        hist = (
            alt.Chart(sep[sep["Length of Stay"] <= 40])
            .mark_bar(color=BROWN_DEEP, opacity=0.9)
            .encode(
                x=alt.X("Length of Stay:Q", bin=alt.Bin(maxbins=25), title="Length of Stay (days)"),
                y=alt.Y("count():Q", title="Number of Patients"),
                tooltip=[alt.Tooltip("count():Q", title="Patients")],
            )
            .properties(title="Distribution of Length of Stay (Septicemia)", height=300)
        )
        st.altair_chart(hist, use_container_width=True)
        st.caption("Stays longer than 40 days are excluded from this view for readability.")

    # --- Age group profile: area chart ---
    with col2:
        age_counts = (
            sep["Age Group"].value_counts().reindex(AGE_ORDER).reset_index()
        )
        age_counts.columns = ["Age Group", "Count"]

        area = (
            alt.Chart(age_counts)
            .mark_area(
                line={"color": BROWN_DARKEST},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[
                        alt.GradientStop(color=BROWN_LIGHT, offset=0),
                        alt.GradientStop(color=BROWN_DEEP, offset=1),
                    ],
                    x1=1, x2=1, y1=1, y2=0,
                ),
                interpolate="monotone",
            )
            .encode(
                x=alt.X("Age Group:N", sort=AGE_ORDER, title=None),
                y=alt.Y("Count:Q", title="Number of Patients"),
                tooltip=["Age Group", "Count"],
            )
            .properties(title="Septicemia Admissions by Age Group", height=300)
        )
        st.altair_chart(area, use_container_width=True)
        st.caption("Septicemia disproportionately affects older patients — nearly half are 70+.")

        # --- Severity and risk of mortality: paired donuts with a single shared legend ---
    st.subheader("How severe are these cases?")

    sev_counts = sep["APR Severity of Illness Description"].value_counts().reindex(SEVERITY_ORDER).reset_index()
    sev_counts.columns = ["Category", "Count"]
    sev_counts["Metric"] = "Severity of Illness"
    sev_counts["pct"] = (sev_counts["Count"] / sev_counts["Count"].sum() * 100).round(1)

    risk_counts = sep["APR Risk of Mortality"].value_counts().reindex(SEVERITY_ORDER).reset_index()
    risk_counts.columns = ["Category", "Count"]
    risk_counts["Metric"] = "Risk of Mortality"
    risk_counts["pct"] = (risk_counts["Count"] / risk_counts["Count"].sum() * 100).round(1)

    color_scale = alt.Scale(domain=SEVERITY_ORDER, range=[BROWN_LIGHT, BROWN_SOFT, BROWN_DEEP, ACCENT])

    def make_donut(data, title):
        base = alt.Chart(data).encode(
            theta=alt.Theta("Count:Q", stack=True),
            color=alt.Color("Category:N", scale=color_scale, legend=alt.Legend(title=None, orient="bottom")),
            tooltip=["Category", "Count", "pct"],
        )
        arc = base.mark_arc(innerRadius=65, outerRadius=120)
        labels = base.mark_text(radius=145, size=12, color="#333").encode(
            text=alt.Text("pct:Q", format=".0f")
        )
        return (arc + labels).properties(title=title, height=320)

    donut_sev = make_donut(sev_counts, "Severity of Illness")
    donut_risk = make_donut(risk_counts, "Risk of Mortality")

    paired = alt.hconcat(donut_sev, donut_risk).resolve_scale(color="shared")
    st.altair_chart(paired, use_container_width=True)

    st.caption(
        "Nearly half of Septicemia admissions are classified 'Extreme' on both severity of "
        "illness (48.5%) and risk of mortality (50.8%) — a much heavier case mix than the "
        "hospital-wide average from Section 3. The two measures track closely, but they are "
        "not identical: risk of mortality skews slightly higher toward 'Extreme', while "
        "severity of illness has a larger 'Major' share."
    )

    # --- Where it concentrates: top counties ---
    st.subheader("Where Septicemia cases concentrate")
    top_counties = sep["Hospital County"].value_counts().head(8).reset_index()
    top_counties.columns = ["County", "Admissions"]

    dot_county = (
        alt.Chart(top_counties)
        .mark_circle(size=220, color=BROWN_DARK)
        .encode(
            x=alt.X("Admissions:Q"),
            y=alt.Y("County:N", sort=top_counties["County"].tolist(), title=None),
            tooltip=["County", "Admissions"],
        )
    )
    rule_county = (
        alt.Chart(top_counties)
        .mark_rule(color=BROWN_SOFT)
        .encode(x="Admissions:Q", x2=alt.value(0), y=alt.Y("County:N", sort=top_counties["County"].tolist()))
    )
    st.altair_chart(rule_county + dot_county, use_container_width=True)

    st.info(
        f"""
**Closing the loop.** Septicemia is a small share of admissions but a disproportionate
share of hospital burden: {share_beddays:.1f}% of bed-days, {(avg_cost_sep/avg_cost_all - 1)*100:.0f}%
higher average cost per stay, and a {mortality_rate:.1f}% in-hospital mortality rate — far
above the hospital-wide average. It concentrates in older patients and in the state's
largest metro counties. For a records office, this is exactly the kind of diagnosis
worth flagging for capacity planning: infrequent enough to be easy to overlook in a
simple admissions count, but consequential enough to strain beds, staff, and budget
when it appears.
"""
    )