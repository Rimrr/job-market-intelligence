import pandas as pd


def build_gold_tables(df: pd.DataFrame) -> dict:


    # ---------------- TOP SKILLS ----------------
    skills_exploded = df.explode("skills").dropna(subset=["skills"])
    top_skills = (
        skills_exploded.groupby("skills")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(20)
    )

    # ---------------- OFFERS BY CITY ----------------
    offers_by_city = (
        df.groupby("location")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(20)
    )

    # ---------------- SALARY BY CITY (FIXED VERSION) ----------------
    df_salary = (
    df[df["salary_min"].notna()]
    .copy()
    .assign(location=lambda x: x["location"].str.strip().str.title())
    .groupby("location")
    .agg(
        salary_min=("salary_min", "mean"),
        salary_max=("salary_max", "mean"),
        nb_offres=("salary_min", "count")
    )
    .reset_index()
    .round(0)
    .sort_values("nb_offres", ascending=False)
    ) 
    # ---------------- OFFERS BY SOURCE ----------------
    offers_by_source = (
        df.groupby("source")
        .size()
        .reset_index(name="count")
    )

    # ---------------- OFFERS OVER TIME ----------------
    df["date"] = pd.to_datetime(df["published_at"], errors="coerce").dt.date

    offers_over_time = (
        df.groupby(["date", "source"])
        .size()
        .reset_index(name="count")
        .sort_values("date")
    )

    # ---------------- GOLD DICTIONARY ----------------
    gold = {
        "top_skills": top_skills,
        "offers_by_city": offers_by_city,
        "salary_by_city": df_salary,
        "offers_by_source": offers_by_source,
        "offers_over_time": offers_over_time
    }

    # ---------------- LOG OUTPUT ----------------
    for name, table in gold.items():
        print(f"🥇 Gold [{name}]: {len(table)} lignes")

    return gold