SELECT
    CONTINENT,
    YEAR,
    SUM(GDP_VALUE) AS TOTAL_GDP
FROM {{ ref('annual_gdp_by_country') }}
GROUP BY
    CONTINENT,
    YEAR
ORDER BY
    YEAR,
    TOTAL_GDP DESC