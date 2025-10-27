import streamlit as st
import pandas as pd
import uuid

# --- Seiteneinstellungen ---
st.set_page_config(page_title="Barcode Inventory System", layout="wide")

# --- Titel ---
st.title("🏷️ Barcode Inventory System")
st.markdown("Ein einfaches Lagerverwaltungssystem mit Barcode-Funktion – erstellt von **Vitalii Shevchuk** (2025)")

# --- Daten laden oder erstellen ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("inventory.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Produktname", "Kategorie", "Menge", "Preis (€)", "Barcode"])
        df.to_csv("inventory.csv", index=False)
    return df

df = load_data()

# --- Seitenlayout ---
tab1, tab2, tab3 = st.tabs(["📦 Inventar anzeigen", "➕ Neues Produkt", "📇 Barcode suchen"])

# --- TAB 1: Inventar anzeigen ---
with tab1:
    st.subheader("📋 Aktuelles Inventar")
    st.dataframe(df, use_container_width=True)

# --- TAB 2: Neues Produkt hinzufügen ---
with tab2:
    st.subheader("➕ Neues Produkt hinzufügen")
    with st.form("add_product_form"):
        name = st.text_input("Produktname")
        category = st.text_input("Kategorie")
        quantity = st.number_input("Menge", min_value=0, step=1)
        price = st.number_input("Preis (€)", min_value=0.0, step=0.1)
        barcode = st.text_input("Barcode (optional)", value=str(uuid.uuid4())[:8])
        submitted = st.form_submit_button("✅ Hinzufügen")

        if submitted:
            new_product = {"Produktname": name, "Kategorie": category, "Menge": quantity, "Preis (€)": price, "Barcode": barcode}
            df = pd.concat([df, pd.DataFrame([new_product])], ignore_index=True)
            df.to_csv("inventory.csv", index=False)
            st.success(f"✅ Produkt **{name}** wurde hinzugefügt!")

# --- TAB 3: Barcode-Suche ---
with tab3:
    st.subheader("🔍 Produkt über Barcode finden")
    barcode_search = st.text_input("Barcode eingeben oder scannen")

    if barcode_search:
        result = df[df["Barcode"] == barcode_search]
        if not result.empty:
            st.success("✅ Produkt gefunden:")
            st.table(result)
        else:
            st.error("❌ Kein Produkt mit diesem Barcode gefunden.")

# --- Fußzeile ---
st.markdown("---")
st.markdown("© 2025 Barcode Inventory System – Erstellt von Vitalii Shevchuk")
