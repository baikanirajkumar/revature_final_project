
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="GDP Analytics",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 GDP Analytics Dashboard")
st.markdown(
    """
    Explore GDP data across countries and continents using
    Snowflake, dbt, and Streamlit.
    """
)
st.markdown("---")
st.sidebar.title("🌍 GDP Analytics")
st.sidebar.markdown("---")

st.sidebar.write("### Dashboard Navigation")
st.sidebar.write("📊 GDP Overview")
st.sidebar.write("🌍 Country Analysis")
st.sidebar.write("⚖️ Country Comparison")
# -----------------------------
# Snowflake Connection
# -----------------------------

conn = snowflake.connector.connect(
    account=st.secrets["snowflake"]["account"],
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
    role=st.secrets["snowflake"]["role"]
)


# -----------------------------
# Year Selection
# -----------------------------

# -----------------------------
# Filters
# -----------------------------

st.subheader("🔎 Dashboard Filters")

query_filters = """
SELECT
    DISTINCT
    c.CONTINENT,
    c.INCOME_GROUP
FROM GDP_ANALYTICS.DW.ANNUAL_GDP_BY_COUNTRY AS g
JOIN GDP_ANALYTICS.DW.DIM_COUNTRY AS c
    ON g.COUNTRY_ID = c.COUNTRY_ID
"""

df_filters = pd.read_sql(
    query_filters,
    conn
)

query_years = """
SELECT DISTINCT YEAR
FROM GDP_ANALYTICS.DW.ANNUAL_GDP_BY_COUNTRY
ORDER BY YEAR DESC
"""

df_years = pd.read_sql(
    query_years,
    conn
)

col1, col2, col3 = st.columns(3)

with col1:
    selected_year = st.selectbox(
        "📅 Select Year",
        df_years["YEAR"].tolist()
    )

with col2:
    continent_options = ["All"] + sorted(
        df_filters["CONTINENT"].dropna().unique().tolist()
    )

    selected_continent = st.selectbox(
        "🌎 Select Continent",
        continent_options
    )

with col3:
    income_options = ["All"] + sorted(
        df_filters["INCOME_GROUP"].dropna().unique().tolist()
    )

    selected_income = st.selectbox(
        "💰 Select Income Group",
        income_options
    )
# -----------------------------
# KPI - Total GDP
# -----------------------------

# -----------------------------
# KPI Cards
# -----------------------------
st.subheader("📊 GDP Overview")
query_kpis = """
SELECT
    SUM(g.GDP_VALUE) AS TOTAL_GDP,
    COUNT(DISTINCT g.COUNTRY_ID) AS TOTAL_COUNTRIES,
    AVG(g.GDP_VALUE) AS AVERAGE_GDP
FROM GDP_ANALYTICS.DW.ANNUAL_GDP_BY_COUNTRY AS g
JOIN GDP_ANALYTICS.DW.DIM_COUNTRY AS c
    ON g.COUNTRY_ID = c.COUNTRY_ID
WHERE g.YEAR = %s
  AND (%s = 'All' OR c.CONTINENT = %s)
  AND (%s = 'All' OR c.INCOME_GROUP = %s)
"""

df_kpis = pd.read_sql(
    query_kpis,
    conn,
    params=(
        selected_year,
        selected_continent,
        selected_continent,
        selected_income,
        selected_income
    )
)


query_highest = """
SELECT
    COUNTRY_NAME,
    GDP_VALUE
FROM GDP_ANALYTICS.DW.ANNUAL_GDP_BY_COUNTRY
WHERE YEAR = %s
ORDER BY GDP_VALUE DESC
LIMIT 1
"""

df_highest = pd.read_sql(
    query_highest,
    conn,
    params=(selected_year,)
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total GDP",
        f"{df_kpis['TOTAL_GDP'].iloc[0]:,.2f}"
    )

with col2:
    st.metric(
        "🌍 Total Countries",
        f"{df_kpis['TOTAL_COUNTRIES'].iloc[0]:,}"
    )

with col3:
    st.metric(
        "📊 Average GDP",
        f"{df_kpis['AVERAGE_GDP'].iloc[0]:,.2f}"
    )

with col4:
    st.metric(
        "🏆 Highest GDP",
        df_highest["COUNTRY_NAME"].iloc[0]
    )
# -----------------------------
# Top 10 Countries
# -----------------------------

st.subheader(
    f"🏆 Top 10 Countries by GDP — {selected_year}"
)

