import pandas as pd
import numpy as np
import re

def transform_product(df):
    df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce").fillna(0)
    df["no_of_ratings"] = pd.to_numeric(
        df["no_of_ratings"].replace({"GET":0,"FREE Delivery by Amazon":0}),
        errors="coerce"
    ).fillna(0)

    def split_currency(val):
        if pd.isna(val): return (np.nan,np.nan)
        m = re.match(r"([^\d]+)([\d.,]+)", str(val))
        return (m.group(1).strip() if m else np.nan,
                float(m.group(2).replace(",","")) if m else np.nan)
    
    df[["type_currency","actual_price"]] = df["actual_price"].apply(lambda x: pd.Series(split_currency(x)))
    _, df["discount_price"] = zip(*df["discount_price"].apply(split_currency))

    df["discount_price"] = df.apply(
        lambda x: x["actual_price"] if pd.isna(x["discount_price"]) else x["discount_price"], axis=1
    )
    df["actual_price"] = df.apply(
        lambda x: x["discount_price"] if pd.isna(x["actual_price"]) else x["actual_price"], axis=1
    )

    df.dropna(subset=["actual_price","discount_price"], how="all", inplace=True)

    df["discount_percentage"] = ((df["actual_price"] - df["discount_price"]) / df["actual_price"] * 100).round(2).fillna(0)
    df["potential_revenue"] = df["discount_price"] * df["no_of_ratings"]
    df["potential_loss_from_discount"] = (df["actual_price"] - df["discount_price"]) * df["no_of_ratings"]

    # Hapus duplikat berdasarkan nama produk
    df.drop_duplicates(subset=["name"], keep="first", inplace=True)

    return df

def demographi(df):
    report = {}

    # Teknis
    report["Basic_Info"] = pd.DataFrame({
        "Metric": [
            "Total Rows", "Total Columns", "Missing Values",
            "Duplicate Rows", "Memory Usage (KB)"
        ],
        "Value": [
            len(df),
            df.shape[1],
            df.isnull().sum().sum(),
            df.duplicated().sum(),
            round(df.memory_usage().sum() / 1024, 2)
        ]
    })

    # Data type counts
    dtype_counts = df.dtypes.value_counts().reset_index()
    dtype_counts.columns = ["Dtype", "Count"]
    report["Data_Types"] = dtype_counts

    # Descriptive stats untuk numeric
    num_desc = df.describe().T.reset_index()
    num_desc.rename(columns={"index":"Column"}, inplace=True)
    report["Numeric_Stats"] = num_desc

    # Missing values detail
    miss = df.isnull().sum().reset_index()
    miss.columns = ["Column", "Missing_Count"]
    report["Missing_By_Column"] = miss

    # Bisnis
    biz = {
        "Avg Price": df["actual_price"].mean(),
        "Median Price": df["actual_price"].median(),
        "Avg Discount %": df["discount_percentage"].mean(),
        "Total Potential Revenue": df["potential_revenue"].sum(),
        "Total Potential Loss (Discount)": df["potential_loss_from_discount"].sum(),
    }
    report["Business_Summary"] = pd.DataFrame(list(biz.items()), columns=["Metric","Value"])

    # Produk dengan diskon tertinggi
    max_disc = df.loc[df["discount_percentage"].idxmax()]
    report["Max_Discount_Product"] = pd.DataFrame({
        "Name":[max_disc["name"]],
        "Discount%":[max_disc["discount_percentage"]],
        "Price":[max_disc["actual_price"]]
    })

    # Produk paling banyak terjual
    best = df.loc[df["no_of_ratings"].idxmax()]
    report["Best_Selling"] = pd.DataFrame({
        "Name":[best["name"]],
        "Ratings":[best["no_of_ratings"]],
        "Avg_Rating":[best["ratings"]]
    })

    # Top 5 revenue
    report["Top5_Revenue"] = df.nlargest(5,"potential_revenue")[["name","potential_revenue"]]

    # Distribusi harga (binning)
    report["Price_Distribution"] = pd.cut(df["actual_price"], bins=5).value_counts().reset_index()
    report["Price_Distribution"].columns = ["Price_Range","Count"]

    return report