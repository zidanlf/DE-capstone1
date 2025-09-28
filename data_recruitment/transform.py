import pandas as pd
import re
import numpy as np

pd.set_option('future.no_silent_downcasting', True)

def transform(df):
    # 0. Hapus kolom "Unnamed: 0" kalau ada
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # 1. Bersihkan kolom company (hapus angka di belakang nama)
    df["company"] = df["company"].str.replace(r"\s*\d+(\.\d+)?$", "", regex=True).str.strip()
    df = df[df["company"].notna() & (df["company"].str.strip() != "")]

    # 2. company_rating → NaN jadi 0, ubah ke float
    df["company_rating"] = pd.to_numeric(df["company_rating"], errors="coerce").fillna(0.0)

    # 3. Parsing job_description
    def parse_description(desc):
        if pd.isna(desc):
            return pd.Series([None, None, None, None])

        # --- Skills (tambahkan lebih banyak skills dan case-insensitive matching)
        skills_keywords = [
            "Python", "SQL", "Spark", "Snowflake", "AWS", "Java", "JavaScript", "Scala",
            "Tableau", "ETL", "Talend", "Informatica", "BigQuery", "PowerBI", "Looker",
            "Redshift", "DBT", "Airflow", "HIVE", "Azure", "GCP", "Docker", "Kubernetes",
            "Kafka", "MongoDB", "PostgreSQL", "MySQL", "Oracle", "Cassandra", "Redis",
            "Terraform", "Jenkins", "Git", "Linux", "Hadoop", "Pandas", "NumPy",
            "TensorFlow", "PyTorch", "Scikit-learn", "R", "SAS", "SPSS", "Excel"
        ]
        
        # Improved skills detection - avoid partial matches
        skills = []
        for skill in skills_keywords:
            if re.search(rf"\b{re.escape(skill)}\b", desc, re.IGNORECASE):
                skills.append(skill)

        # --- Experience level (perbaiki regex untuk lebih akurat)
        level_patterns = {
            "Entry": r"\b(entry|0[-\s]?to[-\s]?2\s+years?|under\s+1\s+year|junior|fresher|0[-\s]?2\s+years?)\b",
            "Mid": r"\b(mid|3[-\s]?to[-\s]?5\s+years?|intermediate|3[-\s]?5\s+years?)\b", 
            "Senior": r"\b(senior|lead|6\+?\s+years?|8\+?\s+years?|manager|principal|staff|architect)\b"
        }
        
        level = "Not Specified"  # Default value instead of None
        for lvl, pattern in level_patterns.items():
            if re.search(pattern, desc, re.IGNORECASE):
                level = lvl
                break

        # --- Job type (improved detection)
        job_types = []
        if re.search(r"\bfull[-\s]?time\b", desc, re.IGNORECASE):
            job_types.append("Full-time")
        if re.search(r"\bpart[-\s]?time\b", desc, re.IGNORECASE):
            job_types.append("Part-time")
        if re.search(r"\bcontract\b", desc, re.IGNORECASE):
            job_types.append("Contract")
        if re.search(r"\bintern(ship)?\b", desc, re.IGNORECASE):
            job_types.append("Internship")
        if re.search(r"\bremote\b", desc, re.IGNORECASE):
            job_types.append("Remote")
        if re.search(r"\bhybrid\b", desc, re.IGNORECASE):
            job_types.append("Hybrid")
            
        job_type = ", ".join(job_types) if job_types else "Not Specified"

        # --- Benefits
        benefits_keywords = {
            "insurance": ["insurance", "medical", "dental", "vision", "health"],
            "bonus": ["bonus", "incentive", "commission"],
            "retirement": ["retirement", "401k", "pension"],
            "stock": ["stock", "equity", "shares", "rsu"],
            "assistance": ["assistance", "support", "help"],
            "development": ["development", "training", "education", "learning"],
            "vacation": ["vacation", "pto", "paid time off", "leave"],
            "flexible": ["flexible", "work from home", "wfh"]
        }
        
        benefits = []
        for benefit_type, keywords in benefits_keywords.items():
            for keyword in keywords:
                if re.search(rf"\b{re.escape(keyword)}\b", desc, re.IGNORECASE):
                    benefits.append(benefit_type.capitalize())
                    break  

        return pd.Series([
            ", ".join(skills) if skills else "Not Specified",
            level,
            job_type,
            ", ".join(benefits) if benefits else "Not Specified"
        ])

    df[["skills", "experience_level", "job_type", "benefits"]] = df["job_description"].apply(parse_description)

    # 4. Parsing salary_estimate → float + unit + currency
    def parse_salary(s):
        if pd.isna(s):
            return pd.Series([0.0, "-", "-"])
        match = re.search(r"([\d,\.]+)", s)
        salary = float(match.group(1).replace(",", "")) if match else 0.0
        unit = "per year" if "yr" in s else "per hour" if "hr" in s else "-"
        currency = "$" if "$" in s else "-"
        return pd.Series([salary, unit, currency])

    df[["salary_estimate", "salary_unit", "currency"]] = df["salary_estimate"].apply(parse_salary)

    # 4b. Imputasi salary_estimate yang bernilai 0

    def fill_salary(row):
        if row["salary_estimate"] > 0:
            return row["salary_estimate"]

        mask = (
            (df["company"] == row["company"]) &
            (df["job_title"] == row["job_title"]) &
            (df["experience_level"] == row["experience_level"]) &
            (df["salary_estimate"] > 0)
        )
        if mask.any():
            return df.loc[mask, "salary_estimate"].median()

    df["salary_estimate"] = df.apply(fill_salary, axis=1)

    # 5-8. Improved missing values handling
    for col in ["company_size", "company_type", "company_sector", "company_industry"]:
        # First try to fill within same company
        df[col] = df.groupby("company")[col].transform(lambda x: x.ffill().bfill())
        
        # Then fill remaining NaN with "-"
        df[col] = df[col].fillna("-")
        
        # Handle empty strings
        df[col] = df[col].replace("", "-")

    # 9. Company founded → isi 0 kalau kosong, ubah ke int
    df["company_founded"] = pd.to_numeric(df["company_founded"], errors="coerce").fillna(0).astype(int)

    # 10. Company revenue → isi "-" kalau kosong
    df["company_revenue"] = df["company_revenue"].fillna("-").replace("", "-")

    # 11. Improved date formatting
    df["dates"] = pd.to_datetime(df["dates"], errors="coerce", utc=True)
    df["dates"] = df["dates"].dt.strftime("%Y-%m-%d")

    # Drop original job_description
    if "job_description" in df.columns:
        df = df.drop(columns=["job_description"])

    return df

