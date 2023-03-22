import os
import warnings
from datetime import timedelta

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Chef's Restaurant Sales Analytics", page_icon="\U0001F373", layout="centered"
)

st.title("\U0001F373" + " Chef Restaurant Sales Analytics")

with st.sidebar:
    st.header("Data Input")
    excel_file = st.file_uploader("Excel file for analysis - Artikkelsummering.xlsx", type="xlsx")
    sheet_name = st.text_input("Name of the sheet?", value="sheet1")

    if excel_file and sheet_name:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            data_raw = pd.read_excel(excel_file, sheet_name=sheet_name, engine="openpyxl")
    else:
        st.stop()

    data_period_start = data_raw["Dato"].min().strftime("%Y-%m-%d")
    data_period_end = data_raw["Dato"].max().strftime("%Y-%m-%d")
    data_days_provided = (data_raw["Dato"].max() - data_raw["Dato"].min()).days + 1

    tile = f'<p style="font-family:sans-serif; color:Red; font-size: 22px;">Period: {data_period_start} - {data_period_end}  ({data_days_provided} days)</p>'
    st.markdown(tile, unsafe_allow_html=True)

st.header("Analytics")
gruppe = st.radio("Gruppe", ("Alkohol", "Butikk", "Restaurant"), index=2, horizontal=True)
undergruppe_selection = list(data_raw[data_raw["Gruppe"] == gruppe]["Undergruppe"].unique())
undergruppe_default_index = undergruppe_selection.index("Mat print") if "Mat print" in undergruppe_selection else 0
undergruppe = st.selectbox("Undergruppe", undergruppe_selection, index=undergruppe_default_index)

data_analysis = data_raw.loc[(data_raw["Gruppe"] == gruppe) & (data_raw["Undergruppe"] == undergruppe), :]

chart_tab, data_tab = st.tabs(["📈 Chart", "\U0001F522 Data"])
with chart_tab:
    aggregation = st.radio("Aggregation", ("Daily", "Weekly", "Monthly"), index=0, horizontal=True, key="radio_0")
    metric = st.selectbox("Metric to aggregate", ("Antall", "Brutto", "Netto", "Profitt"), key="metric_0")

    items = st.multiselect("Select Items", options=list(data_analysis["Artikkel"].unique()))

    if st.button("\U0001FA84", key="do_magic_button_0"):
        
        data_analysis_selected = data_analysis.loc[data_analysis["Artikkel"].isin(items), :]
        if aggregation == "Daily":
            data_analysis_selected.loc[:, "Aggregation"] = data_analysis_selected.loc[:, "Dato"]
        elif aggregation == "Weekly":
            data_analysis_selected.loc[:, "Aggregation"] = data_analysis_selected["Dato"] - data_analysis_selected["Dato"].dt.weekday * np.timedelta64(1, 'D')
        else:
            data_analysis_selected.loc[:, "Aggregation"] = data_analysis_selected["Dato"] - data_analysis_selected["Dato"].dt.weekday * np.timedelta64(1, 'M')

        stats = data_analysis_selected[["Artikkel", "Aggregation", metric]].groupby(["Artikkel", "Aggregation"]).sum().reset_index()

        fig = px.line(stats, x="Aggregation", y=metric, color="Artikkel")
        st.plotly_chart(fig)

        with st.expander("Data inside"):
            stats_pivoted = stats.pivot(index="Artikkel", columns="Aggregation", values=metric)
            st.dataframe(stats_pivoted)

with data_tab:
    aggregation = st.radio("Aggregation", ("Daily", "Weekly", "Monthly"), index=0, horizontal=True, key="radio_1")
    metric = st.selectbox("Metric to aggregate", ("Antall", "Brutto", "Netto", "Profitt"), key="metric_1")
    
    if st.button("\U0001FA84", key="do_magic_button_1"):
        if aggregation == "Daily":
            data_analysis.loc[:, "Aggregation"] = data_analysis["Dato"].dt.strftime("Day: %Y-%m-%d")
        elif aggregation == "Weekly":
            data_analysis.loc[:, "Aggregation"] = data_analysis["Dato"].dt.strftime("Week: %Y-%W")
        else:
            data_analysis.loc[:, "Aggregation"] = data_analysis["Dato"].dt.strftime("Month: %Y-%m")

        stats = data_analysis[["Artikkel", "Aggregation", metric]].groupby(["Artikkel", "Aggregation"]).sum().groupby(
                "Artikkel"
            ).agg(["min", "max", "median", "mean"]).reset_index()
        stats.columns = ["Artikkel", f"{metric} Min", f"{metric} Max", f"{metric} Median", f"{metric} Mean"]
        
        day_from = data_analysis["Dato"].max() - timedelta(days=7)
        last_7_days_totals = data_analysis[data_analysis["Dato"] >= day_from].groupby(
            "Artikkel"
        ).agg({metric: "sum"}).reset_index()
        last_7_days_totals.columns = ["Artikkel", f"{metric}: Last 7 Days Total"]
        
        with_last_7_days = stats.merge(last_7_days_totals, on="Artikkel", how="outer")
        with_last_7_days.sort_values(by=f"{metric}: Last 7 Days Total", ascending=False, inplace=True)

        st.header(f"Statistics - {aggregation} - {metric}")
        st.table(with_last_7_days)

    
