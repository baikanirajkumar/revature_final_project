WITH date_range AS (
    SELECT
        MIN(PERIOD_START) AS min_date,
        MAX(PERIOD_START) AS max_date
    FROM {{ ref('stg_observations') }}
),

dates AS (
    SELECT
        DATEADD(
            DAY,
            SEQ4(),
            min_date
        ) AS full_date
    FROM date_range,
    TABLE(GENERATOR(ROWCOUNT => 10000))
    WHERE DATEADD(DAY, SEQ4(), min_date) <= max_date
)

SELECT
    full_date AS date_key,
    YEAR(full_date) AS year,
    QUARTER(full_date) AS quarter,
    MONTH(full_date) AS month,
    MONTHNAME(full_date) AS month_name,
    DAY(full_date) AS day,
    DAYOFWEEK(full_date) AS day_of_week
FROM dates