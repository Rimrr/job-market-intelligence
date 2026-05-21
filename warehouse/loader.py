import ast
import subprocess
import pandas as pd
from urllib.parse import urljoin
import math

def to_sql_int(val):
    if val is None:
        return "NULL"
    try:
        if math.isnan(float(val)):
            return "NULL"
        return str(int(val))
    except (TypeError, ValueError):
        return "NULL"

def run_sql(sql: str, params: dict = None) -> list:
    """Exécute SQL via docker exec — version corrigée"""

    if params:
        for key, val in params.items():
            if val is None:
                sql = sql.replace(f":{key}", "NULL")
            elif isinstance(val, str):
                val_escaped = val.replace("'", "''")
                sql = sql.replace(f":{key}", f"'{val_escaped}'")
            else:
                sql = sql.replace(f":{key}", str(val))

    cmd = [
        "docker", "exec",
        "job_market_intelligence-postgres-1",
        "psql",
        "-U", "jobuser",
        "-d", "jobmarket",
        "-t",
        "-A",
        "-c", sql
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        raise Exception(result.stderr.strip())

    # nettoyage INSERT 0 0
    lines = []
    for l in result.stdout.strip().split("\n"):
        l = l.strip()
        if l and not l.startswith("INSERT"):
            lines.append(l)

    return lines


def load_to_warehouse(df_silver: pd.DataFrame, gold: dict):
    loaded = 0

    for _, row in df_silver.iterrows():
        try:
            # ---------------- BASIC FIELDS ----------------
            title    = str(row.get("title", "N/A")).replace("'", "''")
            company  = str(row.get("company", "N/A")).replace("'", "''")
            location = str(row.get("location", "N/A")).replace("'", "''")
            language = str(row.get("language", "unknown"))
            source   = str(row.get("source", "unknown"))

            # ---------------- URL FIX ----------------
            raw_url = str(row.get("url", "")).strip()

            if raw_url.startswith("http"):
                url = raw_url
            else:
                url = urljoin("https://www.rekrute.com", raw_url)

            url = url.split("?")[0]
            url = url.replace("'", "''")

            pub_at = str(row.get("published_at", ""))

            sal_min = row.get("salary_min")
            sal_max = row.get("salary_max")

            sal_min_sql = "NULL" if (sal_min is None or (isinstance(sal_min, float) and math.isnan(sal_min))) else str(int(sal_min))
            sal_max_sql = "NULL" if (sal_max is None or (isinstance(sal_max, float) and math.isnan(sal_max))) else str(int(sal_max))

            # ---------------- UPSERT (IMPORTANT FIX) ----------------
            sql = f"""
                INSERT INTO fact_job_offers
                    (title, company, location, salary_min, salary_max,
                     language, source, url, published_at)
                VALUES
                    ('{title}','{company}','{location}',
                     {sal_min_sql},{sal_max_sql},
                     '{language}','{source}','{url}','{pub_at}')
                ON CONFLICT (url) DO UPDATE SET
                    title        = EXCLUDED.title,
                    company      = EXCLUDED.company,
                    location     = EXCLUDED.location,
                    salary_min   = EXCLUDED.salary_min,
                    salary_max   = EXCLUDED.salary_max,
                    published_at = EXCLUDED.published_at
                RETURNING id
            """

            rows = run_sql(sql)

            offer_id = rows[0].strip()
            loaded += 1

            # ---------------- SKILLS ----------------
            skills = row.get("skills", [])

            if isinstance(skills, str):
                try:
                    skills = ast.literal_eval(skills)
                except Exception:
                    skills = []

            for skill in skills:
                skill_clean = str(skill).replace("'", "''")

                run_sql(f"""
                    INSERT INTO dim_skills (name)
                    VALUES ('{skill_clean}')
                    ON CONFLICT (name) DO NOTHING
                """)

                skill_rows = run_sql(f"""
                    SELECT id FROM dim_skills
                    WHERE name = '{skill_clean}'
                """)

                if skill_rows:
                    skill_id = skill_rows[0].strip()

                    run_sql(f"""
                        INSERT INTO offer_skills (offer_id, skill_id)
                        VALUES ({offer_id}, {skill_id})
                        ON CONFLICT DO NOTHING
                    """)

        except Exception as e:
            print(f"[Warehouse] Erreur ligne: {e}")
            continue

    print(f"✅ Warehouse: {loaded} offres traitées (insert + update)")