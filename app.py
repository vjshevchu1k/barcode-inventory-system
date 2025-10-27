import streamlit as st
import pandas as pd
import plotly.express as px

# --- Seiteneinstellungen ---
st.set_page_config(page_title="📦 Barcode & Lagerverwaltungssystem", layout="wide")

# --- Logo und Titel ---
st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Deutsche_Telekom_Logo_2013.svg", width=150)
st.title("📦 Barcode & Lagerverwaltungssystem")
st.markdown("Ein interaktives System zur Verwaltung von Produkten, Beständen und Standorten im Einzelhandel.")

# --- Daten laden ---
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

df = load_data()

# --- Filterbereich ---
st.sidebar.header("🔍 Filter")
category = st.sidebar.selectbox("Kategorie auswählen:", sorted(df["Kategorie"].unique()))
location = st.sidebar.selectbox("Standort auswählen:", sorted(df["Standort"].unique()))

filtered_df = df[(df["Kategorie"] == category) & (df["Standort"] == location)]

# --- Barcode-Suche ---
st.subheader("🔎 Produktsuche")
barcode_input = st.text_input("Bitte Barcode eingeben:", "")

if barcode_input:
    product = df[df["Barcode"].astype(str) == barcode_input]
    if not product.empty:
        st.success(f"**Produkt gefunden:** {product.iloc[0]['Produktname']}")
        st.write(product)
    else:
        st.error("❌ Kein Produkt mit diesem Barcode gefunden.")

# --- Datenanzeige ---
st.subheader(f"📋 Produktliste ({category} – {location})")
st.dataframe(filtered_df, use_container_width=True)

# --- Diagramm ---
st.subheader("📊 Gesamtmenge pro Kategorie")
fig = px.bar(df.groupby("Kategorie")["Menge"].sum().reset_index(),
             x="Kategorie", y="Menge", title="Gesamtmenge pro Kategorie")
st.plotly_chart(fig, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Telekom Lagerverwaltung – Erstellt von **Vitalii Shevchuk**, Münster, Deutschland")
