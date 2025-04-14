import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px
import folium
from branca.colormap import linear
from streamlit_folium import st_folium
import requests


load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def get_recent_data():
    conn = get_db_connection()
    now = datetime.utcnow()
    past_24h = now - timedelta(hours=24)

    carbon_query = """
        SELECT measure_at, forecast_measure 
        FROM carbon_intensities 
        WHERE measure_at >= %s
        ORDER BY measure_at ASC;
    """

    demand_query = """
        SELECT demand_at, total_demand 
        FROM demands 
        WHERE demand_at >= %s
        ORDER BY demand_at ASC;
    """

    df_carbon = pd.read_sql(carbon_query, conn, params=(past_24h,))
    df_demand = pd.read_sql(demand_query, conn, params=(past_24h,))

    conn.close()
    return df_carbon, df_demand


def plot_recent_carbon_and_demand(df_carbon, df_demand):
    fig, ax1 = plt.subplots(figsize=(18, 8))

    sns.lineplot(
        data=df_carbon, x='measure_at', y='forecast_measure', ax=ax1, color='green', label='CO₂ Intensity (gCO₂/kWh)'
    )
    ax1.set_ylabel('CO₂ Intensity (gCO₂/kWh)', color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    ax2 = ax1.twinx()
    sns.lineplot(
        data=df_demand, x='demand_at', y='total_demand', ax=ax2, color='blue', label='Electricity Demand (MW)'
    )
    ax2.set_ylabel('Electricity Demand (MW)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    ax1.set_title("CO₂ Intensity & Electricity Demand Over the Last 24 Hours")
    ax1.set_xlabel("Timestamp")
    fig.autofmt_xdate()

    st.pyplot(fig)


def show_emissions_doughnut_by_region():
    time_period = st.selectbox(
        "Select the time period for CO₂ emissions data:",
        ["Last 24 hours", "Last 72 hours", "Last week"]
    )

    now = datetime.utcnow()

    if time_period == "Last 24 hours":
        time_delta = timedelta(hours=24)
    elif time_period == "Last 72 hours":
        time_delta = timedelta(hours=72)
    else:
        time_delta = timedelta(weeks=1)

    past_time = now - time_delta

    conn = get_db_connection()

    query = """
        SELECT r.region_name, ci.region_id, SUM(ci.forecast_measure) AS total_emissions
        FROM carbon_intensities ci
        JOIN regions r ON ci.region_id = r.region_id
        WHERE ci.measure_at >= %s
        GROUP BY ci.region_id, r.region_name
        ORDER BY total_emissions DESC;
    """

    df = pd.read_sql(query, conn, params=(past_time,))
    conn.close()

    if df.empty:
        st.warning(
            f"No CO₂ data available for the selected time period: {time_period}.")
        return

    total_emissions = df['total_emissions'].sum()

    fig = go.Figure(data=[go.Pie(
        labels=df['region_name'],
        values=df['total_emissions'],
        hole=0.5,
        hoverinfo='label+percent',
        textinfo='value',
        marker=dict(line=dict(color='#000000', width=1))
    )])

    fig.update_layout(
        title_text=f"CO₂ Emissions by Region ({time_period})",
        annotations=[dict(
            text=f"{int(total_emissions)}<br>gCO₂/kWh",
            x=0.5,
            y=0.5,
            font_size=18,
            showarrow=False
        )],
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)


def show_outages_by_provider():
    conn = get_db_connection()

    region_provider_query = """
        SELECT r.region_id, r.region_name, r.provider_id, p.provider_name
        FROM regions r
        JOIN providers p ON r.provider_id = p.provider_id
        ORDER BY r.region_id;
    """
    region_df = pd.read_sql(region_provider_query, conn)

    st.subheader("🗺️ Region to Provider Mapping")
    st.dataframe(region_df[['region_name', 'provider_name']],
                 use_container_width=True)

    providers = region_df[['provider_id', 'provider_name']].drop_duplicates()
    selected_provider_name = st.selectbox(
        "Select your provider to view outages in your area:", providers['provider_name'])

    selected_provider_id = providers.loc[providers['provider_name']
                                         == selected_provider_name, 'provider_id'].values[0]

    now = datetime.utcnow()
    past_48h = now - timedelta(hours=48)

    outage_query = """
        SELECT outage_start, outage_end, planned
        FROM outages
        WHERE provider_id = %s
        AND outage_start >= %s
        ORDER BY outage_start;
    """

    outage_df = pd.read_sql(outage_query, conn, params=(
        int(selected_provider_id), past_48h))
    conn.close()

    if outage_df.empty:
        st.info(
            f"No outages recorded for **{selected_provider_name}** in the last 48 hours.")
        return

    outage_df = outage_df.fillna("NaN")

    fig = px.timeline(
        outage_df,
        x_start="outage_start",
        x_end="outage_end",
        y=outage_df.index,
        title=f"⚡ Outages for {selected_provider_name} (Last 48 Hours)",
    )

    fig.update_yaxes(title="Outage Record")
    fig.update_traces(
        hovertemplate="Outage Start: %{x}<br>" +
        "Outage End: %{x_end}<br>" +
        "Planned: %{customdata[0]}",
        customdata=outage_df[['planned']].values
    )

    st.plotly_chart(fig, use_container_width=True)


def fetch_data(conn, option):
    if option == "Outages":
        query = """
        SELECT r.region_name, COUNT(*) as value
        FROM outages o
        JOIN providers p ON o.provider_id = p.provider_id
        JOIN regions r ON r.provider_id = p.provider_id
        WHERE outage_start >= NOW() - INTERVAL '7 DAYS'
        GROUP BY r.region_name;
        """
        label = "Outages (Last 7 Days)"
    else:
        query = """
        SELECT r.region_name, AVG(c.forecast_measure) as value
        FROM carbon_intensities c
        JOIN regions r ON r.region_id = c.region_id
        WHERE measure_at >= NOW() - INTERVAL '7 DAYS'
        GROUP BY r.region_name;
        """
        label = "Avg CO₂ Emissions (Last 7 Days)"

    df = pd.read_sql(query, conn)
    return df, label


def load_geojson():
    geo_url = "https://sdgdata.gov.uk/sdg-data/en/geojson/regions/indicator_8-10-1.geojson"
    return requests.get(geo_url).json()


def build_map(df, label, geojson, geo_to_db_region_map):
    min_val = df["value"].min()
    max_val = df["value"].max()
    colormap = linear.OrRd_09.scale(min_val, max_val)
    colormap.caption = label

    value_dict = dict(zip(df["region_name"], df["value"]))

    m = folium.Map(
        location=[54, -2],
        zoom_start=6,
        min_zoom=5,
        max_zoom=10,
        max_bounds=True,
    )
    m.fit_bounds([[49.5, -11], [61, 2]])

    def style_function(feature):
        geo_region = feature["properties"]["name"]
        db_region = geo_to_db_region_map.get(geo_region)
        value = value_dict.get(db_region)
        return {
            'fillColor': colormap(value) if value is not None else "#ccc",
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    folium.GeoJson(
        geojson,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Region:"])
    ).add_to(m)

    colormap.add_to(m)
    return m


def main():
    st.title("Energy Trends: CO₂ Emissions vs Electricity Demand")

    df_carbon, df_demand = get_recent_data()

    if df_carbon.empty or df_demand.empty:
        st.warning("No data available for the last 48 hours.")
    else:
        plot_recent_carbon_and_demand(df_carbon, df_demand)

    show_emissions_doughnut_by_region()
    show_outages_by_provider()

    geo_to_db_region_map = {
        "North East": "North East England",
        "North West": "North West England",
        "Yorkshire and The Humber": "Yorkshire",
        "East Midlands": "East Midlands",
        "West Midlands": "West Midlands",
        "East": "East England",
        "London": "London",
        "South East": "South East England",
        "South West": "South West England",
    }

    option = st.selectbox("Choose metric to display:",
                          ["Outages", "CO₂ emissions"])

    conn = get_db_connection()

    df, label = fetch_data(conn, option)
    conn.close()

    geojson = load_geojson()
    m = build_map(df, label, geojson, geo_to_db_region_map)
    st_folium(m, width=700, height=500)


if __name__ == "__main__":
    main()
