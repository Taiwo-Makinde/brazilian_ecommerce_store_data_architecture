# Loading 
# Import Python standard packages 
import os
from pathlib import Path 

# Import Third Party Python Packages 
import pandas as pd
import sqlalchemy                     # sqlalchemy module for loading data into sql database
from sqlalchemy.exc import IntegrityError, SQLAlchemyError                  # We want to know if the primary keys and foreign keys were consistent

import psycopg2
from psycopg2 import sql                                    # psycopg2 module is for running raw SQL data definition language (ddl) or data manipulation language (dml) scripts.

# Import customised local modules/packages
from scripts import config_brazilian_ecommerce as config
from scripts.config_brazilian_ecommerce import brazilian_ecommerce_db_engine                            # contains db_host, port, db_name, db_user, db_password
from scripts.extract_brazilian_ecommerce import run_extract_sequence


# We create the database and the different tables in it
def create_database(config):
    # Create the database 
    conn = psycopg2.connect(config.brazilian_ecommerce_db_engine)
    conn.autocommit= True
    cur = conn.cursor()
    cur.execute ("SELECT 1 FROM pg_database WHERE datname = %s", (config.DB_NAME,))
    if not cur.fetchbone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(config.DB_NAME)))
        print(f"Database '{config.DB_NAME}' created.")
    else:
        print(f"Database '{config.DB_NAME}' already exists.")
    
    # Create the schema & tables
    with open ("001_Brazilian_ecommerce_Schema.sql") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Schema Applied.")


def load_database(brazilian_ecommerce_dataframes_dict, brazilian_ecommerce_db_engine):
    # Load each of the .csv into their database 
    for key, df_name in brazilian_ecommerce_dataframes_dict.items():                            # I use for before try so that we have a try block for each iteration. 
        table_name = key.removesuffix("_df")
        try:
            df_name.to_sql(table_name, brazilian_ecommerce_db_engine,if_exists="append", index=False, method="multi", chunksize=1000)
            print(f"Loaded {len(df_name)} rows into {table_name}")
        except IntegrityError as e:
            print(f"Constraint violation while loading {table_name} : {e}")
            raise
        except SQLAlchemyError as sqle:
            print(f"Database error while loading '{table_name}': {sqle}")
            raise

    print("All Table loaded successfully. ")


# Orchestration
def run_load_sequence():                                                                            # We do not need to state config and brazilian_ecommerce_db_engine as parameters because they were imported and are now global variables.
    create_database(config)                                                                         # Call the function that creates database. 
    brazilian_ecommerce_dataframes_dict = run_extract_sequence()                                    # Call the function that orchestrates the download function and reads the csv files into a dictionary and returns the dictionary
    load_database(brazilian_ecommerce_dataframes_dict, brazilian_ecommerce_db_engine)               # call the function that iterates through the dataframes and loads the dataframes into the respective tables in the database


# Script guide
if __name__ == "__main__":
    run_load_sequence()










