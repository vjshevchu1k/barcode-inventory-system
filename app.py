# app.py — Barcode & Inventory System (robust version)
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Page config ---
st.set_page_config(page_title="📦 Barcode & Lagerverwaltungssystem", layout="wide")

# --- Helper: find csv file ---
def find_csv_file():
    candidates = ["data.csv", "inventory.csv", "inventory.csv".lower()]
    for name in candidates:
        p = Path(name)
        if p.exists():
            return p
    return None

CSV_PATH = find_csv_file() or Path("data.csv")  # fallback to data.csv

# --- Safe CSV loader with normalization of column names ---
@st.cache_data
def load_data(path: Path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        # empty template dataframe
        df = pd.DataFrame(
            columns=[
                "Produktname", "Kategorie", "Bestand", "Preis", "Barcode", "Standort"
            ]
        )
        return df

    # normalize column names: strip, lower -> map to canonical German names
    col_map = {}
    for col in df.columns:
        c = col.strip().lower()
        if c in ("produktname", "product", "name", "produkt"):
            col_map[col] = "Produktname"
        elif c in ("kategorie", "category", "cat"):
            col_map[col] = "Kategorie"
        elif c in ("bestand", "stock", "quantity", "menge"):
            col_map[col] = "Bestand"
        elif c in ("preis", "price"):
            col_map[col] = "Preis"
        elif c in ("barcode", "ean", "code"):
            col_map[col] = "Barcode"
        elif c in ("standort", "location", "filiale", "store"):
            col_map[col] = "Standort"
        else:
            # try capitalize
            col_map[col] = col.strip().capitalize()

    df = df.rename(columns=col_map)

    # ensure essential columns exist (if missing, create with defaults)
    if "Produktname" not in df.columns:
        df["Produktname"] = ""
    if "Kategorie" not in df.columns:
        df["Kategorie"] = "Allgemein"
    if "Bestand" not in df.columns:
        df["Bestand"] = 0
    if "Preis" not in df.columns:
        df["Preis"] = 0.0
    if "Barcode" not in df.columns:
        df["Barcode"] = ""
    if "Standort" not in df.columns:
        # Standort optional; keep as string
        df["Standort"] = "Hauptlager"

    # coerce types safely
    try:
        df["Bestand"] = pd.to_numeric(df["Bestand"], errors="coerce").fillna(0).astype(int)
    except Exception:
        df["Bestand"] = 0
    try:
        df["Preis"] = pd.to_numeric(df["Preis"], errors="coerce").fillna(0.0)
    except Exception:
        df["Preis"] = 0.0

    # fill NaNs in strings
    df["Produktname"] = df["Produktname"].fillna("").astype(str)
    df["Kategorie"] = df["Kategorie"].fillna("Allgemein").astype(str)
    df["Barcode"] = df["Barcode"].fillna("").astype(str)
    df["Standort"] = df["Standort"].fillna("Hauptlager").astype(str)

    return df

# --- Load data ---
df = load_data(CSV_PATH)

# --- Header / logo (use stable Wikimedia image) ---
# Using a stable barcode sample image from Wikimedia Commons
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Barcode_sample.svg/640px-Barcode_sample.svg.png",
    width=180
)
st.title("📦 Barcode & Lagerverwaltungssystem")
st.markdown("Ein robustes System zur Verwaltung von Produkten, Beständen, Preisen und Barcodes.")
st.markdown("---")

# --- Sidebar filters ---
st.sidebar.header("🔎 Filteroptionen")

# Category filter
unique_categories = sorted(df["Kategorie"].unique())
selected_categories = st.sidebar.multiselect(
    "Kategorie auswählen:", unique_categories, default=unique_categories
)

# Standort filter (optional)
has_standort = "Standort" in df.columns and df["Standort"].nunique() > 0
if has_standort:
    unique_locations = sorted(df["Standort"].unique())
    selected_locations = st.sidebar.multiselect(
        "Standort auswählen:", unique_locations, default=unique_locations
    )
else:
    selected_locations = None

