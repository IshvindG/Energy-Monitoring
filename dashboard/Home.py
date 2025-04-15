"""Homepage for Streamlit dashboard"""
import streamlit as st
import altair as alt
import pandas as pd
from utils.database import get_connection_to_db
from psycopg2.extras import RealDictCursor
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff


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

    generation_mix.drop_duplicates(inplace=True)
    generation_mix['Energy_Gen'] = generation_mix["mw_generated"] / 1000
    generation_mix['Energy_Gen'] = generation_mix['Energy_Gen'].map(lambda x:
                                                                    f"{x:,.2f}GW")
    return generation_mix


def generate_demand_graph(db_cursor, demand_range):
    """Generate demand"""
    duration = get_duration(demand_range)

    db_cursor.execute(
        f"SELECT total_demand, demand_at FROM demands WHERE updated_at >= NOW() - '{duration}'::INTERVAL")
    demands = db_cursor.fetchall()

    demand_df = pd.DataFrame(demands)
    demand_df = format_demand_data(demand_df)

    demand_chart = alt.Chart(demand_df).mark_area().encode(
        x=alt.X('demand_at:T', title="Time"),
        y=alt.Y('Energy Demand:Q', title="Demand (GW)"),
        tooltip=[alt.Tooltip('Energy Demand:Q', title='GW'),
                 alt.Tooltip('demand_at:T', title="Time", format='%H:%M')],
        text='Energy Demand',

    )
    return demand_chart


def generate_price_graph(db_cursor, price_range):
    """Generate price"""
    duration = get_duration(price_range)

    db_cursor.execute(
        f"SELECT * FROM prices WHERE updated_at >= NOW() - '{duration}'::INTERVAL")
    prices = db_cursor.fetchall()

    price_df = pd.DataFrame(prices)
    price_df = format_price_data(price_df)

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


def generate_24h_energy_generation_graph(db_cursor, generation_range):
    """Generate 24h generation mix"""
    duration = get_duration(generation_range)

    db_cursor.execute(
        f"""
        SELECT * FROM generations
        JOIN fuel_types USING(fuel_type_id)
        WHERE generation_at >= NOW() - '{duration}'::INTERVAL
        AND fuel_type NOT LIKE 'INT%'
        AND mw_generated > 0
        """)
    energy_mix = db_cursor.fetchall()
    energy_mix_df = pd.DataFrame(energy_mix)

    energy_mix_df = format_generation_data(energy_mix_df)
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


def get_duration(generation_range):
    duration = '24 hours'
    match(generation_range):
        case '24h':
            duration = '24 hours'
        case '1 week':
            duration = '1 week'
        case '1 month':
            duration = '1 month'
        case _:
            duration = '24 hours'
    return duration


def format_demand_data(demand_data):
    """Format demand data"""
    demand_df = pd.DataFrame(demand_data)
    demand_df.drop_duplicates(inplace=True)
    demand_df['demand_at'] = pd.to_datetime(
        demand_df['demand_at'], utc=True)
    demand_df['Energy Demand'] = demand_df["total_demand"] / 1000
    demand_df['Energy Demand'] = demand_df['Energy Demand'].map(lambda x:
                                                                f"{x:,.2f}")
    return demand_df


def format_price_data(price_data):
    """Format price"""
    price_df = pd.DataFrame(price_data)
    price_df.drop(columns=['price_id'], inplace=True)
    price_df['price_at'] = pd.to_datetime(
        price_df['price_at'], utc=True)

    price_df['price_per_mwh'] = pd.to_numeric(
        price_df['price_per_mwh'])
    price_df['Price per MWH'] = price_df['price_per_mwh'].map(lambda x:
                                                              f"£{x:,.2f}")
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

    return f"{generation:,.2f}GW"


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

    return f"{imports:,.2f}GW"


def add_table(data, filter_type):
    """Creates tables at the bottom"""
    data_copy = data.copy()
    data_copy = data_copy.loc[data_copy['fuel_category']
                              == filter_type]
    data_copy.drop(columns=['fuel_category'], inplace=True)
    data_copy.drop(
        columns=['fuel_category_id', 'fuel_type_id',
                 'fuel_type', 'updated_at'], inplace=True)
    data_copy.sort_values(by=['mw_generated'], inplace=True, ascending=False)

    data_copy.drop(columns=['mw_generated'], inplace=True)

    data_copy.rename(
        columns={"fuel_type_name": "Fuel Name", "Energy_Gen": "Power Generated"}, inplace=True)

    table = ff.create_table(
        data_copy, index_title=filter_type)
    # st.write(table)
    return table


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

    st.set_page_config(
        layout="wide", page_title="Energy Dashboard", page_icon="icon.png")

    st.logo("icon.png")
    st.title("WattWatch Dashboard")
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

    fig = px.bar(positive_mix_data, x='fuel_category',
                 y='mw_generated', color='fuel_type_name')
    col2.write(fig)

    demand_range = st.selectbox(
        "Demand Data Range",
        ("24h", "1 week", "1 month"), key="demand"
    )
    st.write(generate_demand_graph(db_cursor, demand_range))

    price_range = st.selectbox(
        "Price Data Range",
        ("24h", "1 week", "1 month"), key="price"
    )
    st.write(generate_price_graph(db_cursor, price_range))

    generation_range = st.selectbox(
        "Generation Data Range",
        ("24h", "1 week", "1 month"), key="generation"
    )
    st.write(generate_24h_energy_generation_graph(db_cursor, generation_range))

    # show_generation_stats(generation_mix_data)

    tab1, tab2 = st.columns(2)
    tab3, tab4 = st.columns(2)

    tab1.title('Fossil Fuels')
    tab1.plotly_chart(add_table(generation_mix_data, 'Fossil Fuels'), key=1)
    tab2.title('Renewables')
    tab2.plotly_chart(add_table(generation_mix_data, 'Renewables'), key=2)
    tab3.title('Interconnectors')
    tab3.plotly_chart(add_table(generation_mix_data, 'Interconnectors'), key=3)
    tab4.title('Others')
    tab4.plotly_chart(add_table(generation_mix_data, 'Other'), key=4)

    db_conn.close()


if __name__ == '__main__':
    main()
