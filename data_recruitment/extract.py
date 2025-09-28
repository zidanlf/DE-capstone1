import pandas as pd

def extract_recruitment(PATH_FILE_RECRUITMENT):
    return pd.read_csv(PATH_FILE_RECRUITMENT, index_col=False)