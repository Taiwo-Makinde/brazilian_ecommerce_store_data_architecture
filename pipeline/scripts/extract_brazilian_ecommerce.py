# Import Python Standard Packages 
import os
import sys
import json
import subprocess
import importlib

# Import the third party packages 
import pandas as pd

# Import my local customised python package 
from scripts import brazilian_ecommerce_config as config

# Extraction 
# Download Data Set 

def download_brazilian_ecommerce_dataset(config, retries = config.MAX_RETRIES):

    # 1. Check if we already have the files downloaded. 
    # I want to make sure that if the files are already downloaded by the time the pipeline runs, the pipeline does not need to attempt downloading the files

    # Create a function that returns True if all datasets exists in the dataset path, otherwise returns False 
    def all_data_exists (config) -> bool:
        all_exist = True
        for file_path in config.DATASET_PATHS:
            if os.path.exists(file_path):
                print(f"Dataset already exists at : '{file_path}'. Skipping...")
            else:
                print(f"Dataset missing: {file_path}")
                all_exist = False
        return all_exist

    # I call the all_data_exists function to check if all data is present and returns True, that is, complete end this function without continuing the code, and move to the next.
    if all_data_exists(config):
        print("All datasets already exist. Skipping download...")
        return True 


    # 2. Check if Kaggle credentials are available 
    if not config.KAGGLE_USERNAME or not config.KAGGLE_API_TOKEN:
        print(f"Missing kaggle credentials (KAGGLE_USERNAME or KAGGLE_API_TOKEN) in environmental variable file.")
        return False 
    
    # 3. Set Kaggle credentials as environment variables with no file written to the disk
    os.environ["KAGGLE_USERNAME"] = config.KAGGLE_USERNAME
    os.environ["KAGGLE_API_TOKEN"] = config.KAGGLE_API_TOKEN

    # We are using the Kaggle python package to download the files. 
    # 4a. We check if the Kaggle python package is available 
    if importlib.util.find_spec("Kaggle") is None:
        print("Kaggle not found.")

        # 1st Attempt 
        try:
            # The assumption is that Python is already installed so we install Kaggle Python package using pip
            print("Installing Kaggle...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q"])
        except subprocess.CalledProcessError as e:
            print(f"Installastion of kaggle failed: {e}. Proceeding to install without dependencies...")

            # 2nd Attempt 
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q", "--no deps"])
            except subprocess.CalledProcessError as e:
                print(f"Installation without dependencies failed.{e}")
                raise
            else:
                print("Kaggle successfully installed without dependencies.")
        else:
            print("Kaggle fully installed, with all dependencies.")


    # 4b. If Kaggle is found, import kaggle 
    else:
        try:
            import kaggle
        except ImportError:
            print(f"Kaggle package is installed but there is an import error.")
            raise
        else:
            print("Kaggle is installed and the package has been imported into this script successfully.")

    
    # 5. Download with retries
    os.makedirs(config.BRAZILIAN_DATA_DOWNLOAD_PATH, exist_ok = True )
    for attempt in range (1, retries + 1):
        if all_data_exists(config):
                print("All datasets have been successfully downloaded.")
                return True 
        # The above code should only run after all the files ave been downloaded. Hence, it should not run on the first trial. 
        # The above code would complete the loop. 

        try:
            print(f"Attempt {attempt} / {retries} - Downloading {config.DATASET_NAMES}")
            # import kaggle
            import kaggle
            # Authenticate the api
            kaggle.api.authenticate()
            # download the data
            kaggle.api.dataset_download_files (config.BRAZILIAN_ECOMMERCE_DATASET_KAGGLE, path = config.BRAZILIAN_DATA_DOWNLOAD_PATH, unzip = True) # All the datasets would be downloaded as a zip folder and then unzipped. 

        except Exception as e:
            print(f"Attempt {attempt} failed : {type(e).__name__} : {e}")

        # This code only runs if the file has not been downloaded after a given attempt. It informs us of the beginning of another attempt. 
        if not all_data_exists(config):
            print(f"Attempt {attempt} failed. Retrying...")


    # This code only runs after the loop is complete. It also runs if the datasets were not downloaded and 
    if not all_data_exists(config):
        print(f"All attempt to download the file failed.")
        raise FileNotFoundError

    return True


def read_data_frames(config) -> dict[str, pd.Dataframe]:

    # Files do not exist, the code raises an error.
    if not download_brazilian_ecommerce_dataset.all_data_exists(config):
        print("Data is not found All datasets already exist. Skipping download...")
        raise FileNotFoundError

    # File exist, we can start the extraction face 
    print("starting extraction...")
    print(f"Reading datasets...")

    try:
        # Dict 
        brazilian_ecommerce_dataframes_dict = {}                                                              # Empty dictionary which we would append keys and values to later

        brazilian_ecommerce_dataframes_dict ["customer_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_CUSTOMER_DATASET))
        brazilian_ecommerce_dataframes_dict ["geolocation_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_GEOLOCATION_DATASET))
        brazilian_ecommerce_dataframes_dict ["order_items_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_ORDER_ITEMS_DATASET))
        brazilian_ecommerce_dataframes_dict ["order_payments_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_ORDER_PAYMENTS_DATASET))
        brazilian_ecommerce_dataframes_dict ["order_reviews_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_ORDER_REVIEWS_DATASET))
        brazilian_ecommerce_dataframes_dict ["orders_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_ORDERS_DATASET))
        brazilian_ecommerce_dataframes_dict ["products_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_PRODUCTS_DATASET))
        brazilian_ecommerce_dataframes_dict ["sellers_df"] = pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.OLIST_SELLERS_DATASET))
        brazilian_ecommerce_dataframes_dict ["product_category_name_translation_df"] =  pd.read_csv(os.path.join(config.BRAZILIAN_DATA_DOWNLOAD_PATH, config.PRODUCT_CATEGORY_NAME_TRANSLATION))

    except Exception as e:
        print(f"Attempt to read the brazilian eccomerce datasets into a dictionary of dataframes failed: {e}")
        raise
    else:
        print("Brazilian ecommerce datasets succesfully read into brazilian_ecommerce_dataframes_dict.")

    return brazilian_ecommerce_dataframes_dict

# Orchestration Function 
def run_extract_sequence():
    if download_brazilian_ecommerce_dataset():
        brazilian_ecommerce_dataframes_dict = read_data_frames(config)

        if brazilian_ecommerce_dataframes_dict is not None:
            print(f"\nExtraction sequence complete. Datasets are ready for Loading Sequence.")
            return brazilian_ecommerce_dataframes_dict
        else:
            print("\nExtraction failed. brazilian_ecomerce-dataframes_dict is empty")
            raise KeyError                                                                  # Dictionary is empty
    else:
        print("\nDownload failed. Unable to complete extraction step.")
        raise FileNotFoundError

# Script guard
if __name__ == "__main__":
    run_extract_sequence()    



