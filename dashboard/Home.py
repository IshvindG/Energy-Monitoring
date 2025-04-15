"""Homepage for Streamlit dashboard"""
import streamlit as st
import altair as alt
import pandas as pd
from utils.database import get_connection_to_db
from psycopg2.extras import RealDictCursor
import plotly.express as px
import plotly.graph_objects as go


def retrieve_generation_mix_data(db_cursor) -> pd.DataFrame:
    """Retrieve Generation Data from DB"""
    db_cursor.execute(
        """
        WITH Latest_gen_data AS (
            SELECT gd.fuel_type_id, gd.mw_generated, gd.updated_at
            FROM generations gd
            INNER JOIN(
                SELECT fuel_type_id, MAX(updated_at) AS latest_time
                FROM generations
                GROUP BY fuel_type_id
            ) latest ON gd.fuel_type_id = latest.fuel_type_id AND gd.updated_at = latest.latest_time

        )
        SELECT * FROM Latest_gen_data JOIN fuel_types USING(fuel_type_id) JOIN fuel_categories USING(fuel_category_id);
        """)

    generation_data = db_cursor.fetchall()
    return generation_data


def retrieve_price_data(db_cursor):
    """Retrieve Pricing Data from DB"""
    db_cursor.execute(
        "SELECT * FROM prices WHERE updated_at >= NOW() - '1 day'::INTERVAL")
    return db_cursor.fetchall()


def retrieve_demand_data(db_cursor):
    """Retrieve Demand Data from DB"""
    db_cursor.execute(
        "SELECT total_demand, demand_at FROM demands WHERE updated_at >= NOW() - '1 day'::INTERVAL")
    demand = db_cursor.fetchall()
    return demand


def format_generation_data(generation_data: list[dict]):
    """Format generation data to remove unneeded bits"""
    generation_mix = pd.DataFrame(generation_data)
    generation_mix['updated_at'] = pd.to_datetime(
        generation_mix['updated_at'], utc=True)

    generation_mix['Energy_Gen'] = generation_mix["mw_generated"] / 1000
    generation_mix['Energy_Gen'] = generation_mix['Energy_Gen'].map(
        "{:,.2f}GW".format)
    return generation_mix


def generate_demand_graph(demand_df):
    """Generate demand"""
    demand_chart = alt.Chart(demand_df).mark_area().encode(
        x=alt.X('demand_at:T', title="Time"),
        y=alt.Y('Energy Demand:Q', title="Demand (GW)"),
        tooltip=[alt.Tooltip('Energy Demand:Q', title='GW'),
                 alt.Tooltip('demand_at:T', title="Time", format='%H:%M')],
        text='Energy Demand',

    )
    return demand_chart


def generate_price_graph(price_df):
    """Generate price"""

    hover = alt.selection_point(
        fields=["price_at"],
        nearest=True,
        on="mouseover",
        clear="mouseout",
        empty=False
    )

    # Base line chart
    line = alt.Chart(price_df).mark_line().encode(
        x=alt.X('price_at:T', title='Time'),
        y=alt.Y('price_per_mwh:Q', title='Price (£/MW)')
    )

    # Transparent points to enable hover detection
    selectors = alt.Chart(price_df).mark_point().encode(
        y=alt.Y('price_per_mwh:Q', title="£/MW"),
        x=alt.X('price_at:T'),
        opacity=alt.value(0)
    ).add_params(
        hover
    )

    # Dot (circle) on hover
    points = alt.Chart(price_df).mark_circle(size=65, color='steelblue').encode(
        x=alt.X('price_at:T'),
        y='price_per_mwh:Q'
    ).transform_filter(hover)

    # Combine all
    chart = alt.layer(
        line, selectors, points
    ).properties(
        width=700,
        height=400,
        title="Market Price Over Time (£/MW)"
    )
    return chart


def generate_energy_generation_mix_graph(generation_mix: pd.DataFrame):
    """Generate price"""
    generation_mix = generation_mix.loc[generation_mix['fuel_category']
                                        != 'Interconnectors']
    # Create sunburst chart using Plotly
    fig = px.sunburst(
        generation_mix,
        # This defines the hierarchy
        path=['fuel_category', 'fuel_type_name'],
        values='mw_generated',
        title="Energy Generation"
    )

    # Show it in Streamlit
    return fig


def show_generation_stats(generation_mix: pd.DataFrame):
    """Formatting (can be removed)"""
    generation_mix.drop(
        columns=['fuel_category_id', 'fuel_type_id',
                 'fuel_type', 'mw_generated', 'updated_at'], inplace=True)


