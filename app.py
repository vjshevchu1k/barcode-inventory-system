import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="📦 Barcode & Lagerverwaltungssystem", layout="wide")

# 🏪 Вічний логотип EDEKA (офіційна Wikimedia URL)
st.image("https://upload.wikimedia.org/wikipedia/commons/7/70/Edeka_Logo.svg", width=120)

st.title("📦 Barcode & Lagerverwaltungssystem")
st.markdown("Ein interaktives System zur Verwaltung von Produkten, Beständen und Standorten im Einzelhandel.")
st.markdown("---")

# 🧩 Завантаження даних
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        st.error("❌ Datei 'data.csv' wurde nicht gefunden.")
        return pd.DataFrame(columns=["Produktname", "Preis", "Bestand", "Standort", "Kategorie"])
    
    # Уніфікуємо назви колонок
    df.columns = [col.strip().capitalize() for col in df.columns]

    # Якщо відсутні ключові колонки — додаємо заглушки
    if "Standort" not in df.columns:
        df["Standort"] = "Filiale A"
    if "Kategorie" not in df.columns:
        df["Kategorie"] = "Allgemein"

    return df

df = load_data()

# 📊 Фільтри
standorte = sorted(df["Standort"].unique()) if not df.empty else []
kategorien = sorted(df["Kategorie"].unique()) if not df.empty else []

col1, col2 = st.sidebar.columns(2)
with col1:
    selected_standort = st.selectbox("📍 Standort auswählen:", standorte)
with col2:
    selected_kategorie = st.selectbox("🏷️ Kategorie:", kategorien)

filtered_df = df[(df["Standort"] == selected_standort) & (df["Kategorie"] == selected_kategorie)]

# 📈 Візуалізація
if not filtered_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig_stock = px.bar(filtered_df, x="Produktname", y="Bestand", color="Kategorie",
                           title="📊 Lagerbestand nach Produkt", text_auto=True)
        st.plotly_chart(fig_stock, use_container_width=True)

    with col2:
        fig_price = px.bar(filtered_df, x="Produktname", y="Preis", color="Kategorie",
                           title="💰 Preisvergleich", text_auto=True)
        st.plotly_chart(fig_price, use_container_width=True)
else:
    st.warning("⚠️ Keine Daten für die gewählten Filter gefunden.")

# 🧾 Таблиця з даними
st.subheader("📋 Produktliste")
st.dataframe(filtered_df)

st.markdown("---")
st.caption("© 2025 Barcode & Lagerverwaltungssystem – erstellt von Vitalii Shevchuk (Münster, Deutschland)")
