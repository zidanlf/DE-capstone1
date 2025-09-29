import pandas as pd
import re
import numpy as np

pd.set_option('future.no_silent_downcasting', True)

def transform(df):
    """
    Transform recruitment data.
    Philosophy: Keep NaN for truly missing data to preserve data integrity.
    Only fill with meaningful defaults where it makes business sense.
    """
    
    # 0. Hapus kolom "Unnamed: 0" kalau ada
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # 1. Bersihkan kolom company (hapus angka di belakang nama)
    df["company"] = df["company"].str.replace(r"\s*\d+(\.\d+)?$", "", regex=True).str.strip()
    df = df[df["company"].notna() & (df["company"].str.strip() != "")]

    # 2. company_rating → Keep NaN for missing ratings
    # Note: NaN means "not rated yet" which is different from rating of 0
    df["company_rating"] = pd.to_numeric(df["company_rating"], errors="coerce")

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
        
        level = None  # Keep as None instead of "Not Specified"
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
            
        job_type = ", ".join(job_types) if job_types else None

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
            ", ".join(skills) if skills else None,
            level,
            job_type,
            ", ".join(benefits) if benefits else None
        ])

    df[["skills", "experience_level", "job_type", "benefits"]] = df["job_description"].apply(parse_description)

    # 4. Parsing salary_estimate → float + unit + currency
    def parse_salary(s):
        if pd.isna(s):
            return pd.Series([np.nan, None, None])
        match = re.search(r"([\d,\.]+)", s)
        salary = float(match.group(1).replace(",", "")) if match else np.nan
        unit = "per year" if "yr" in s else "per hour" if "hr" in s else None
        currency = "$" if "$" in s else None
        return pd.Series([salary, unit, currency])

    df[["salary_estimate", "salary_unit", "currency"]] = df["salary_estimate"].apply(parse_salary)

    # 4b. Imputasi salary_estimate yang bernilai NaN
    # Note: Only impute if we have similar jobs with known salaries
    def fill_salary(row):
        if pd.notna(row["salary_estimate"]) and row["salary_estimate"] > 0:
            return row["salary_estimate"]

        mask = (
            (df["company"] == row["company"]) &
            (df["job_title"] == row["job_title"]) &
            (df["experience_level"] == row["experience_level"]) &
            (df["salary_estimate"].notna()) &
            (df["salary_estimate"] > 0)
        )
        if mask.any():
            return df.loc[mask, "salary_estimate"].median()
        
        # If no match found, keep as NaN (don't force to 0)
        return np.nan

    df["salary_estimate"] = df.apply(fill_salary, axis=1)

    # 5-8. Keep NaN for missing categorical data
    # Note: NaN is more honest than "-" for missing data
    # Let downstream systems decide how to handle missing values
    for col in ["company_size", "company_type", "company_sector", "company_industry"]:
        # Try to fill within same company first
        df[col] = df.groupby("company")[col].transform(lambda x: x.ffill().bfill())
        # Keep remaining as NaN (don't fill with "-")

    # 9. Company founded → Keep as nullable integer (Int64)
    # Note: NaN means "founding year unknown", which is different from year 0 or -1
    df["company_founded"] = pd.to_numeric(df["company_founded"], errors="coerce").astype("Int64")

    # 10. Company revenue → Keep NaN for missing
    # Note: NaN is clearer than "-" for data pipelines
    df["company_revenue"] = df["company_revenue"].replace("", np.nan)

    # 11. Improved date formatting
    df["dates"] = pd.to_datetime(df["dates"], errors="coerce", utc=True)
    df["dates"] = df["dates"].dt.strftime("%Y-%m-%d")

    # Drop original job_description
    if "job_description" in df.columns:
        df = df.drop(columns=["job_description"])

    return df

