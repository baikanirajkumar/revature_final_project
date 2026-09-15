import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Multi-Indicator Economic Analytics",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Multi-Indicator Economic Analytics Dashboard")

st.markdown(
    """
    Explore economic indicators across countries and continents
    using Snowflake, dbt, and Streamlit.
    """
)

st.markdown("---")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌍 Economic Analytics")

st.sidebar.markdown("---")

st.sidebar.write("### Dashboard Navigation")
st.sidebar.write("📊 Indicator Overview")
st.sidebar.write("🏆 Top Countries")
st.sidebar.write("📈 Country Trend")
st.sidebar.write("⚖️ Country Comparison")
st.sidebar.write("🌎 Continent Analysis")

st.sidebar.markdown("---")


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

conn = snowflake.connector.connect(
    account=st.secrets["snowflake"]["account"],
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
    role=st.secrets["snowflake"]["role"]
)


# ============================================================
# INDICATOR CONFIGURATION
# ============================================================

INDICATORS = {
    "GDP Current USD": {
        "code": "GDP_CURRENT_USD",
        "table": "ANNUAL_GDP_BY_COUNTRY",
        "value_column": "GDP_VALUE",
        "display_column": "GDP_VALUE",
        "unit": "Current US$",
        "color": "#1f77b4",
        "aggregation": "sum"
    },

    "GDP Constant 2015 USD": {
        "code": "GDP_CONST_2015_USD",
        "table": "ANNUAL_GDP_CONSTANT_BY_COUNTRY",
        "value_column": "GDP_VALUE",
        "display_column": "GDP_VALUE",
        "unit": "Constant 2015 US$",
        "color": "#2ca02c",
        "aggregation": "sum"
    },
    "GDP Growth %": {
        "code": "GDP_GROWTH_PCT",
        "table": "GDP_GROWTH_BY_COUNTRY",
        "value_column": "GDP_GROWTH_PERCENT",
        "display_column": "GDP_GROWTH_PERCENT",
        "unit": "%",
        "color": "#ff7f0e",
        "aggregation": "average"
    },
    

    "GDP Per Capita USD": {
        "code": "GDP_PER_CAPITA_USD",
        "table": "GDP_PER_CAPITA_BY_COUNTRY",
        "value_column": "GDP_PER_CAPITA_USD",
        "display_column": "GDP_PER_CAPITA_USD",
        "unit": "US$ per person",
        "color": "#9467bd",
        "aggregation": "average"
    },

    "Inflation CPI %": {
        "code": "INFLATION_CPI_PCT",
        "table": "INFLATION_BY_COUNTRY",
        "value_column": "INFLATION_CPI_PCT",
        "display_column": "INFLATION_CPI_PCT",
        "unit": "%",
        "color": "#d62728",
        "aggregation": "average"
    },

    "Population": {
        "code": "POPULATION",
        "table": "POPULATION_BY_COUNTRY",
        "value_column": "POPULATION",
        "display_column": "POPULATION",
        "unit": "People",
        "color": "#17becf",
        "aggregation": "sum"
    }
}


# ============================================================
# INDICATOR SELECTION
# ============================================================

st.subheader("📌 Select Indicator")

selected_indicator = st.selectbox(
    "Choose an economic indicator",
    list(INDICATORS.keys())
)

indicator = INDICATORS[selected_indicator]

indicator_table = indicator["table"]
value_column = indicator["value_column"]
indicator_color = indicator["color"]
indicator_unit = indicator["unit"]


st.markdown(
    f"""
    ### {selected_indicator}
    **Unit:** {indicator_unit}
    """
)


# ============================================================
# ANALYSIS MODE
# ============================================================

st.subheader("📅 Analysis Period")

analysis_mode = st.radio(
    "Choose analysis mode",
    [
        "All Available Years",
        "Selected Year"
    ],
    horizontal=True
)


# ============================================================
# GET FILTER DATA
# ============================================================

query_filters = """
SELECT DISTINCT
    CONTINENT,
    INCOME_GROUP
FROM GDP_ANALYTICS.DW.DIM_COUNTRY
ORDER BY CONTINENT, INCOME_GROUP
"""

