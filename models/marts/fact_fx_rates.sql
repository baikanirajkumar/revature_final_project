SELECT
    FX_ID,
    COUNTRY_ID,
    BASE_CCY,
    QUOTE_CCY,
    AS_OF_DATE,
    FX_RATE_BASE_PER_QUOTE,
    SOURCE_SYSTEM,
    UPDATED_AT
FROM {{ ref('stg_fx_rates') }}