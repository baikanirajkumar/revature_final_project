WITH ranked_gdp AS (
    SELECT
        COUNTRY_ID,
        COUNTRY_NAME,
        ISO3,
        CONTINENT,
        YEAR,
        GDP_VALUE,

        ROW_NUMBER() OVER (
            PARTITION BY YEAR
            ORDER BY GDP_VALUE DESC
        ) AS GDP_RANK

    FROM {{ ref('annual_gdp_by_country') }}
)

SELECT
    COUNTRY_ID,
    COUNTRY_NAME,
    ISO3,
    CONTINENT,
    YEAR,
    GDP_VALUE,
    GDP_RANK
FROM ranked_gdp
WHERE GDP_RANK <= 10