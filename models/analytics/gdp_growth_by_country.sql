WITH gdp_data AS (
    SELECT
        COUNTRY_ID,
        COUNTRY_NAME,
        ISO3,
        CONTINENT,
        YEAR,
        GDP_VALUE
    FROM {{ ref('annual_gdp_by_country') }}
),

growth_calculation AS (
    SELECT
        COUNTRY_ID,
        COUNTRY_NAME,
        ISO3,
        CONTINENT,
        YEAR,
        GDP_VALUE,

        LAG(GDP_VALUE) OVER (
            PARTITION BY COUNTRY_ID
            ORDER BY YEAR
        ) AS PREVIOUS_YEAR_GDP

    FROM gdp_data
)

SELECT
    COUNTRY_ID,
    COUNTRY_NAME,
    ISO3,
    CONTINENT,
    YEAR,
    GDP_VALUE,
    PREVIOUS_YEAR_GDP,

    CASE
        WHEN PREVIOUS_YEAR_GDP IS NOT NULL
             AND PREVIOUS_YEAR_GDP <> 0
        THEN
            ((GDP_VALUE - PREVIOUS_YEAR_GDP)
             / ABS(PREVIOUS_YEAR_GDP)) * 100
        ELSE NULL
    END AS GDP_GROWTH_PERCENT

FROM growth_calculation