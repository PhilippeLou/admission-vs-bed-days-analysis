# Not All Admissions Are Equal

**An Inpatient Discharge & Length-of-Stay Analysis**
*by Philippe Louis B. Garibay*

An interactive Streamlit dashboard analyzing 74,000+ hospital inpatient discharge
records to answer a records-office question: which admissions actually consume
the most hospital capacity — not just which are the most common?

---

## About the Project

Hospital records offices generate a steady stream of admissions, diagnosis, and
discharge data every day, but this data is often used only for routine reporting.
This project treats that data as an analytical asset instead, following a
narrative-driven flow inspired by [Our World in Data's coverage of plastic
pollution](https://ourworldindata.org/plastic-pollution) — starting from a broad
volume overview, surfacing a central paradox in the data, explaining the
mechanism behind it, breaking it down by patient demographics, and closing with
a focused case-study zoom-in.

The project was built as a portfolio piece practicing the kind of operational
health analytics performed by hospital records/health information offices —
admissions volume, length-of-stay drivers, and case-mix reporting — using real,
publicly available government health data.

## The Analysis Flow

1. **The Volume Overview** — total discharges, admissions by type and age group,
   and where volume concentrates across counties.
2. **The Paradox: Admissions vs. Bed-Days** — comparing each diagnosis's share of
   admissions against its share of total bed-days, revealing that the most
   *common* diagnoses are not always the most *burdensome*.
3. **The Mechanism** — what actually drives length of stay: severity of illness,
   patient age, and admission type (planned vs. emergency).
4. **The Breakdown** — how length of stay and severity vary across gender, race,
   and payer type.
5. **Zoom-In: Septicemia** — a focused case study on the diagnosis identified in
   Section 2 as the clearest example of the paradox, examining its cost,
   mortality rate, and patient profile in detail.

## Tech Stack

- **Python** — data cleaning and analysis ([pandas](https://pandas.pydata.org/))
- **Altair** (Vega-Lite) — interactive, declarative charting
- **Streamlit** — dashboard framework and deployment

## Project Structure