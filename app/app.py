import streamlit as st
from clean_data import load_and_clean
import step1_volume
import step2_paradox
import step3_mechanism

st.set_page_config(page_title="Inpatient Discharges Analysis", layout="wide")

st.markdown("""
<style>
.block-container {
    max-width: 1000px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return load_and_clean("../data/discharges_raw.csv")


df = get_data()

st.title("Not All Admissions Are Equal")
st.markdown("**by Philippe Louis B. Garibay**")
st.markdown(
    """
Hospital records offices generate a steady stream of data every day — admissions,
diagnoses, length of stay, discharges — but this data is often used only for routine
reporting, not for uncovering the patterns hidden inside it.

In 2021 alone, this dataset recorded over 74,000 inpatient discharges across New York
State, spanning everything from routine childbirth to COVID-19 to chronic disease
management. Every discharge carries a story: how long the patient stayed, how severe
their condition was, and how much it cost the system to treat them.

However, not all admissions place the same burden on a hospital. A patient admitted for
a same-day procedure and discharged the next morning does not strain a hospital's
capacity the same way a patient who stays for weeks does. Understanding *which* patients,
diagnoses, and conditions actually consume the most hospital resources — not just which
are the most common — is critical to how a records or planning office allocates beds,
staff, and attention.

This page presents an analysis of that question, following the flow of the data from a
broad volume overview down to a focused look at what drives long hospital stays.
"""
)

step1_volume.render(df)
step2_paradox.render(df)
step3_mechanism.render(df)