# Canadian MicroCap Investment Screener Prototype

This project is a prototype decision-support tool for identifying Canadian microcap investment opportunities.

## Features

- Filters Canadian-listed companies (TSX, TSXV, CSE)
- Applies configurable microcap market cap threshold
- Scores companies using valuation, growth, insider buying, analyst sentiment, management quality, and catalysts
- Ranks opportunities automatically
- Allows dataset updates via CSV

## Files Included

- canadian_microcap_sample_data.csv → dataset
- streamlit_microcap_app.py → Streamlit screener interface

## How to Run the App

Install dependencies:

pip install streamlit pandas

Run locally:

streamlit run streamlit_microcap_app.py

Or deploy using Streamlit Cloud.
