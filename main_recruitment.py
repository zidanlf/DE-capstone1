from config.config import PATH_FILE_RECRUITMENT
from data_recruitment.extract import extract_recruitment
from data_recruitment.data_profiling import inspect_data
from data_recruitment.transform import transform, demographi
from data_recruitment.load import load

if __name__ == "__main__":
    df = extract_recruitment(PATH_FILE_RECRUITMENT)
    inspect_data(df)
    df = transform(df)
    df_demo = demographi(df)
    load(df, demographi_report=df_demo, filename="data_requirements")