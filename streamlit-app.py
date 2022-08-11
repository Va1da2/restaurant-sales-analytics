import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Chef Restaurant Sales Analytics", page_icon="\U0001F373", layout="centered"
)

st.title("\U0001F373" + " Chef Restaurant Sales Analytics")


excel_file = st.file_uploader("Excel file for analysis - Artikkelsummering.xlsx", type="xlsx")
sheet_name = st.text_input("Name of the sheet?", value="sheet1")

if excel_file and sheet_name:
    data = pd.read_excel(excel_file, sheet_name=sheet_name)

    col1, col2 = st.columns(2)
    with col1:
        gruppe = st.radio("Gruppe", ("Alkohol", "Butikk", "Restaurant"), index=2, horizontal=True)
        undergruppe_selection = list(data[data["Gruppe"] == gruppe]["Undergruppe"].unique())
        undergruppe = st.selectbox("Undergruppe", undergruppe_selection)

        data = data[data["Gruppe"] == gruppe]
        data = data[data["Undergruppe"] == undergruppe]
    
    with col2:
        aggregation = st.radio("Aggregation", ("Weekly", "Monthly"), index=0, horizontal=True)
        metric = st.selectbox("Metric to aggregate", ("Antall", "Brutto", "Netto", "Profitt"))

        if aggregation == "Weekly":
            data[f"Aggregation"] = data["Dato"].dt.strftime("Week: %Y-%W")
        else:
            data[f"Aggregation"] = data["Dato"].dt.strftime("Month: %Y-%m")

        stats = data[
            ["Gruppe", "Undergruppe", "Aggregation", "Artikkel", metric]
            ].groupby(
                ["Gruppe", "Undergruppe", "Artikkel", "Aggregation"]
            ).sum().groupby(
                ["Gruppe", "Undergruppe", "Artikkel"]
            ).agg(["min", "max", "median", "mean"])

    st.dataframe(stats)
