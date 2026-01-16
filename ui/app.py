import streamlit as st
import requests
import pandas as pd

API_URL = "http://api:8000"

st.set_page_config(page_title="Ecommerce Dashboard", layout="wide")

def api_get(path: str, params=None):
    try:
        r = requests.get(f"{API_URL}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API indisponible ou erreur sur {path}. Détail: {e}")
        st.stop()

# ---- Sidebar menu ----
st.sidebar.title("📌 Menu")
page = st.sidebar.radio("Aller à :",["Vue générale", "Pays", "Catégories", "Transactions", "Ajouter"])
# ---- Filters from API ----
filters = api_get("/filters")
all_countries = ["(Tous)"] + filters["countries"]
all_categories = ["(Toutes)"] + filters["categories"]

country = st.sidebar.selectbox("Pays", all_countries)
category = st.sidebar.selectbox("Catégorie", all_categories)

country_param = None if country == "(Tous)" else country
category_param = None if category == "(Toutes)" else category

# ---- KPIs ----
kpi = api_get("/kpis", params={"country": country_param, "category": category_param})
orders_count = kpi["orders_count"] or 0
revenue_total = float(kpi["revenue_total"] or 0)
avg_order_value = float(kpi["avg_order_value"] or 0)

st.title("📊 Ecommerce Dashboard")

c1, c2, c3 = st.columns(3)
c1.metric("Chiffre d’affaires", f"{revenue_total:,.2f}")
c2.metric("Nombre de commandes", f"{orders_count:,}")
c3.metric("Panier moyen", f"{avg_order_value:,.2f}")

st.divider()

# ---- Pages ----
if page == "Vue générale":
    st.subheader("Top pays (CA)")
    data = api_get("/countries")
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("country")["revenue"])

    st.subheader("Top catégories (CA)")
    data2 = api_get("/categories")
    df2 = pd.DataFrame(data2)

    st.dataframe(df2, use_container_width=True)
    st.bar_chart(df2.set_index("category")["revenue"])


elif page == "Pays":
    st.subheader("Revenus par pays (filtre appliqué sur KPIs seulement)")
    data = api_get("/countries")
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("country")["revenue"])


elif page == "Catégories":
    st.subheader("Revenus par catégorie (filtre appliqué sur KPIs seulement)")
    data = api_get("/categories")
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("category")["revenue"])


elif page == "Transactions":
    st.subheader("Liste des commandes (avec filtres)")
    limit = st.sidebar.slider("Nombre de lignes", 10, 200, 50)

    params = {"limit": limit}
    if country_param:
        params["country"] = country_param
    if category_param:
        params["category"] = category_param

    orders = api_get("/orders", params=params)
    df = pd.DataFrame(orders)

    st.dataframe(df, use_container_width=True)

elif page == "Ajouter":
    st.title("➕ Ajouter une commande")

    with st.form("add_order"):
        country = st.text_input("Pays")
        category = st.text_input("Catégorie")
        unit_price = st.number_input("Prix unitaire", min_value=0.0)
        quantity = st.number_input("Quantité", min_value=1, step=1)
        order_date = st.date_input("Date")

        submitted = st.form_submit_button("Ajouter")

        if submitted:
            payload = {
                "country": country,
                "category": category,
                "unit_price": unit_price,
                "quantity": quantity,
                "order_date": str(order_date)
            }

            resp = requests.post(f"{API_URL}/orders", json=payload)

            if resp.status_code == 200:
                st.success("Commande ajoutée avec succès")
            else:
                st.error("Erreur lors de l'ajout")
