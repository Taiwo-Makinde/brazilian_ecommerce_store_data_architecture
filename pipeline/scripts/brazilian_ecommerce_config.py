# Import Python standard packages 
import os                                                                 # Python standard package to extract data from .env files 
from pathlib import Path 

# Import Python third-party packages 
from dotenv import load_dotenv                                             # Third party python .env file to load .env file                
from sqlalchemy import create_engine 

# Loading .env file 
env_path = Path(__file__).parents[2] /"config" / "brazilian_ecommerce.env" # Our brazilian .env file is two level directory away from this file
print("env_exists:", env_path.exists())

load_dotenv(env_path)

# We are downloading data from Kaggle so let's load our Kaggle Credentials
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_API_TOKEN = os.getenv("KAGGLE_API_TOKEN")

# Load our credential details about the data on Kaggle and download path 
BRAZILIAN_ECOMMERCE_DATASET_KAGGLE = os.getenv("BRAZILIAN_ECOMMERCE_DATASET_KAGGLE")                                         # Reference to the dataset folder on Kaggle 
BRAZILIAN_DATA_DOWNLOAD_PATH = os.getenv("BRAZILIAN_DATA_DOWNLOAD_PATH")                                                     # Reference to the anticipated download folder path

OLIST_CUSTOMER_DATASET = os.getenv("OLIST_CUSTOMER_DATASET")
OLIST_GEOLOCATION_DATASET = os.getenv("OLIST_GEOLOCATION_DATASET")
OLIST_ORDER_ITEMS_DATASET = os.getenv("OLIST_ORDER_ITEMS_DATASET")
OLIST_ORDER_PAYMENTS_DATASET = os.getenv("OLIST_ORDER_PAYMENTS_DATASET")
OLIST_ORDER_REVIEWS_DATASET = os.getenv("OLIST_ORDER_REVIEWS_DATASET")
OLIST_ORDERS_DATASET = os.getenv("OLIST_ORDERS_DATASET")
OLIST_PRODUCTS_DATASET = os.getenv("OLIST_PRODUCTS_DATASET")
OLIST_SELLERS_DATASET = os.getenv("OLIST_SELLERS_DATASET")
PRODUCT_CATEGORY_NAME_TRANSLATION = os.getenv("PRODUCT_CATEGORY_NAME_TRANSLATION")

# Create a list of Dataset, just as important as the individual list 
raw = os.getenv("DATASET_NAMES")                                            # I read the DATASET_NAMES environment variable into the variable raw

DATASET_NAMES = []                                                          # I create an empty list with the intention to fill this list later

for name in raw.split(","):                                                 # I iterate through the split of the items in raw which is the DATASET_NAMES environment variable 
    name = name.strip()                                                     # I mke sure all named do not have spaces by assigning all cleaned names (spaces removed by .strip method) to name variable
    if name:
        DATASET_NAMES.append(name)                                          # I append the items in name variable as list in DATASET_NAMES

DATASET_PATHS = []

for name in DATASET_NAMES:
    full_path = os.path.join(BRAZILIAN_DATA_DOWNLOAD_PATH, name)
    DATASET_PATHS.append(full_path)

# Configuration for extraction step 
EXTRACT_PATH = BRAZILIAN_DATA_DOWNLOAD_PATH

# Pipeline behavious
MAX_RETRIES = 4 
TIMEOUT_SECONDS = 120
FILE_DOWNLOAD_FORMAT = "csv"

# Database Credentials 

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

brazilian_ecommerce_engine = create_engine(f"postgresql+psycopg2://{DB_USER}: {DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")






