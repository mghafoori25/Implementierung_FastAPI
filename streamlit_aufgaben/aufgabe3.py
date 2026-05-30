import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Mini-Dashboard",
    page_icon="💻",
    layout="wide"
)

st.title("Mini-Dashboard: Technik-Verkäufe")

@st.cache_data
def lade_daten():
    return pd.read_csv("technik_verkaeufe.csv")

df = lade_daten()

st.subheader("Filter")

kategorie = st.selectbox(
    "Kategorie auswählen:",
    options=["Alle"] + sorted(df["Kategorie"].unique().tolist())
)

if kategorie == "Alle":
    gefilterte_daten = df
else:
    gefilterte_daten = df[df["Kategorie"] == kategorie]

gesamtumsatz = gefilterte_daten["Umsatz"].sum()
durchschnitt = gefilterte_daten["Umsatz"].mean()
maximum = gefilterte_daten["Umsatz"].max()

spalte1, spalte2, spalte3 = st.columns(3)

with spalte1:
    st.metric("Gesamtumsatz", f"{gesamtumsatz:.2f} €")

with spalte2:
    st.metric("Durchschnitt", f"{durchschnitt:.2f} €")

with spalte3:
    st.metric("Höchster Monatswert", f"{maximum:.2f} €")

st.subheader("Gefilterte Daten")
st.dataframe(gefilterte_daten, use_container_width=True)

st.subheader("Umsatzdiagramm")
st.bar_chart(
    gefilterte_daten,
    x="Monat",
    y="Umsatz"
)