query_top = """
SELECT
    t.COUNTRY_NAME,
    t.GDP_VALUE,
    t.GDP_RANK,
    t.YEAR
FROM GDP_ANALYTICS.DW.TOP_GDP_COUNTRIES AS t
JOIN GDP_ANALYTICS.DW.DIM_COUNTRY AS c
    ON t.COUNTRY_ID = c.COUNTRY_ID
WHERE t.YEAR = %s
  AND (%s = 'All' OR c.CONTINENT = %s)
  AND (%s = 'All' OR c.INCOME_GROUP = %s)
ORDER BY t.GDP_RANK
"""

df_top = pd.read_sql(
    query_top,
    conn,
    params=(
        selected_year,
        selected_continent,
        selected_continent,
        selected_income,
        selected_income
    )
)

fig_top = px.bar(
    df_top,
    x="GDP_VALUE",
    y="COUNTRY_NAME",
    orientation="h",
    title=f"Top 10 Countries by GDP — {selected_year}"
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
# -----------------------------
# GDP by Country
# -----------------------------

st.subheader(
    "📊 GDP by Country — Available Years"
)

query_countries = """
SELECT DISTINCT COUNTRY_NAME
FROM GDP_ANALYTICS.DW.ANNUAL_GDP_BY_COUNTRY
ORDER BY COUNTRY_NAME
"""

df_countries = pd.read_sql(
    query_countries,
    conn
)

selected_country = st.selectbox(
    "Select a country",
    df_countries["COUNTRY_NAME"].tolist()
)


# -----------------------------
# Country GDP Data
# -----------------------------

query_country_gdp = """
SELECT
    COUNTRY_NAME,
    YEAR,
    GDP_VALUE
FROM GDP_ANALYTICS.DW.ANNUAL_GDP_BY_COUNTRY
WHERE COUNTRY_NAME = %s
ORDER BY YEAR
"""

df_country_gdp = pd.read_sql(
    query_country_gdp,
    conn,
    params=(selected_country,)
)


# -----------------------------
# Country GDP Chart
# -----------------------------

fig_country_gdp = px.line(
    df_country_gdp,
    x="YEAR",
    y="GDP_VALUE",
    markers=True,
    title=f"GDP Over Available Years — {selected_country}"
)

fig_country_gdp.update_xaxes(
    title="Year"
)

fig_country_gdp.update_yaxes(
    title="GDP (Current US$)"
)

st.plotly_chart(
    fig_country_gdp,
    use_container_width=True
)

# -----------------------------
# Country Comparison
# -----------------------------

st.subheader("⚖️ Country GDP Comparison")

comparison_countries = st.multiselect(
    "Select 2 countries to compare",
    df_countries["COUNTRY_NAME"].tolist(),
    max_selections=2
)


if len(comparison_countries) == 2:

    query_comparison = """
    SELECT
        COUNTRY_NAME,
        YEAR,
        GDP_VALUE
    FROM GDP_ANALYTICS.DW.ANNUAL_GDP_BY_COUNTRY
    WHERE COUNTRY_NAME IN (%s, %s)
    ORDER BY YEAR, COUNTRY_NAME
    """

    df_comparison = pd.read_sql(
        query_comparison,
        conn,
        params=(
            comparison_countries[0],
            comparison_countries[1]
        )
    )

    fig_comparison = px.line(
        df_comparison,
        x="YEAR",
        y="GDP_VALUE",
        color="COUNTRY_NAME",
        markers=True,
        title="GDP Comparison"
    )

    fig_comparison.update_xaxes(
        title="Year"
    )

    fig_comparison.update_yaxes(
        title="GDP (Current US$)"
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )

else:

    st.info("Please select exactly 2 countries to compare.")
# -----------------------------
# GDP by Continent
# -----------------------------

st.subheader(
    f"🌎 GDP by Continent — {selected_year}"
)

query_continent = """
SELECT
    CONTINENT,
    TOTAL_GDP
FROM GDP_ANALYTICS.DW.GDP_BY_CONTINENT
WHERE YEAR = %s
ORDER BY TOTAL_GDP DESC
"""

df_continent = pd.read_sql(
    query_continent,
    conn,
    params=(selected_year,)
)


# -----------------------------
# Continent Chart
# -----------------------------

fig_continent = px.bar(
    df_continent,
    x="CONTINENT",
    y="TOTAL_GDP",
    title=f"Total GDP by Continent — {selected_year}"
)

fig_continent.update_xaxes(
    title="Continent"
)

fig_continent.update_yaxes(
    title="Total GDP"
)

st.plotly_chart(
    fig_continent,
    use_container_width=True
)


# -----------------------------
# Close Connection
# -----------------------------

conn.close()
