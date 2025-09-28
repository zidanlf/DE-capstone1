import pandas as pd
import os

def load(df, demographi_report, filename):
    os.makedirs("cleaned_data", exist_ok=True)
    path = f"cleaned_data/{filename}.xlsx"

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet utama: data hasil transformasi
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)

        # Sheet demographi
        if isinstance(demographi_report, dict):
            for sheet, data in demographi_report.items():
                # Kalau data berupa DataFrame → langsung simpan
                if isinstance(data, pd.DataFrame):
                    data.to_excel(writer, sheet_name=sheet[:31], index=False)

                # Kalau data berupa dict (contoh Salary_Distribution per unit)
                elif isinstance(data, dict):
                    for subkey, subdata in data.items():
                        sub_sheet = f"{sheet}_{subkey}"[:31]  # max 31 karakter
                        if isinstance(subdata, pd.DataFrame):
                            subdata.to_excel(writer, sheet_name=sub_sheet, index=False)
                        else:
                            pd.DataFrame([subdata], columns=["Value"]) \
                                .to_excel(writer, sheet_name=sub_sheet, index=False)

                # Kalau bukan DataFrame/dict → simpan jadi DataFrame biasa
                else:
                    pd.DataFrame([data], columns=["Value"]) \
                        .to_excel(writer, sheet_name=sheet[:31], index=False)

        else:
            pd.DataFrame(demographi_report.split("\n"), columns=["Demographi"]) \
                .to_excel(writer, sheet_name="Demographi", index=False)

    print(f"[INFO] Saved to {path}")