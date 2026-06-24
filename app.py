"""
app.py
Phase 5 + 6: The dashboard with Executive Brief.

Ties everything together:
  upload (or built-in) data -> clean -> categorise -> statistics
  -> recommendations -> one-click executive brief
Run it with:  streamlit run app.py
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd
import streamlit as st
import plotly.express as px

from load_data import clean_tickets
from statistics_engine import run_all_tests
from recommendations import generate_recommendations
from executive_brief import build_executive_brief

# ---------- Page setup ----------
st.set_page_config(page_title="Support Intelligence Platform", page_icon="📊", layout="wide")

st.title("Customer Support Intelligence Platform")
st.caption("Upload support data. Get findings, evidence and prioritised actions — backed by statistics, not guesswork.")

# ---------- Get the data ----------
st.sidebar.header("Data source")
choice = st.sidebar.radio(
    "Choose your data:",
    ["Use built-in sample data", "Upload my own CSV"],
)

df_raw = None
if choice == "Upload my own CSV":
    uploaded = st.sidebar.file_uploader("Upload a support CSV", type=["csv"])
    if uploaded is not None:
        df_raw = pd.read_csv(uploaded)
else:
    if os.path.exists("data/tickets.csv"):
        df_raw = pd.read_csv("data/tickets.csv")
    else:
        st.error("Built-in data not found at data/tickets.csv.")

if df_raw is None:
    st.info("Choose a data source in the sidebar to begin.")
    st.stop()

# ---------- Run the pipeline ----------
try:
    all_tickets, rated_tickets = clean_tickets(df_raw)
except Exception as e:
    st.error(f"Could not process this file. It may not match the expected support format. ({e})")
    st.stop()

findings = run_all_tests(all_tickets, rated_tickets)
significant = [f for f in findings if f["significant"]]
recs = generate_recommendations(findings)

# ---------- Top numbers ----------
st.subheader("Overview")
c1, c2, c3 = st.columns(3)
c1.metric("Tickets analysed", f"{len(all_tickets):,}")
c2.metric("Significant findings", len(significant))
if "CSAT Score" in rated_tickets.columns and len(rated_tickets):
    c3.metric("Average satisfaction", f"{rated_tickets['CSAT Score'].mean():.2f} / 5")

# ---------- Charts ----------
st.subheader("What the data looks like")
g1, g2 = st.columns(2)

if "Category" in all_tickets.columns:
    counts = all_tickets["Category"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    fig = px.bar(counts, x="Count", y="Category", orientation="h",
                 title="Complaints by category")
    g1.plotly_chart(fig, use_container_width=True)

if "CSAT Score" in rated_tickets.columns and len(rated_tickets):
    fig2 = px.histogram(rated_tickets, x="CSAT Score",
                        title="Satisfaction score distribution")
    g2.plotly_chart(fig2, use_container_width=True)

# ---------- Findings ----------
st.subheader("Findings (statistically significant only)")
if significant:
    for f in significant:
        st.markdown(f"- {f['finding']}")
else:
    st.write("No statistically significant patterns were detected in this data.")

# ---------- Recommendations ----------
st.subheader("Prioritised recommendations")
if recs:
    for i, r in enumerate(recs, 1):
        with st.expander(f"{i}. {r['action'][:70]}..."):
            st.write(r["action"])
            st.caption(f"Evidence: {r['evidence']}")
else:
    st.write("No recommendations — no significant findings to act on.")

# ---------- Executive Brief ----------
st.divider()
st.subheader("Executive Brief")
st.caption("A plain-language summary for decision-makers. Every figure comes from the data above.")

if st.button("Generate Executive Brief"):
    sections = build_executive_brief(all_tickets, rated_tickets, findings, recs)
    if not sections:
        st.write("Not enough significant findings to build a brief.")
    for s in sections:
        st.markdown(f"**Finding:** {s['finding']}")
        st.markdown(f"**Evidence:** {s['evidence']}")
        st.markdown(f"**Business Impact:** {s['impact']}")
        st.markdown(f"**Recommended Action:** {s['action']}")
        st.divider()