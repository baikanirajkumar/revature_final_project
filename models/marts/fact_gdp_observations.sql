SELECT
    o.OBS_ID,
    o.COUNTRY_ID,
    o.INDICATOR_ID,
    o.PERIOD_START,
    o.YEAR,
    o.VALUE,
    o.SOURCE_SYSTEM,
    o.VINTAGE_DATE,
    o.IS_ESTIMATE,
    o.UPDATED_AT
FROM {{ ref('stg_observations') }} AS o