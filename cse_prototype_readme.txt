CSE-based Canadian MicroCap Screener Prototype

Files:
- cse_microcap_database_prototype.xlsx
  Preserves the original uploaded CSE list and adds an Enriched_Database sheet, Controls sheet, Instructions, and Dashboard.
- cse_microcap_database_template.csv
  CSV template version of the enriched database for the Streamlit app.
- streamlit_cse_microcap_app.py
  Streamlit app that uses the CSE listings as the base universe and lets you enrich/scored rows in-browser.

How it works:
1. The uploaded CSE Listings file is used as the base company universe database.
2. You fill in missing finance/investment fields manually (market cap, growth, valuation, insider buying, analyst rating, catalysts, etc.).
3. The model calculates microcap qualification and total score automatically.
4. You can rank ideas and download your enriched database.

Note:
Because the uploaded CSE list does not include market cap or valuation data, those fields are left as user-input columns.
