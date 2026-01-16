import streamlit as st
import requests
import pandas as pd

API_URL = "http://api:8000"
st.set_page_config(page_title="Ecommerce Dashboard", layout="wide")

st.title("📊 Ecommerce Dashboard")

# ---- Revenue by country ----
st.header("Revenue by country")

resp = requests.get(f"{API_URL}/countries")
data = resp.json()

df_countries = pd.DataFrame(data)
st.dataframe(df_countries)

st.bar_chart(
    df_countries.set_index("country")["revenue"]
)

# ---- Revenue by category ----
st.header("Revenue by category")

resp = requests.get(f"{API_URL}/categories")
data = resp.json()

df_categories = pd.DataFrame(data)
st.dataframe(df_categories)

st.bar_chart(
    df_categories.set_index("category")["revenue"]
)
