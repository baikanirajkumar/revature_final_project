# 🌍 GDP Analytics

A data engineering and analytics project that processes GDP and economic data using **Snowflake, dbt, and Streamlit**.

The project demonstrates a modern data pipeline from raw CSV files to a cloud data warehouse, transformation layer, analytical models, and an interactive dashboard.

---

## 🏗️ Architecture

```text
                CSV Files
                    │
                    ▼
          Snowflake Internal Stage
                    │
                    ▼
              RAW Tables
                    │
                    ▼
              dbt Staging
                    │
                    ▼
          Data Warehouse Layer
          ┌─────────┴─────────┐
          │                   │
      Dimensions            Facts
          │                   │
          └─────────┬─────────┘
                    │
                    ▼
            dbt Analytics
                    │
                    ▼
          Streamlit Dashboard
```

---

## 🛠️ Technologies Used

* **Python**
* **SQL**
* **Snowflake**
* **dbt**
* **Streamlit**
* **Pandas**
* **Plotly**
* **Git & GitHub**

---

## 📂 Data Sources

The project uses four CSV datasets:

### Countries

`gdp_countries.csv`

Contains country-level information such as:

* Country ID
* Country name
* ISO3 code
* Continent
* Sub-region
* Local currency
* Market type
* Income group

### Indicators

`gdp_indicators.csv`

Contains economic indicator definitions such as:

* GDP
* GDP growth
* GDP per capita
* Inflation
* Population

### GDP Observations

`gdp_observations.csv`

Contains GDP observations by:

* Country
* Indicator
* Year
* Value
* Source system
* Vintage date
* Estimate flag

### FX Rates

`gdp_fx_rates.csv`

Contains foreign exchange rate information.

---

## ❄️ Snowflake Data Warehouse

Snowflake is used as the main data warehouse.

### Database

```text
GDP_ANALYTICS
```

### Schemas

```text
RAW
DW
```

### RAW Layer

The raw layer stores the original CSV data.

```text
RAW_COUNTRIES
RAW_INDICATORS
RAW_FX_RATES
RAW_OBSERVATIONS
```

### DW Layer

The warehouse layer contains:

```text
DIM_COUNTRY
DIM_INDICATOR
DIM_DATE

FACT_GDP_OBSERVATIONS
FACT_FX_RATES
```

---

## 🔄 dbt Transformation Layer

dbt is used to transform and test the Snowflake data.

### Staging Models

```text
stg_countries
stg_indicators
stg_fx_rates
stg_observations
```

The staging layer performs basic transformations such as:

* Trimming strings
* Standardizing currency codes
* Standardizing ISO codes
* Preparing raw data for analytical models

### Warehouse Models

```text
dim_country
dim_indicator
dim_date
fact_gdp_observations
fact_fx_rates
```

### Analytics Models

```text
annual_gdp_by_country
gdp_growth_by_country
top_gdp_countries
gdp_by_continent
```

---

## 🧪 Data Quality

dbt tests are used to validate the warehouse.

The project includes tests for:

* Primary key uniqueness
* Not-null columns
* Foreign key relationships
* Referential integrity

Current test result:

```text
PASS = 40
WARN = 0
ERROR = 0
```

---

## 📊 Streamlit Dashboard

The Streamlit dashboard provides an interactive interface for exploring GDP data.

### Dashboard Features

* 📅 Year selection
* 🌎 Continent filter
* 💰 Income group filter
* 💵 Total GDP KPI
* 🌍 Total countries KPI
* 📊 Average GDP KPI
* 🏆 Highest GDP country
* Top 10 countries by GDP
* GDP by country
* Country GDP comparison
* GDP by continent

---

## 🔍 Analytical Use Cases

The project supports analysis such as:

### GDP Ranking

Identify the top countries by GDP for a selected year.

### Country Analysis

Explore GDP values for individual countries across the available years.

### Country Comparison

Compare GDP values between two selected countries.

### Continental Analysis

Analyze total GDP across continents.

---

## ⚠️ Data Availability

The current sample dataset contains a limited number of GDP observations across years.

Therefore, some countries may have only one available year while others may have multiple years.

The dashboard displays the available data rather than generating artificial values for missing years.

---

## 🚀 Project Workflow

```text
1. Upload CSV files
        ↓
2. Create Snowflake database and schemas
        ↓
3. Create Snowflake file format
        ↓
4. Upload files to internal stage
        ↓
5. Load data into RAW tables
        ↓
6. Configure dbt
        ↓
7. Create staging models
        ↓
8. Create dimensions and fact tables
        ↓
9. Create analytical models
        ↓
10. Run dbt data quality tests
        ↓
11. Connect Streamlit to Snowflake
        ↓
12. Build interactive dashboard
```

---

## 💻 Running the Project

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd gdp_analytics
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Snowflake credentials

Create:

```text
.streamlit/secrets.toml
```

Add your Snowflake connection details.

Do **not** commit this file to GitHub.

### 6. Run dbt

```bash
dbt debug
```

```bash
dbt run
```

```bash
dbt test
```

### 7. Run Streamlit

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```text
gdp_analytics/
│
├── app.py
├── dbt_project.yml
├── requirements.txt
├── README.md
├── .gitignore
│
├── models/
│   ├── staging/
│   │   ├── stg_countries.sql
│   │   ├── stg_indicators.sql
│   │   ├── stg_fx_rates.sql
│   │   └── stg_observations.sql
│   │
│   └── marts/
│       ├── dim_country.sql
│       ├── dim_indicator.sql
│       ├── dim_date.sql
│       ├── fact_gdp_observations.sql
│       ├── fact_fx_rates.sql
│       ├── annual_gdp_by_country.sql
│       ├── gdp_growth_by_country.sql
│       ├── top_gdp_countries.sql
│       └── gdp_by_continent.sql
│
├── .streamlit/
│   └── secrets.toml
│
└── ...
```

---

## 🎯 Project Goals

This project demonstrates practical experience with:

* Cloud data warehousing
* Snowflake architecture
* Data ingestion
* Data modeling
* ETL/ELT concepts
* dbt transformations
* Data quality testing
* Analytical SQL
* Python
* Interactive dashboards
* Data engineering workflow

---

## 👩‍💻 Author

**Baikani Raj Kumar**

Aspiring Data Engineer with a focus on:

```text
Python
SQL
Snowflake
dbt
PySpark
Data Engineering
```
