import streamlit as st
import pandas as pd

st.set_page_config(page_title="Canadian MicroCap Screener", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("canadian_microcap_sample_data.csv")

def score_growth(g):
    if g > 30: return 3
    if g > 20: return 2
    if g >= 10: return 1
    return 0

def score_valuation(ps, ev):
    score = 0
    score += 2 if ps < 2 else 1 if ps <= 4 else 0
    score += 2 if ev < 7 else 1 if ev <= 10 else 0
    return score

def score_insider(x):
    return 2 if x == "Strong" else 1 if x == "Moderate" else 0

def score_analyst(x):
    return 2 if x == "Buy" else 1 if x == "Spec Buy" else 0

def reason_to_buy(row):
    if row["Revenue Growth %"] >= 30 and row["Total Score"] >= 9:
        return "Momentum"
    if row["P/S"] < 1.5 and row["EV/EBITDA"] < 6.5:
        return "Value Play"
    if row["Pending Catalyst"] and row["Total Score"] >= 8:
        return "Catalyst-Driven"
    return "Undervalued"

df = load_data()

st.title("Canadian MicroCap Investment Screener")
st.write("Prototype tool for screening and presenting Canadian microcap investment opportunities.")

threshold = st.sidebar.number_input("MicroCap threshold ($M CAD)", min_value=25, max_value=500, value=300, step=25)
exchange = st.sidebar.multiselect("Exchange", sorted(df["Exchange"].unique()), default=sorted(df["Exchange"].unique()))
sector = st.sidebar.multiselect("Sector", sorted(df["Sector"].unique()), default=sorted(df["Sector"].unique()))
min_score = st.sidebar.slider("Minimum total score", 0, 20, 0)

df["MicroCap Qualified"] = df["Exchange"].isin(["TSX","TSXV","CSE"]) & (df["Market Cap ($M)"] <= threshold)
df["Growth Score"] = df["Revenue Growth %"].apply(score_growth)
df["Valuation Score"] = [score_valuation(ps, ev) for ps, ev in zip(df["P/S"], df["EV/EBITDA"])]
df["Insider Score"] = df["Insider Buying"].apply(score_insider)
df["Analyst Score"] = df["Analyst Rating"].apply(score_analyst)
df["Catalyst Score"] = df["Pending Catalyst"].apply(lambda x: 2 if str(x).strip() else 0)
df["Total Score"] = df["Growth Score"] + df["Valuation Score"] + df["Insider Score"] + df["Analyst Score"] + df["Catalyst Score"] + df["Management Score"]
df["Reason to Buy"] = df.apply(reason_to_buy, axis=1)

filtered = df[(df["MicroCap Qualified"]) & (df["Exchange"].isin(exchange)) & (df["Sector"].isin(sector)) & (df["Total Score"] >= min_score)].sort_values("Total Score", ascending=False)

c1, c2, c3 = st.columns(3)
c1.metric("Qualified opportunities", len(filtered))
c2.metric("Average score", round(filtered["Total Score"].mean(), 1) if len(filtered) else 0)
c3.metric("Top idea", filtered.iloc[0]["Ticker"] if len(filtered) else "-")

st.subheader("Ranked opportunities")
st.dataframe(filtered, use_container_width=True)

st.subheader("Top 5")
st.dataframe(filtered[["Ticker","Company","Total Score","Reason to Buy","Pending Catalyst"]].head(5), use_container_width=True)

st.subheader("Update capability")
st.write("To update the prototype, edit the CSV file and rerun the app. Scores will refresh automatically.")
