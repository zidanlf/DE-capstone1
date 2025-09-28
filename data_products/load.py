# import pandas as pd
# import os

# def load_product(df, filename="All Exercise and Fitness.csv"):
#     output_path = f"cleaned_data/{filename}"
#     df.to_csv(output_path, index=False)
#     print(f"Data saved to: {output_path}")
    
#     return output_path

import pandas as pd
import os

def load_product(df, demographi_report, filename):
    os.makedirs("cleaned_data", exist_ok=True)
    path = f"cleaned_data/{filename}.xlsx"

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet utama
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)

        # Sheet demographi
        if isinstance(demographi_report, dict):
            for sheet, data in demographi_report.items():
                if isinstance(data, pd.DataFrame):
                    data.to_excel(writer, sheet_name=sheet[:31], index=False)
                elif isinstance(data, dict):
                    pd.DataFrame(list(data.items()), columns=["Metric", "Value"]) \
                        .to_excel(writer, sheet_name=sheet[:31], index=False)
                else:
                    pd.DataFrame([data], columns=["Value"]) \
                        .to_excel(writer, sheet_name=sheet[:31], index=False)
        else:
            pd.DataFrame(demographi_report.split("\n"), columns=["Demographi"]) \
                .to_excel(writer, sheet_name="Demographi", index=False)

    print(f"Saved to {path}")
