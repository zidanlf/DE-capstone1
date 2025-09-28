import pandas as pd
import os

def inspect_data(df, filename="inspect_data_recruitment.txt"):
    filepath = os.path.join("cleaned_data", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=== INFO ===\n")
        df.info(buf=f)

        f.write("\n\n=== HEAD ===\n")
        f.write(df.head().to_string())

        f.write("\n\n=== DESCRIBE ===\n")
        f.write(df.describe(include="all").to_string())

        f.write("\n\n=== NULL VALUES ===\n")
        f.write(df.isnull().sum().to_string())

        f.write("\n\n=== DUPLICATES ===\n")
        f.write(str(df.duplicated().sum()))

    print(f"Inspect data saved to: {filepath}")
