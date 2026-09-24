# Orchestration with airflow (dag)

# Standard python Library 
from datetime import datetime                                                   # Python standard package for time is required because the date and time is necessary for scheduling.

# Third party Python packages (Airflow only)
from airflow import DAG                                                         # Directed Acyclic Graph which is a visual abstraction/blueprint of tasks in a pipeline and the order in which they should run.
from airflow.operators.python import PythonOperator                             # Python Operator helps run python function 
from airflow.operators.bash import BashOperator                                 # Used to run bash commands such as dbt build which would typically be inputted in terminal 
                                                
# Local customised packages 
from scripts import config_brazilian_ecommerce as config                        # We need config for the dbt folder location
from scripts.load_brazilian_ecommerce import run_load_sequence()                # run_load_sequence encapsulates all the functions for downloading, extracting, creating database for and loading the datasets.


# The major pipeline orchestration function 
def run_extract_load_brazilian_ecommerce():
    run_load_sequence()

with DAG(
    dag_id="brazilian_ecommerce_olist_pipeline",
    schedule="0 6 * * *",                                                       # 6am every day (0 minute, 6 hour, any day, any month, any day of the week) 
    start_date=datetime(2026, 10, 1)                                            # 1st October 2026
    catchup=False,
) as dag:
    extract_load = PythonOperator(
    task_id="extract_and_load_olist",
    python_callable=run_extract_load_brazilian_ecommerce,
    )

    dbt_build = BashOperator (
        task_id="dbt_build",
        bash_command=f"cd {config.DBT_PROJECT_DIR} && dbt build --profiles-dir .",  
    )

    extract_load >> dbt_build                                                   # extract_load runs first before dbt_build



