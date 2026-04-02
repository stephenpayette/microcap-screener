import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CSE MicroCap Screener", layout="wide")

DEFAULT_PATH = "cse_microcap_database_template.csv"

@st.cache_data
def load_default():
    return pd.read_csv(DEFAULT_PATH)

def normalize_df(df):
    needed = ["Company","Ticker","Exchange","Industry","Identifier","Indices","Currency","Trading Date","Tier",
              "Market Cap ($M)","Revenue Growth %","P/S","EV/EBITDA","Insider Buying","Analyst Rating",
              "Pending Catalyst","Management Score","Notes","Last Updated","Source"]
    for c in needed:
        if c not in df.columns:
            df[c] = ""
    if "Exchange" not in df.columns:
        df["Exchange"] = "CSE"
    return df[needed]

def score_growth(g):
    if pd.isna(g): return None
    if g > 30: return 3
    if g > 20: return 2
    if g >= 10: return 1
    return 0

def score_valuation(ps, ev):
    if pd.isna(ps) or pd.isna(ev): return None
    return (2 if ps < 2 else 1 if ps <= 4 else 0) + (2 if ev < 7 else 1 if ev <= 10 else 0)

def score_insider(v):
    if v == "Strong": return 2
    if v == "Moderate": return 1
    if v == "None": return 0
    return None

def score_analyst(v):
    if v == "Buy": return 2
    if v == "Spec Buy": return 1
    if v == "Hold": return 0
    return None

def score_catalyst(v):
    return 2 if isinstance(v, str) and v.strip() else None

def compute(df, threshold):
    out = df.copy()
    for col in ["Market Cap ($M)","Revenue Growth %","P/S","EV/EBITDA","Management Score"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["Exchange Eligible"] = out["Exchange"].eq("CSE")
    out["Market Cap Eligible"] = out["Market Cap ($M)"].le(threshold)
    out["MicroCap Qualified"] = out["Exchange Eligible"] & out["Market Cap Eligible"]
    out["Growth Score"] = out["Revenue Growth %"].apply(score_growth)
    out["Valuation Score"] = [score_valuation(ps, ev) for ps, ev in zip(out["P/S"], out["EV/EBITDA"])]
    out["Insider Score"] = out["Insider Buying"].apply(score_insider)
    out["Analyst Score"] = out["Analyst Rating"].apply(score_analyst)
    out["Catalyst Score"] = out["Pending Catalyst"].apply(score_catalyst)
    components = ["Growth Score","Valuation Score","Insider Score","Analyst Score","Catalyst Score","Management Score"]
    out["Total Score"] = out[components].sum(axis=1, min_count=6)
    out["Reason to Buy"] = ""
    out.loc[(out["Revenue Growth %"] >= 30) & (out["Total Score"] >= 9), "Reason to Buy"] = "Momentum"
    out.loc[(out["P/S"] < 1.5) & (out["EV/EBITDA"] < 6.5) & (out["Reason to Buy"] == ""), "Reason to Buy"] = "Value Play"
    out.loc[(out["Pending Catalyst"].astype(str).str.strip() != "") & (out["Total Score"] >= 8) & (out["Reason to Buy"] == ""), "Reason to Buy"] = "Catalyst-Driven"
    out.loc[(out["Reason to Buy"] == "") & out["Total Score"].notna(), "Reason to Buy"] = "Undervalued"
    return out

st.title("CSE-Based Canadian MicroCap Screener")
st.caption("Uses your uploaded CSE Listings file as the company universe database. Add financial inputs manually to enrich and score names.")

upload = st.sidebar.file_uploader("Upload an updated CSV database (optional)", type=["csv"])
threshold = st.sidebar.number_input("MicroCap threshold ($M CAD)", min_value=25, max_value=500, value=300, step=25)
industry_filter = st.sidebar.multiselect("Industry filter", options=[])
only_qualified = st.sidebar.checkbox("Show only qualified microcaps", value=False)

if "db" not in st.session_state:
    st.session_state.db = load_default()

if upload is not None:
    st.session_state.db = normalize_df(pd.read_csv(upload))

base = normalize_df(st.session_state.db)
all_industries = sorted([x for x in base["Industry"].dropna().astype(str).unique() if x.strip()])
if not industry_filter:
    industry_filter = all_industries

st.subheader("1) Edit / enrich the database")
editable_cols = ["Market Cap ($M)","Revenue Growth %","P/S","EV/EBITDA","Insider Buying","Analyst Rating","Pending Catalyst","Management Score","Notes","Last Updated"]
display_cols = ["Company","Ticker","Industry","Tier"] + editable_cols

edited = st.data_editor(
    base[display_cols],
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Insider Buying": st.column_config.SelectboxColumn(options=["", "Strong","Moderate","None"]),
        "Analyst Rating": st.column_config.SelectboxColumn(options=["", "Buy","Spec Buy","Hold"]),
        "Last Updated": st.column_config.DateColumn("Last Updated"),
    },
    key="editor"
)

# Merge edits back into base by row order
for col in editable_cols:
    base[col] = edited[col]

scored = compute(base, threshold)
filtered = scored[scored["Industry"].astype(str).isin(industry_filter)].copy()
if only_qualified:
    filtered = filtered[filtered["MicroCap Qualified"]]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Database companies", len(scored))
c2.metric("Rows with market cap entered", int(scored["Market Cap ($M)"].notna().sum()))
c3.metric("Qualified microcaps", int(scored["MicroCap Qualified"].sum()))
avg_score = round(float(filtered["Total Score"].dropna().mean()), 1) if filtered["Total Score"].notna().any() else 0.0
c4.metric("Average score", avg_score)

st.subheader("2) Ranked opportunities")
ranked = filtered[filtered["Total Score"].notna()].sort_values(["Total Score","Revenue Growth %"], ascending=[False,False])
st.dataframe(
    ranked[["Ticker","Company","Industry","Market Cap ($M)","Revenue Growth %","P/S","EV/EBITDA","Total Score","Reason to Buy","Pending Catalyst"]],
    use_container_width=True
)

st.subheader("3) Database screening view")
st.dataframe(
    filtered[["Ticker","Company","Industry","Tier","Market Cap ($M)","Exchange Eligible","Market Cap Eligible","MicroCap Qualified","Total Score","Reason to Buy"]],
    use_container_width=True
)

download_df = scored.copy()
st.download_button(
    "Download enriched database as CSV",
    data=download_df.to_csv(index=False).encode("utf-8"),
    file_name="cse_microcap_enriched_database.csv",
    mime="text/csv"
)

st.info("Tip: start by entering Market Cap, Revenue Growth, P/S, EV/EBITDA, Insider Buying, Analyst Rating, and a short catalyst note for the companies you want to analyze.")
