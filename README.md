# brazilian_ecommerce_store_data_architecture
A real-world data architecture project that extracts a Brazilian ecommerce store's datasets from Kaggle using its API and loads it into a PostgreSQL database, then migrates and transforms the data into a data warehouse using dbt. Airflow orchestrates the end-to-end pipeline.

## Table of Contents
- [Overview](#overview)
- [Data Pipeline Flow](#data-pipeline-flow)
- [Project Structure](#project-structure)
- [Pipelines](#pipelines)
- [Data Warehouse](#data-warehouse)
- [Database Entity Relationship Model Diagram](#database-entity-relationship-model-diagram)
- [Data Warehouse Entity Relationship Model Diagram](#data-warehouse-entity-relationship-model-diagram)
- [Data Model Notes](#data-model-notes)
- [Supporting Folders](#supporting-folders)
- [Environment Configuration](#environment-configuration)
- [Use Cases](#use-cases)
- [Version History](#version-history)

## Overview

This project simulates a realistic, end-to-end data infrastructure setup, starting from raw source data and ending in an analytics-ready warehouse.

Rather than loading a CSV directly into a warehouse, this project mirrors how the data typically exists in the real world : first as records in an operational (OLTP) database, and only later extracted into a warehouse for analysis. The pipeline is split into two clear stages:

1. **Extraction & Load** — Data is downloaded from Kaggle via its API, and loaded into a normalized PostgreSQL database (`db`) with full primary key, foreign key, and other constraints enforced.
2. **Migration & Transformation** — Data is extracted from the operational database into a data warehouse and transformed through a medallion architecture (bronze → silver → gold) using dbt, ending in a star schema optimized for analytics.

Apache Airflow orchestrates both stages, while each stage also remains independently runnable from the command line for local development and testing.

## Data Pipeline Flow

```
Kaggle API
    │
    ▼
download_dataset()  ──────────────▶  data/ (raw CSVs)
    │
    ▼
read_data_frames()  ──────────────▶  dataframe_dict
    │
    ▼
create_database()   ──────────────▶  db (PostgreSQL, constrained schema)
    │
    ▼
load_database()     ──────────────▶  db populated with source data
    │
    ▼
run_transform_dbt() ──────────────▶  dbt build
                                          │
                                          ▼
                                     bronze  (raw extract from db)
                                          │
                                          ▼
                                     silver (cleaned, typed, constrained)
                                          │
                                          ▼
                                     gold   (star schema: facts & dimensions)
```

Each arrow above corresponds to a function or task that can be triggered either manually (via `main.py`) or through Airflow (via `dags/pipeline_dag.py`).

## Project Structure

```
project-root/
│
├── config/
│   ├── .env                              # gitignored
│   └── .env.example
│
├── data/                                 # gitignored — raw CSVs land here
│
├── database/
│   ├── db/
│   │   ├── migrations/
│   │   │   └── 001_Brazilian_ecommerce_Schema.sql
│   │   ├── schema/
│   │   │   └── db_schema_snapshot.sql    # generated via pg_dump
│   │   └── diagrams/
│   │       └── erd.png
│   └── dwh/
│       ├── schema/
│       │   └── dwh_schema_snapshot.sql   # generated via pg_dump
│       └── diagrams/
│           └── star_schema.png
│
├── dags/
│   └── brazilian_ecommerce_dag.py                   # Airflow scans this folder
│
├── pipeline/
│   ├── __init__.py
│   ├── config_brazilian_ecommerce.py                         # loads .env, exposes db_engine, DBT_PROJECT_DIR, etc.
│   ├── extract_brazilian_ecommerce.py                        # run_extract(), download_dataset(), read_data_frames()
│   ├── load_brazilian_ecommerce.py                           # create_database(), load_database(), run_load(), run_transform_dbt()
│   │
│   └── warehouse/                        # dbt project root
│       ├── dbt_project.yml
│       ├── profiles.yml
│       ├── models/
│       │   ├── bronze/
│       │   │   ├── sources.yml
│       │   │   ├── bronze_customers.sql
│       │   │   └── bronze_orders.sql
│       │   ├── silver/
│       │   │   ├── silver_customers.sql
│       │   │   ├── silver_orders.sql
│       │   │   └── schema.yml
│       │   └── gold/
│       │       ├── dim_customer.sql
│       │       ├── dim_product.sql
│       │       ├── fact_orders.sql
│       │       └── schema.yml
│       └── seeds/                        # lookup tables (e.g. status_lookup.csv)
│
├── main_brazilian_ecommerce.py                               # manual entry point
├── pyproject.toml                        # makes `pipeline` importable from dags/
└── .gitignore
```

## Pipelines

The `pipeline/` package contains all extraction, load, and transformation logic, organized into small, single-purpose orchestration functions.

| Function | Location | Responsibility |
|---|---|---|
| `download_dataset()` | `pipeline/extract.py` | Downloads the raw dataset from Kaggle via its API into `data/` |
| `read_data_frames(config)` | `pipeline/extract.py` | Reads each CSV in `data/` into a `dict[str, pd.DataFrame]`, in dependency order |
| `run_extract()` | `pipeline/extract.py` | Orchestrates download + read; returns the populated `dataframe_dict` |
| `create_database(config)` | `pipeline/load.py` | Creates the `db` PostgreSQL database and applies the constrained schema migration |
| `load_database(dataframe_dict, db_engine)` | `pipeline/load.py` | Loads each DataFrame into its corresponding table, respecting foreign key load order |
| `run_load()` | `pipeline/load.py` | Orchestrates `create_database()` → `run_extract()` → `load_database()` |
| `run_transform_dbt()` | `pipeline/load.py` | Runs `dbt build` against the warehouse project, transforming `db` data through bronze → silver → gold |

Both `main.py` (manual runs) and `dags/pipeline_dag.py` (Airflow runs) call these same functions — no logic is duplicated or written twice for either entry point.

```bash
# Run the full pipeline manually
python main.py
```

## Data Warehouse

The warehouse is built with dbt (dbt Core), following a medallion architecture across three schemas within a dedicated warehouse database:

| Layer | Schema | Purpose |
|---|---|---|
| **Bronze** | `bronze` | Raw extract from `db`, mirroring its normalized (snowflake) structure. No constraints — fidelity to source is the priority. |
| **Silver** | `silver` | Cleaned, typed, and constrained (primary keys, foreign keys, `not_null`, `unique`, `relationships`). Still normalized. |
| **Gold** | `gold` | Denormalized star schema — fact and dimension tables — built specifically for reporting and analysis. |

dbt tests replace what would otherwise be manual validation queries, declared alongside each model in its `schema.yml`.

```bash
cd pipeline/warehouse
dbt build --profiles-dir .
```

## Database Entity Relationship Model Diagram

The operational database (`db`) is fully normalized, so its entity relationship diagram shows the tables, primary/foreign keys, and relationships as they exist in the constrained OLTP schema. It is documented at:

```
database/db/diagrams/erd.png
```

This diagram should be regenerated whenever `database/db/migrations/001_create_oltp_schema.sql` changes, so it stays an accurate reflection of the live schema rather than the originally authored one.

## Data Warehouse Entity Relationship Model Diagram

The warehouse's star schema — its fact and dimension tables and how they relate — is documented visually at:

```
database/dwh/diagrams/star_schema.png
```

This diagram reflects the `gold` layer specifically, since that's the schema designed for dimensional querying; `bronze` and `silver` remain normalized and are represented by the same structure as the operational database's ERD.

## Data Model Notes

- **Source database (`db`)** is deliberately modeled as a realistic OLTP system — fully normalized, with primary keys, foreign keys, `NOT NULL`, `UNIQUE`, and `CHECK` constraints enforced at the database level. This stands in for what would, in a real company, already exist before any warehouse work begins.
- **Bronze** intentionally carries no constraints — its job is raw fidelity, not correctness.
- **Silver** re-applies constraints, since this is the trusted, general-purpose layer that other consumers (not just the gold layer) could reasonably query.
- **Gold** is built as real tables (not views), populated via dbt models, allowing for surrogate keys and more complex transformation logic than a materialized view would easily support.
- Schema snapshots under `database/*/schema/` are generated via `pg_dump --schema-only` and should never be hand-edited — they exist purely as an accurate, point-in-time reference of what's actually in each database.

## Supporting Folders

| Folder | Purpose |
|---|---|
| `config/` | Environment configuration (`.env`), loaded by `pipeline/config.py` |
| `data/` | Raw CSVs downloaded from Kaggle; gitignored, regenerated by `download_dataset()` |
| `database/db/migrations/` | Authored DDL used to create the operational database schema |
| `database/db/schema/`, `database/dwh/schema/` | Generated `pg_dump` schema snapshots |
| `database/db/diagrams/`, `database/dwh/diagrams/` | ERD and star schema diagrams |
| `dags/` | Airflow DAG definitions, scanned automatically by the Airflow scheduler |

## Environment Configuration

Connection details and paths are managed via a `.env` file, loaded by `pipeline/config.py`. Copy the example file and fill in real values before running the pipeline:

```bash
cp config/.env.example config/.env
```

Typical variables include:

```
KAGGLE_USERNAME=
KAGGLE_KEY=

DB_HOST=localhost
DB_PORT=5432
DB_NAME=db
DB_USER=
DB_PASSWORD=

DWH_HOST=localhost
DWH_PORT=5432
DWH_NAME=dwh
DWH_USER=
DWH_PASSWORD=

DBT_PROJECT_DIR=pipeline/warehouse
```

`config/` is gitignored; only 

## Use Cases

- **Local development** — run the full pipeline directly via `python main.py`, without needing Airflow running at all.
- **Orchestrated / scheduled runs** — trigger the same pipeline through Airflow, with per-stage task visibility, logging, and dependency management via `dags/pipeline_dag.py`.
- **Analytics** — query the `gold` schema directly for reporting, dashboards, or ad hoc analysis, without needing to understand the underlying normalized source structure.
- **Auditing / debugging** — trace any gold-layer figure back through silver and bronze to the original source data in `db`, since each layer preserves traceability back to the one before it.

## Version History

| Version | Date | Notes |
|---|---|---|
| 0.1.0 | TBD | Initial project scaffold: extraction, OLTP load, medallion warehouse structure, Airflow orchestration |