df_filters = pd.read_sql(
    query_filters,
    conn
)


# ============================================================
# GET YEARS
# ============================================================

query_years = f"""
SELECT DISTINCT YEAR
FROM GDP_ANALYTICS.RAW_DW.{indicator_table}
ORDER BY YEAR DESC
"""

df_years = pd.read_sql(
    query_years,
    conn
)


# ============================================================
# DASHBOARD FILTERS
# ============================================================

st.subheader("🔎 Dashboard Filters")

col1, col2, col3 = st.columns(3)


# ------------------------------------------------------------
# YEAR
# ------------------------------------------------------------

with col1:

    if analysis_mode == "Selected Year":

        selected_year = st.selectbox(
            "📅 Select Year",
            df_years["YEAR"].tolist()
        )

    else:

        selected_year = None

        st.info("All available years selected")


# ------------------------------------------------------------
# CONTINENT
# ------------------------------------------------------------

with col2:

    continent_options = ["All"] + sorted(
        df_filters["CONTINENT"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_continent = st.selectbox(
        "🌎 Select Continent",
        continent_options
    )


# ------------------------------------------------------------
# INCOME GROUP
# ------------------------------------------------------------

with col3:

    income_options = ["All"] + sorted(
        df_filters["INCOME_GROUP"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_income = st.selectbox(
        "💰 Select Income Group",
        income_options
    )


# ============================================================
# BASE QUERY
# ============================================================

base_query = f"""
SELECT
    t.COUNTRY_ID,
    t.COUNTRY_NAME,
    t.ISO3,
    t.CONTINENT,
    t.YEAR,
    t.{value_column} AS INDICATOR_VALUE,
    t.IS_ESTIMATE
FROM GDP_ANALYTICS.RAW_DW.{indicator_table} AS t
WHERE 1 = 1
"""


query_params = []


# ============================================================
# YEAR FILTER
# ============================================================

if analysis_mode == "Selected Year":

    base_query += """
    AND t.YEAR = %s
    """

    query_params.append(selected_year)


# ============================================================
# CONTINENT FILTER
# ============================================================

if selected_continent != "All":

    base_query += """
    AND t.CONTINENT = %s
    """

    query_params.append(selected_continent)


# ============================================================
# INCOME GROUP FILTER
# ============================================================

# Income group is stored in DIM_COUNTRY.
# Therefore, apply the filter using COUNTRY_ID.

if selected_income != "All":

    base_query = f"""
    SELECT
        t.COUNTRY_ID,
        t.COUNTRY_NAME,
        t.ISO3,
        t.CONTINENT,
        t.YEAR,
        t.{value_column} AS INDICATOR_VALUE,
        t.IS_ESTIMATE
    FROM GDP_ANALYTICS.RAW_DW.{indicator_table} AS t

    JOIN GDP_ANALYTICS.DW.DIM_COUNTRY AS c
        ON t.COUNTRY_ID = c.COUNTRY_ID

    WHERE c.INCOME_GROUP = %s
    """

    query_params = [selected_income]

    if analysis_mode == "Selected Year":

        base_query += """
        AND t.YEAR = %s
        """

        query_params.append(selected_year)

    if selected_continent != "All":

        base_query += """
        AND c.CONTINENT = %s
        """

        query_params.append(selected_continent)


base_query += """
ORDER BY t.YEAR, t.COUNTRY_NAME
"""


df = pd.read_sql(
    base_query,
    conn,
    params=tuple(query_params)
)


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if df.empty:

    st.warning(
        f"No data available for {selected_indicator} "
        f"with the selected filters."
    )

    conn.close()

    st.stop()


# ============================================================
# FORMAT DATA
# ============================================================

df["INDICATOR_VALUE"] = pd.to_numeric(
    df["INDICATOR_VALUE"],
    errors="coerce"
)

df = df.dropna(
    subset=["INDICATOR_VALUE"]
)


# ============================================================
# KPI SECTION
# ============================================================

st.markdown("---")

st.subheader(
    f"📊 {selected_indicator} Overview"
)


# ------------------------------------------------------------
# KPI CALCULATIONS
# ------------------------------------------------------------

total_countries = df["COUNTRY_ID"].nunique()

average_value = df["INDICATOR_VALUE"].mean()

highest_row = df.loc[
    df["INDICATOR_VALUE"].idxmax()
]

lowest_row = df.loc[
    df["INDICATOR_VALUE"].idxmin()
]


# ------------------------------------------------------------
# TOTAL VALUE
# ------------------------------------------------------------

if indicator["aggregation"] == "sum":

    total_value = df["INDICATOR_VALUE"].sum()

else:

    total_value = df["INDICATOR_VALUE"].mean()


# ============================================================
# NUMBER FORMAT FUNCTION
# ============================================================

def format_value(value, unit):

    if pd.isna(value):
        return "N/A"

    if unit == "%":

        return f"{value:,.2f}%"

    if unit == "People":

        return f"{value:,.0f}"

    return f"{value:,.2f}"


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    if indicator["aggregation"] == "sum":

        label = f"Total {selected_indicator}"

    else:

        label = f"Average {selected_indicator}"

    st.metric(
        label,
        format_value(
            total_value,
            indicator_unit
        )
    )


with kpi2:

    st.metric(
        "🌍 Countries",
        f"{total_countries:,}"
    )


with kpi3:

    st.metric(
        f"📊 Average {selected_indicator}",
        format_value(
            average_value,
            indicator_unit
        )
    )


with kpi4:

    st.metric(
        f"🏆 Highest {selected_indicator}",
        highest_row["COUNTRY_NAME"]
    )


# ============================================================
# TOP 10 COUNTRIES
# ============================================================

st.markdown("---")

st.subheader(
    f"🏆 Top 10 Countries by {selected_indicator}"
)


# For percentage indicators, highest value is still meaningful
# but the chart is explicitly labelled as an indicator ranking.

df_top = (
    df.groupby(
        [
            "COUNTRY_ID",
            "COUNTRY_NAME",
            "CONTINENT"
        ],
        as_index=False
    )["INDICATOR_VALUE"]
    .mean()
)


df_top = df_top.sort_values(
    "INDICATOR_VALUE",
    ascending=False
).head(10)


fig_top = px.bar(
    df_top,
    x="INDICATOR_VALUE",
    y="COUNTRY_NAME",
    orientation="h",
    title=f"Top 10 Countries — {selected_indicator}",
    labels={
        "INDICATOR_VALUE": indicator_unit,
        "COUNTRY_NAME": "Country"
    }
)


fig_top.update_traces(
    marker_color=indicator_color
)


fig_top.update_layout(
    yaxis={
        "categoryorder": "total ascending"
    }
)


st.plotly_chart(
    fig_top,
    use_container_width=True
)


# ============================================================
# COUNTRY TREND
# ============================================================

st.markdown("---")

st.subheader(
    f"📈 {selected_indicator} — Country Trend"
)


# Get countries from current indicator table

country_options = sorted(
    df["COUNTRY_NAME"]
    .dropna()
    .unique()
    .tolist()
)


selected_country = st.selectbox(
    "🌍 Select Country",
    country_options
)


# ------------------------------------------------------------
# COUNTRY TREND QUERY
# ------------------------------------------------------------

country_query = f"""
SELECT
    t.COUNTRY_NAME,
    t.YEAR,
    t.{value_column} AS INDICATOR_VALUE
FROM GDP_ANALYTICS.RAW_DW.{indicator_table} AS t
WHERE t.COUNTRY_NAME = %s
ORDER BY t.YEAR
"""


df_country = pd.read_sql(
    country_query,
    conn,
    params=(selected_country,)
)


df_country["INDICATOR_VALUE"] = pd.to_numeric(
    df_country["INDICATOR_VALUE"],
    errors="coerce"
)


df_country = df_country.dropna(
    subset=["INDICATOR_VALUE"]
)


# ============================================================
# COUNTRY TREND CHART
# ============================================================

fig_country = px.line(
    df_country,
    x="YEAR",
    y="INDICATOR_VALUE",
    markers=True,
    title=f"{selected_indicator} Over Available Years — {selected_country}",
    labels={
        "YEAR": "Year",
        "INDICATOR_VALUE": indicator_unit
    }
)


fig_country.update_traces(
    line_color=indicator_color,
    marker_color=indicator_color
)


st.plotly_chart(
    fig_country,
    use_container_width=True
)


# ============================================================
# COUNTRY COMPARISON
# ============================================================

st.markdown("---")

st.subheader(
    f"⚖️ {selected_indicator} — Country Comparison"
)


comparison_countries = st.multiselect(
    "Select exactly 2 countries",
    country_options,
    max_selections=2
)


if len(comparison_countries) == 2:

    comparison_query = f"""
    SELECT
        COUNTRY_NAME,
        YEAR,
        {value_column} AS INDICATOR_VALUE
    FROM GDP_ANALYTICS.RAW_DW.{indicator_table}
    WHERE COUNTRY_NAME IN (%s, %s)
    ORDER BY YEAR, COUNTRY_NAME
    """

    df_comparison = pd.read_sql(
        comparison_query,
        conn,
        params=(
            comparison_countries[0],
            comparison_countries[1]
        )
    )


    df_comparison["INDICATOR_VALUE"] = pd.to_numeric(
        df_comparison["INDICATOR_VALUE"],
        errors="coerce"
    )


    fig_comparison = px.line(
        df_comparison,
        x="YEAR",
        y="INDICATOR_VALUE",
        color="COUNTRY_NAME",
        markers=True,
        title=(
            f"{selected_indicator} Comparison — "
            f"{comparison_countries[0]} vs "
            f"{comparison_countries[1]}"
        ),
        labels={
            "YEAR": "Year",
            "INDICATOR_VALUE": indicator_unit
        }
    )


    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )

else:

    st.info(
        "Please select exactly 2 countries to compare."
    )


# ============================================================
# CONTINENT ANALYSIS
# ============================================================

st.markdown("---")

st.subheader(
    f"🌎 {selected_indicator} by Continent"
)


# ------------------------------------------------------------
# AGGREGATION
# ------------------------------------------------------------

if indicator["aggregation"] == "sum":

    df_continent = (
        df.groupby(
            "CONTINENT",
            as_index=False
        )["INDICATOR_VALUE"]
        .sum()
    )

else:

    df_continent = (
        df.groupby(
            "CONTINENT",
            as_index=False
        )["INDICATOR_VALUE"]
        .mean()
    )


df_continent = df_continent.sort_values(
    "INDICATOR_VALUE",
    ascending=False
)


# ============================================================
# CONTINENT CHART
# ============================================================

fig_continent = px.bar(
    df_continent,
    x="CONTINENT",
    y="INDICATOR_VALUE",
    title=f"{selected_indicator} by Continent",
    labels={
        "CONTINENT": "Continent",
        "INDICATOR_VALUE": indicator_unit
    }
)


fig_continent.update_traces(
    marker_color=indicator_color
)


st.plotly_chart(
    fig_continent,
    use_container_width=True
)


# ============================================================
# DATA TABLE
# ============================================================

st.markdown("---")

st.subheader(
    f"📋 {selected_indicator} Data"
)


display_df = df.copy()


display_df = display_df.rename(
    columns={
        "COUNTRY_NAME": "Country",
        "ISO3": "ISO3",
        "CONTINENT": "Continent",
        "YEAR": "Year",
        "INDICATOR_VALUE": selected_indicator,
        "IS_ESTIMATE": "Estimate"
    }
)


columns_to_show = [
    "Country",
    "ISO3",
    "Continent",
    "Year",
    selected_indicator,
    "Estimate"
]


st.dataframe(
    display_df[columns_to_show],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Data Pipeline: Snowflake RAW → dbt Bronze/Silver/Gold → "
    "Streamlit Analytics"
)


# ============================================================
# CLOSE CONNECTION
# ============================================================

conn.close()