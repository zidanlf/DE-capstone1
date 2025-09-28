from config.config import PATH_FILE_PRODUCTS
from data_products.extract import extract_product
from data_products.transform import transform_product, demographi
from data_products.load import load_product
from data_products.data_profiling import inspect_data

if __name__ == "__main__":
    df = extract_product(PATH_FILE_PRODUCTS)
    inspect_data(df)
    df = transform_product(df)
    df_demo = demographi(df)
    load_product(df, demographi_report=df_demo, filename="All Exercise and Fitness")