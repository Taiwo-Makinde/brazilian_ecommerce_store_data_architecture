# Manual execution of the codes 

# Python standard standard packages
import subprocess

# Local customised packages 
from scripts import config_brazilian_ecommerce as config                        # We need config for the dbt folder location
from scripts.load_brazilian_ecommerce import run_load_sequence                  # run_load_sequence encapsulates all the functions for downloading, extracting, creating database for and loading the datasets.


# dbt build 
def run_dbt_build():
    subprocess.run(
        ["dbt", "build", "--profile-dir", "."],
        cwd=config.DBT_PROJECT_DIR, 
        check=True,
    )


# The major pipeline orchestration function 
def run_extract_load_transform_brazilian_ecommerce():
    run_load_sequence()
    run_dbt_build()


# Script Guard 
if __name__ == "__main__":
    run_extract_load_transform_brazilian_ecommerce()