def demographi(df):
    report = {}

    # === TEKNIS ===
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

    # Descriptive stats untuk numeric (kecuali salary_estimate)
    num_cols = [c for c in df.select_dtypes(include=["int64","float64"]).columns if c != "salary_estimate"]
    if num_cols:
        num_desc = df[num_cols].describe().T.reset_index()
        num_desc.rename(columns={"index": "Column"}, inplace=True)
        report["Numeric_Stats"] = num_desc

    # Descriptive stats salary dipisah berdasarkan unit
    salary_stats = {}
    for unit in df["salary_unit"].unique():
        if unit != "-":
            sub = df[df["salary_unit"] == unit]["salary_estimate"]
            if not sub.empty:
                desc = sub.describe().reset_index()
                desc.columns = ["Stat", "Value"]
                salary_stats[unit] = desc
    report["Salary_Stats_By_Unit"] = salary_stats

    # Missing values detail
    miss = df.isnull().sum().reset_index()
    miss.columns = ["Column", "Missing_Count"]
    report["Missing_By_Column"] = miss

    # === BISNIS / DEMOGRAFI ===
    biz = {
        "Avg Company Rating": df["company_rating"].mean(),
        "Median Company Rating": df["company_rating"].median(),
        "Earliest Founded": df["company_founded"].min(),
        "Latest Founded": df["company_founded"].max(),
    }

    # Salary summary per unit
    salary_summary = []
    for unit in df["salary_unit"].unique():
        if unit != "-":
            sub = df[df["salary_unit"] == unit]
            salary_summary.append([f"Median Salary ({unit})", sub["salary_estimate"].median()])
            salary_summary.append([f"Average Salary ({unit})", sub["salary_estimate"].mean()])

    biz_df = pd.DataFrame(list(biz.items()), columns=["Metric","Value"])
    salary_df = pd.DataFrame(salary_summary, columns=["Metric","Value"])
    report["Business_Summary"] = pd.concat([biz_df, salary_df], ignore_index=True)

    # Top Skills
    skills_series = df["skills"].dropna().str.split(", ")
    all_skills = skills_series.explode().value_counts().reset_index()
    all_skills.columns = ["Skill","Count"]
    report["Top_Skills"] = all_skills.head(10)

    # Distribusi Experience Level
    exp_dist = df["experience_level"].value_counts().reset_index()
    exp_dist.columns = ["Experience_Level","Count"]
    report["Experience_Distribution"] = exp_dist

    # Distribusi Job Type
    jobtype_series = df["job_type"].dropna().str.split(", ")
    job_dist = jobtype_series.explode().value_counts().reset_index()
    job_dist.columns = ["Job_Type","Count"]
    report["JobType_Distribution"] = job_dist

    # Top Companies dengan lowongan terbanyak
    top_companies = df["company"].value_counts().head(10).reset_index()
    top_companies.columns = ["Company","Job_Postings"]
    report["Top_Companies"] = top_companies

    # Distribusi Salary (binning per unit)
    salary_dist_list = {}
    for unit in df["salary_unit"].unique():
        if unit != "-":
            sub = df[df["salary_unit"] == unit]
            if sub["salary_estimate"].notna().any():
                salary_dist = pd.cut(sub["salary_estimate"], bins=5).value_counts().reset_index()
                salary_dist.columns = ["Salary_Range","Count"]
                salary_dist_list[unit] = salary_dist
    report["Salary_Distribution"] = salary_dist_list

    return report