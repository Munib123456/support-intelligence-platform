"""
app.py
Phase 5 + 6: The dashboard with Executive Brief — Linear-style dark theme.

Logic is unchanged from the working version. The only additions are:
  - a CSS theme block (look only)
  - the .streamlit/config.toml dark base theme
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

# ---------- Theme (look only) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Base canvas */
.stApp {
    background:
      radial-gradient(900px 600px at 50% -10%, rgba(94,106,210,0.18), transparent 60%),
      radial-gradient(ellipse at top, #0a0a0f 0%, #050506 50%, #020203 100%);
    font-family: 'Inter', system-ui, sans-serif;
    color: #EDEDEF;
}

/* Subtle technical grid overlay */
.stApp::before {
    content: "";
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 64px 64px;
    pointer-events: none;
    z-index: 0;
}

/* Gradient headline */
h1 {
    font-weight: 600 !important;
    letter-spacing: -0.03em !important;
    background: linear-gradient(to bottom, #ffffff, rgba(255,255,255,0.70));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
h2, h3 { font-weight: 600 !important; letter-spacing: -0.01em !important; color: #EDEDEF; }

/* Metric cards — glass effect with multi-layer shadow */
[data-testid="stMetric"] {
    background: linear-gradient(to bottom, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.4), 0 0 40px rgba(0,0,0,0.2);
}
[data-testid="stMetricValue"] { color: #EDEDEF; font-weight: 600; }
[data-testid="stMetricLabel"] { color: #8A8F98; }

/* Buttons — accent with glow */
.stButton > button {
    background: #5E6AD2;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    box-shadow: 0 0 0 1px rgba(94,106,210,0.5),
                0 4px 12px rgba(94,106,210,0.3),
                inset 0 1px 0 0 rgba(255,255,255,0.2);
    transition: all 200ms cubic-bezier(0.16,1,0.3,1);
}
.stButton > button:hover {
    background: #6872D9;
    box-shadow: 0 0 0 1px rgba(94,106,210,0.6),
                0 6px 18px rgba(94,106,210,0.45),
                inset 0 1px 0 0 rgba(255,255,255,0.25);
    transform: translateY(-2px);
}

/* Expanders (recommendations) — glass cards */
[data-testid="stExpander"] {
    background: linear-gradient(to bottom, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0a0a0c;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Findings bullets spacing */
.stMarkdown p { color: #c9ccd2; }

/* Pull content above the grid overlay */
.main .block-container { position: relative; z-index: 1; }
</style>
""", unsafe_allow_html=True)

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

# Plotly theming to match the dark look
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#8A8F98",
    title_font_color="#EDEDEF",
)

if "Category" in all_tickets.columns:
    counts = all_tickets["Category"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    fig = px.bar(counts, x="Count", y="Category", orientation="h",
                 title="Complaints by category",
                 color_discrete_sequence=["#5E6AD2"])
    fig.update_layout(**PLOT_LAYOUT)
    g1.plotly_chart(fig, use_container_width=True)

if "CSAT Score" in rated_tickets.columns and len(rated_tickets):
    fig2 = px.histogram(rated_tickets, x="CSAT Score",
                        title="Satisfaction score distribution",
                        color_discrete_sequence=["#5E6AD2"])
    fig2.update_layout(**PLOT_LAYOUT)
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

# ---------- Data & Method ----------
st.divider()
with st.expander("Data & Method"):
    st.markdown("""
**Analytics dataset:** Customer Support Data (~82,000 real support records, public, via Kaggle).

**NLP training dataset:** CFPB Consumer Complaint Database (real, human-written complaint narratives with verified category labels).

**Statistical methods:** chi-square test of independence (category vs category), Kruskal-Wallis test (a numeric measure across categorical groups), and Spearman rank correlation (two ordinal/continuous measures). A result is reported as a finding only when p < 0.05.

**Significance vs effect size:** because the dataset is large, most tests reach statistical significance, so effect size (e.g. the Spearman r) is also reported to show how strong each relationship actually is.

**Role of AI:** the language model is used only to phrase the executive summary. Every finding and every number comes from the statistical analysis, not the model.
    """)