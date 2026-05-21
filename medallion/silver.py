# Silver : nettoyage, normalisation, détection langue
import re
import pandas as pd
from langdetect import detect, LangDetectException

# ──────────────────────────────────────────────
# Table de référence salaires Maroc (MAD/mois)
# ──────────────────────────────────────────────
SALARY_REFERENCE = {
    "data engineer":         (15000, 35000),
    "data scientist":        (18000, 40000),
    "data analyst":          (12000, 28000),
    "business intelligence": (12000, 25000),
    "machine learning":      (18000, 42000),
    "nlp":                   (18000, 40000),
    "computer vision":       (18000, 40000),
    "devops":                (15000, 35000),
    "cloud":                 (15000, 35000),
    "software engineer":     (12000, 30000),
    "fullstack":             (10000, 28000),
    "backend":               (10000, 25000),
    "frontend":              (8000,  22000),
    "mobile":                (10000, 25000),
    "flutter":               (10000, 25000),
    "react":                 (10000, 25000),
    "product manager":       (15000, 35000),
    "scrum master":          (14000, 30000),
    "chef de projet":        (12000, 28000),
    "consultant":            (12000, 30000),
    "architect":             (20000, 50000),
    "lead":                  (18000, 40000),
    "senior":                (18000, 40000),
    "junior":                (6000,  15000),
    "stagiaire":             (2000,   6000),
    "stage":                 (2000,   6000),
}

SKILLS_LIST = [
    "python", "sql", "java", "spark", "kafka", "airflow",
    "docker", "kubernetes", "react", "javascript", "aws",
    "azure", "machine learning", "deep learning", "dbt",
    "power bi", "tableau", "scala", "tensorflow", "mongodb",
    "excel", "hadoop", "linux", "git", "devops", "django",
    "fastapi", "node.js", "flutter", "php", "laravel",
    "data engineer", "data scientist", "data analyst",
    "business intelligence", "etl", "nlp", "computer vision"
]


def estimate_salary_from_title(title: str, description: str = "") -> tuple:
    text = (title + " " + description).lower()
    for keyword, (s_min, s_max) in SALARY_REFERENCE.items():
        if keyword in text:
            return s_min, s_max
    return None, None                                          # ← bug 2 corrigé


def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return text.strip().title()


def detect_language(text: str) -> str:
    try:
        return detect(text) if len(text) > 30 else "unknown"
    except LangDetectException:
        return "unknown"


def extract_skills(description: str, title: str = "") -> list:
    text = (description + " " + title).lower()
    return [s for s in SKILLS_LIST if s in text]


def transform_to_silver(offers_raw: list) -> pd.DataFrame:

    df = pd.DataFrame(offers_raw)

    # ---------------- REMOVE DUPLICATES ----------------
    df = df.drop_duplicates(subset=["url"])

    # ---------------- CLEAN TEXT ----------------
    df["description"] = df["description"].apply(clean_html)
    df["title"] = df["title"].apply(normalize_text)
    df["company"] = df["company"].apply(normalize_text)
    df["location"] = df["location"].fillna("").str.strip()

    # ---------------- LANGUAGE ----------------
    df["language"] = df["description"].apply(detect_language)

    # ---------------- SKILLS ----------------
    df["skills"] = df.apply(
        lambda row: extract_skills(row["description"], row["title"]),
        axis=1
    )

    # ---------------- SALARY ----------------
    salary_parsed = df.apply(
        lambda row: estimate_salary_from_title(
            str(row.get("title", "") or ""),
            str(row.get("description", "") or "")
        ),
        axis=1
    )
    df["salary_min"] = [s[0] for s in salary_parsed]
    df["salary_max"] = [s[1] for s in salary_parsed]

    # ---------------- FINAL CLEANING ----------------      ← bug 1 corrigé
    df = df.dropna(subset=["title", "url"])
    df = df[df["title"].str.len() >= 3]

    print(f"✅ Silver: {len(df)} offres après nettoyage")

    return df                                               # ← return à la fin