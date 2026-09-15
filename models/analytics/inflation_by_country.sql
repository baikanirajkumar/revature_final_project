SELECT
    c.COUNTRY_ID,
    c.COUNTRY_NAME,
    c.ISO3,
    c.CONTINENT,
    o.YEAR,
    o.VALUE AS INFLATION_CPI_PCT,
    o.IS_ESTIMATE
FROM {{ ref('fact_gdp_observations') }} AS o
JOIN {{ ref('dim_country') }} AS c
    ON o.COUNTRY_ID = c.COUNTRY_ID
JOIN {{ ref('dim_indicator') }} AS i
    ON o.INDICATOR_ID = i.INDICATOR_ID
WHERE i.INDICATOR_CODE = 'INFLATION_CPI_PCT'