# Price slider
min_price = float(df["Preis"].min()) if not df["Preis"].isnull().all() else 0.0
max_price = float(df["Preis"].max()) if not df["Preis"].isnull().all() else 0.0
if min_price == max_price:
    # avoid slider error if all equal
    price_range = (min_price, max_price + 1.0)
else:
    price_range = st.sidebar.slider("Preisbereich (€):", min_value=float(min_price), max_value=float(max_price), value=(float(min_price), float(max_price)))

# --- Apply filters ---
filtered = df[df["Kategorie"].isin(selected_categories)]
filtered = filtered[(filtered["Preis"] >= price_range[0]) & (filtered["Preis"] <= price_range[1])]
if selected_locations is not None:
    filtered = filtered[filtered["Standort"].isin(selected_locations)]

# --- Barcode search ---
st.subheader("🔍 Barcode-Suche")
barcode_input = st.text_input("Barcode eingeben (oder scannen):", value="")

if barcode_input:
    res = df[df["Barcode"].astype(str) == str(barcode_input)]
    if not res.empty:
        st.success("✅ Produkt gefunden:")
        st.table(res.reset_index(drop=True))
    else:
        st.error("❌ Produkt mit diesem Barcode nicht gefunden.")

st.markdown("---")

# --- Display inventory and visualizations ---
st.subheader("📋 Produktliste")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

# Charts only if we have data
if not filtered.empty:
    # Stock per product
    try:
        fig_stock = px.bar(
            filtered.sort_values("Bestand", ascending=False),
            x="Produktname",
            y="Bestand",
            color="Kategorie",
            title="📦 Lagerbestand nach Produkt",
            text_auto=True
        )
        st.plotly_chart(fig_stock, use_container_width=True)
    except Exception as e:
        st.warning("Diagramm Lagerbestand konnte nicht gezeichnet werden.")

    # Average price per category
    try:
        avg_price = filtered.groupby("Kategorie", as_index=False)["Preis"].mean()
        fig_price = px.bar(
            avg_price,
            x="Kategorie",
            y="Preis",
            title="💰 Durchschnittspreis pro Kategorie",
            text_auto=".2f"
        )
        st.plotly_chart(fig_price, use_container_width=True)
    except Exception:
        st.warning("Diagramm Durchschnittspreise konnte nicht gezeichnet werden.")
else:
    st.info("Keine Einträge für die gewählten Filter. Versuche andere Filtereinstellungen.")

st.markdown("---")

# --- Form: add new product ---
st.subheader("➕ Neues Produkt hinzufügen")
with st.form("add_product_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Produktname")
        new_category = st.text_input("Kategorie", value="Allgemein")
    with col2:
        new_stock = st.number_input("Bestand", min_value=0, step=1, value=1)
        new_price = st.number_input("Preis (€)", min_value=0.0, step=0.1, value=0.0)
    new_barcode = st.text_input("Barcode (optional)")
    new_location = st.text_input("Standort (optional)", value="Hauptlager")
    submitted = st.form_submit_button("Produkt hinzufügen")

    if submitted:
        new_row = {
            "Produktname": str(new_name),
            "Kategorie": str(new_category) if new_category else "Allgemein",
            "Bestand": int(new_stock),
            "Preis": float(new_price),
            "Barcode": str(new_barcode),
            "Standort": str(new_location) if new_location else "Hauptlager"
        }
        # append to dataframe and save
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        try:
            # write to CSV_PATH (this updates file in the app environment)
            df.to_csv(CSV_PATH, index=False)
            st.success(f"✅ Produkt '{new_name}' wurde hinzugefügt und gespeichert.")
            # clear cache and reload
            load_data.clear()
            df = load_data(CSV_PATH)
        except Exception as e:
            st.error("❌ Speichern fehlgeschlagen. In der Cloud-Umgebung wird die Datei lokal im App-Container gespeichert, nicht in GitHub.")
            st.exception(e)

st.markdown("---")
st.caption("© 2025 Barcode & Lagerverwaltungssystem – Erstellt von Vitalii Shevchuk (Münster, Deutschland)")