def generate_24h_energy_generation_graph(db_cursor):
    """Generate 24h generation mix"""
    db_cursor.execute(
        """
        SELECT * FROM generations 
        JOIN fuel_types USING(fuel_type_id) 
        WHERE generation_at >= NOW() - '24 hours'::INTERVAL 
        AND fuel_type NOT LIKE 'INT%' 
        AND mw_generated > 0
        """)
    energy_mix = db_cursor.fetchall()
    energy_mix_df = pd.DataFrame(energy_mix)
    energy_mix_df.to_csv('thingy.csv', index=False)
    energy_mix_df['updated_at'] = pd.to_datetime(
        energy_mix_df['updated_at'], utc=True)
    energy_mix_df['updated_at'] = energy_mix_df['updated_at'].dt.round('min')

    fig = alt.Chart(energy_mix_df).mark_area().encode(
        x=alt.X('updated_at', title="Time"),
        y=alt.Y('mw_generated', title="MW Generated"),
        color=alt.Color('fuel_type_name', legend=alt.Legend(
            orient='bottom', direction='horizontal', title='Fuel Types  ')),
        tooltip=[alt.Tooltip('mw_generated', title="Power Generated"), alt.Tooltip(
            'fuel_type_name', title="Fuel Type"),
            alt.Tooltip('updated_at', title="Time", timeUnit='hoursminutes')]

    ).properties(
        height=500
    )
    return fig


def format_demand_data(demand_data):
    demand_df = pd.DataFrame(demand_data)
    demand_df.drop_duplicates(inplace=True)
    demand_df['demand_at'] = pd.to_datetime(
        demand_df['demand_at'], utc=True)
    demand_df['Energy Demand'] = demand_df["total_demand"] / 1000
    demand_df['Energy Demand'] = demand_df['Energy Demand'].map(
        "{:,.2f}".format)
    return demand_df


def format_price_data(price_data):
    price_df = pd.DataFrame(price_data)
    price_df.drop(columns=['price_id'], inplace=True)
    price_df['price_at'] = pd.to_datetime(
        price_df['price_at'], utc=True)

    price_df['price_per_mwh'] = pd.to_numeric(
        price_df['price_per_mwh'])
    price_df['Price per MWH'] = price_df['price_per_mwh'].map(
        "£{:,.2f}".format)
    return price_df


def latest_demand_metric(demand_df):
    """Get latest demand metric"""
    return f"{demand_df.iloc[-1]['Energy Demand']}GW"


def latest_price_metric(price_df):
    """Get latest pricing metric"""
    return f"{price_df.iloc[-1]['Price per MWH']}"


def latest_generation_metric(generation_df):
    """Get latest generation metric"""
    df = generation_df.copy()
    df = df.loc[df['fuel_category']
                != 'Interconnectors']
    df = df["mw_generated"]
    generation = df.sum()
    generation = generation/1000

    return "{:,.2f}GW".format(generation)


def latest_imports_metric(generation_df):
    """Get latest imports metric"""
    df = generation_df.copy()
    df = df.loc[df['fuel_category']
                == 'Interconnectors']
    df = df.loc[df['mw_generated']
                > 0]

    df = df["mw_generated"]
    imports = df.sum()
    imports = imports/1000

    return "{:,.2f}GW".format(imports)


def add_table(data, filter_type):
    st.title(filter_type)
    data_copy = data.copy()
    data_copy = data_copy.loc[data_copy['fuel_category']
                              == filter_type]
    data_copy.drop(columns=['fuel_category'], inplace=True)
    # data_copy.sort_values('mw_generated')
    st.table(data_copy)


def main():
    """Main method for running dashboard"""
    db_conn = get_connection_to_db()
    db_cursor = db_conn.cursor(cursor_factory=RealDictCursor)

    generation_data = retrieve_generation_mix_data(db_cursor)
    demand_data = retrieve_demand_data(db_cursor)
    price_data = retrieve_price_data(db_cursor)

    generation_mix_data = format_generation_data(generation_data)
    demand_data = format_demand_data(demand_data)
    price_data = format_price_data(price_data)

    st.set_page_config(layout="wide")
    st.title("Energize Dashboard")
    st.write("Welcome! Use the sidebar to navigate between dashboards.")

    col1, col2, col3 = st.columns(3)
    col1.write(generate_energy_generation_mix_graph(generation_mix_data))
    col3.metric(label="UK Power Demand",
                value=latest_demand_metric(demand_data))
    col3.metric(label="UK Power Generation",
                value=latest_generation_metric(generation_mix_data))
    col3.metric(label="Price per MW",
                value=latest_price_metric(price_data))
    col3.metric(label="Power Imports",
                value=latest_imports_metric(generation_mix_data))

    positive_mix_data = generation_mix_data.copy()
    positive_mix_data = positive_mix_data.loc[positive_mix_data['mw_generated'] > 0]

    col2.write(alt.Chart(positive_mix_data).mark_bar().encode(
        x=alt.X('fuel_category', axis=alt.Axis(labels=False)),
        y=alt.Y('mw_generated'),
        color=alt.Color('fuel_type_name', legend=alt.Legend(
        ))
    ).properties(
        height=600

    )
    )

    st.write(generate_demand_graph(demand_data))
    st.write(generate_price_graph(price_data))

    st.write(generate_24h_energy_generation_graph(db_cursor))

    show_generation_stats(generation_mix_data)

    for fuel_category in ['Fossil Fuels', 'Renewables', 'Interconnectors', 'Other']:

        add_table(generation_mix_data, fuel_category)


if __name__ == '__main__':
    main()
