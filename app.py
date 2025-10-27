import streamlit as st
import pandas as pd
import plotly.express as px

# --- App Einstellungen ---
st.set_page_config(page_title="📦 Barcode & Lagerverwaltungssystem", layout="wide")

# --- Titel & Logo ---
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Edeka_Logo_2014.svg/512px-Edeka_Logo_2014.svg.png", width=150)

st.title("📦 Barcode & Lagerverwaltungssystem")
st.markdown("Ein interaktives System zur Verwaltung von Produkten, Beständen und Standorten im Einzelhandel.")

# --- Daten laden ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        df.columns = [c.strip().capitalize() for c in df.columns]
        if "Produktname" not in df.columns:
            df["Produktname"] = [f"Produkt {i}" for i in range(len(df))]
        if "Kategorie" not in df.columns:
            df["Kategorie"] = "Allgemein"
        if "Bestand" not in df.columns:
            df["Bestand"] = 0
        if "Preis" not in df.columns:
            df["Preis"] = 0
        if "Standort" not in df.columns:
            df["Standort"] = "Zentral"
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame(columns=["Produktname", "Kategorie", "Bestand", "Preis", "Standort"])

df = load_data()

# --- Sidebar Filter ---
st.sidebar.header("🔎 Filteroptionen")

unique_categories = sorted(df["Kategorie"].unique())
selected_categories = st.sidebar.multiselect(
    "Kategorie auswählen:", unique_categories, default=[]
)

has_standort = "Standort" in df.columns and df["Standort"].nunique() > 0
if has_standort:
    unique_locations = sorted(df["Standort"].unique())
    selected_locations = st.sidebar.multiselect(
        "Standort auswählen:", unique_locations, default=[]
    )
else:
    selected_locations = None

# Preis-Slider (aktiv nur wenn Auswahl getroffen)
if not selected_categories and (not has_standort or not selected_locations):
    st.sidebar.info("Bitte zuerst Kategorie oder Standort auswählen.")
    price_range = (float(df["Preis"].min()), float(df["Preis"].max()))
else:
    min_price = float(df["Preis"].min()) if not df["Preis"].isnull().all() else 0.0
    max_price = float(df["Preis"].max()) if not df["Preis"].isnull().all() else 0.0
    price_range = st.sidebar.slider(
        "💰 Preisbereich (€):",
        min_value=float(min_price),
        max_value=float(max_price),
        value=(float(min_price), float(max_price))
    )

# --- Daten filtern ---
filtered_df = df.copy()

if selected_categories:
    filtered_df = filtered_df[filtered_df["Kategorie"].isin(selected_categories)]
if has_standort and selected_locations:
    filtered_df = filtered_df[filtered_df["Standort"].isin(selected_locations)]
filtered_df = filtered_df[
    (filtered_df["Preis"] >= price_range[0]) &
    (filtered_df["Preis"] <= price_range[1])
]

# --- Anzeige ---
if filtered_df.empty:
    st.warning("👋 Bitte wähle Kategorie oder Standort aus, um Daten anzuzeigen.")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Lagerbestand nach Produkt")
        fig_stock = px.bar(
            filtered_df,
            x="Produktname",
            y="Bestand",
            color="Kategorie",
            text_auto=True,
            title="Lagerbestand"
        )
        st.plotly_chart(fig_stock, use_container_width=True)

    with col2:
        st.subheader("💰 Preisverteilung")
        fig_price = px.histogram(
            filtered_df,
            x="Preis",
            nbins=10,
            color="Kategorie",
            title="Preisverteilung"
        )
        st.plotly_chart(fig_price, use_container_width=True)

    st.subheader("📋 Gefilterte Produktliste")
    st.dataframe(filtered_df, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Barcode & Lagerverwaltungssystem – Erstellt von **Vitalii Shevchuk**")




