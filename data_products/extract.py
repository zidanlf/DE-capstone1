import pandas as pd

def extract_product(PATH_FILE_PRODUCT):
    return pd.read_csv(PATH_FILE_PRODUCT, index_col=False)