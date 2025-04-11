import streamlit as st
import pandas as pd
import altair as alt
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

db_params = {
    'host': DB_HOST,
    'port': DB_PORT,
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD
}


def get_data_from_db(query):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    conn.close()
    return df


regions_query = "SELECT region_id, region_name, provider_id FROM regions"
carbon_intensities_query = "SELECT carbon_intensity_id, region_id, forecast_measure, measure_at FROM carbon_intensities"
outages_query = "SELECT outage_id, outage_start, outage_end, provider_id, planned FROM outages"

regions_df = get_data_from_db(regions_query)
carbon_df = get_data_from_db(carbon_intensities_query)
outages_df = get_data_from_db(outages_query)

carbon_df = carbon_df.merge(
    regions_df[['region_id', 'region_name']], on='region_id', how='left')
outages_df = outages_df.merge(
    regions_df[['provider_id', 'region_name']], on='provider_id', how='left')

st.title("Energy Monitoring Dashboard")

st.subheader("Regional Carbon Intensity Trends")
line_chart = alt.Chart(carbon_df).mark_line().encode(
    x='measure_at:T',
    y='forecast_measure:Q',
    color='region_name:N',
    tooltip=['region_name', 'measure_at:T', 'forecast_measure:Q']
).properties(width=600, height=300)
st.altair_chart(line_chart)

st.subheader("Live Carbon Intensity Index by Region")
latest_time = carbon_df['measure_at'].max()
latest_df = carbon_df[carbon_df['measure_at'] == latest_time]
heatmap = alt.Chart(latest_df).mark_rect().encode(
    x='region_name:N',
    y=alt.value(1),
    color='forecast_measure:Q',
    tooltip=['region_name', 'forecast_measure']
).properties(width=600, height=100)
st.altair_chart(heatmap)

st.subheader("Outage Count by Region")
outage_counts = outages_df.groupby(
    'region_name').size().reset_index(name='count')
bar_chart = alt.Chart(outage_counts).mark_bar().encode(
    x='region_name:N',
    y='count:Q',
    tooltip=['region_name', 'count']
).properties(width=600, height=300)
st.altair_chart(bar_chart)
