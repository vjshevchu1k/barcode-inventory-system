import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="📦 Barcode & Lagerverwaltungssystem", layout="wide")

# 🏪 Стабільне PNG-лого (вічне посилання на Wikimedia)
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Edeka_Logo.svg/512px-Edeka_Logo.svg.png", width=120)

st.title("📦 Barcode & Lagerverwaltungssystem")
st.markdown("Ein interaktives System zur Verwaltung von Produkten, Beständen und Standorten im Einzelhandel.")
st.markdown("---")

# 🧩 Завантаження даних
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        df.columns = [col.strip().capitalize() for col in df.columns]
    except Exception:
        # Якщо CSV відсутній або з помилкою — створюємо тестові дані
        df = pd.DataFrame({
            "Produktname": ["Apfel", "Bananen", "Milch", "Käse", "Brot"],
            "Preis": [0.99, 1.29, 1.49, 2.99, 1.89],
            "Bestand": [120, 85, 60, 40, 75],
            "Standort": ["Filiale A", "Filiale A", "Filiale B", "Filiale B", "Filiale C"],
            "Kategorie": ["Obst", "Obst", "Milchprodukte", "Milchprodukte", "Backwaren"]
        })
    return df

df = load_data()

# 📊 Фільтри

kategorien = sorted(df["Kategorie"].unique())

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
        fig_stock = px.bar(
            filtered_df,
            x="Produktname",
            y="Bestand",
            color="Kategorie",
            title="📊 Lagerbestand nach Produkt",
            text_auto=True
        )
        st.plotly_chart(fig_stock, use_container_width=True)

    with col2:
        fig_price = px.bar(
            filtered_df,
            x="Produktname",
            y="Preis",
            color="Kategorie",
            title="💰 Preisvergleich",
            text_auto=True
        )
        st.plotly_chart(fig_price, use_container_width=True)
else:
    st.warning("⚠️ Keine Daten für die gewählten Filter gefunden.")

# 🧾 Таблиця з даними
st.subheader("📋 Produktliste")
st.dataframe(filtered_df)

st.markdown("---")
st.caption("© 2025 Barcode & Lagerverwaltungssystem – erstellt von Vitalii Shevchuk (Münster, Deutschland)")

