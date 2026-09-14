# Loading 
# Import Python standard packages 
import os
import Path 

# Import Third Party Python Packages 
import pandas as pd
import sqlalchemy import create_engine                      # sqlalchemy module for loading data into sql database
from sqlalchemy.exc import IntegrityError                   # We want to know if the primary keys and foreign keys were consistent

import psycopg2
from psycopg2 import sql                                    # psycopg2 module is for running raw SQL data definition language (ddl) or data manipulation language (dml) scripts.

# Import customised local modules/packages
from scripts import config_brazilian_ecommerce as config
from scripts.config_brazilian_ecommerce import brazilian_ecommerce_db_engine                            # contains db_host, port, db_name, db_user, db_password


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
    with open ("001_Schema.sql") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Schema Applied.")


def load_database(brazilian_ecommerce_dataframes_dict, brazilian_ecommerce_db_engine, ):
    # Load each of the .csv into their database 
    load_order = [
        brazilian_ecommerce_dataframes_dict["geolocation_df"],
        brazilian_ecommerce_dataframes_dict["customers_df"],
        brazilian_ecommerce_dataframes_dict["sellers_df"],
        brazilian_ecommerce_dataframes_dict["orders_df"],
        brazilian_ecommerce_dataframes_dict["products_df"],
        brazilian_ecommerce_dataframes_dict["order_reviews_df"],
        brazilian_ecommerce_dataframes_dict["order_payments_df"],
        brazilian_ecommerce_dataframes_dict["order_items_df"],
        brazilian_ecommerce_dataframes_dict ["product_category_name_translation_df"]                              # Lookup table/dataframe for translation from Portuguese to English
    ]

    try:
        for table in brazilian_ecommerce_dataframes_dict.keys() & dataframe_name in brazilian_ecommerce_dataframes_dict.values():
            table = ((brazilian_ecommerce_dataframes_dict.keys()).removesuffix("_df"))
            dataframe_name = brazilian_ecommerce_dataframes_dict[""]

            dataframe_name.to_sql(table, brazilian_ecommerce_db_engine, if_exists="append", index="False", method="multi", chunksize=1000 )
            print(f"Loaded {len(dataframe_name)} rows into {table}")
    except IntegrityError as interr:
        print(f"Failed loading {table} : {e}")
        raise