def demographi(df):
    """
    Generate demographic report.
    Handles NaN values appropriately in statistics.
    """
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
    # Use dropna() in calculations to exclude NaN properly
    num_cols = [c for c in df.select_dtypes(include=["int64","float64","Int64"]).columns 
                if c != "salary_estimate"]
    if num_cols:
        num_desc = df[num_cols].describe().T.reset_index()
        num_desc.rename(columns={"index": "Column"}, inplace=True)
        report["Numeric_Stats"] = num_desc

    # Descriptive stats salary dipisah berdasarkan unit
    salary_stats = {}
    for unit in df["salary_unit"].dropna().unique():
        sub = df[df["salary_unit"] == unit]["salary_estimate"].dropna()
        if not sub.empty:
            desc = sub.describe().reset_index()
            desc.columns = ["Stat", "Value"]
            salary_stats[unit] = desc
    if salary_stats:
        report["Salary_Stats_By_Unit"] = salary_stats

    # Missing values detail
    miss = df.isnull().sum().reset_index()
    miss.columns = ["Column", "Missing_Count"]
    report["Missing_By_Column"] = miss

    # === BISNIS / DEMOGRAFI ===
    biz = {}
    
    # Company rating stats (skip NaN)
    if df["company_rating"].notna().any():
        biz["Avg Company Rating"] = df["company_rating"].mean()
        biz["Median Company Rating"] = df["company_rating"].median()
    
    # Company founded stats (skip NaN)
    founded_valid = df["company_founded"].dropna()
    if not founded_valid.empty:
        biz["Earliest Founded"] = int(founded_valid.min())
        biz["Latest Founded"] = int(founded_valid.max())

    # Salary summary per unit
    salary_summary = []
    for unit in df["salary_unit"].dropna().unique():
        sub = df[df["salary_unit"] == unit]["salary_estimate"].dropna()
        if not sub.empty:
            salary_summary.append([f"Median Salary ({unit})", sub.median()])
            salary_summary.append([f"Average Salary ({unit})", sub.mean()])

    biz_df = pd.DataFrame(list(biz.items()), columns=["Metric","Value"])
    if salary_summary:
        salary_df = pd.DataFrame(salary_summary, columns=["Metric","Value"])
        report["Business_Summary"] = pd.concat([biz_df, salary_df], ignore_index=True)
    else:
        report["Business_Summary"] = biz_df

    # Top Skills (skip NaN)
    skills_series = df["skills"].dropna().str.split(", ")
    if not skills_series.empty:
        all_skills = skills_series.explode().value_counts().reset_index()
        all_skills.columns = ["Skill","Count"]
        report["Top_Skills"] = all_skills.head(10)

    # Distribusi Experience Level (skip NaN)
    exp_dist = df["experience_level"].value_counts(dropna=False).reset_index()
    exp_dist.columns = ["Experience_Level","Count"]
    report["Experience_Distribution"] = exp_dist

    # Distribusi Job Type (skip NaN)
    jobtype_series = df["job_type"].dropna().str.split(", ")
    if not jobtype_series.empty:
        job_dist = jobtype_series.explode().value_counts().reset_index()
        job_dist.columns = ["Job_Type","Count"]
        report["JobType_Distribution"] = job_dist

    # Top Companies dengan lowongan terbanyak
    top_companies = df["company"].value_counts().head(10).reset_index()
    top_companies.columns = ["Company","Job_Postings"]
    report["Top_Companies"] = top_companies

    # Distribusi Salary (binning per unit, skip NaN)
    salary_dist_list = {}
    for unit in df["salary_unit"].dropna().unique():
        sub = df[df["salary_unit"] == unit]["salary_estimate"].dropna()
        if len(sub) > 0:
            salary_dist = pd.cut(sub, bins=5).value_counts().reset_index()
            salary_dist.columns = ["Salary_Range","Count"]
            salary_dist_list[unit] = salary_dist
    if salary_dist_list:
        report["Salary_Distribution"] = salary_dist_list

    return report