# quality/expectations.py

import pandas as pd
import json
from datetime import datetime


def run_quality_checks(df: pd.DataFrame = None) -> dict:

    # =========================
    # CHARGEMENT DES DONNÉES
    # =========================
    if df is None:
        from datalake.minio_client import read_all_bronze
        from medallion.silver import transform_to_silver

        df = transform_to_silver(read_all_bronze())

    # =========================
    # CORRECTION DES URLS
    # =========================
    BASE_URL = "https://www.rekrute.com"

    df["url"] = df["url"].apply(
        lambda x: BASE_URL + x
        if pd.notna(x) and str(x).startswith("/")
        else x
    )

    # =========================
    # VARIABLES
    # =========================
    results = {}
    errors = []

    # =========================
    # 1. COMPLETUDE
    # =========================
    missing_title = df["title"].isna().sum()
    missing_url = df["url"].isna().sum()
    missing_date = df["published_at"].isna().sum()

    results["completeness_title"] = missing_title == 0
    results["completeness_url"] = missing_url == 0
    results["completeness_date"] = missing_date == 0

    if missing_title > 0:
        errors.append(f"⚠️ {missing_title} offres sans titre")

    if missing_url > 0:
        errors.append(f"⚠️ {missing_url} offres sans URL")

    if missing_date > 0:
        errors.append(f"⚠️ {missing_date} offres sans date")

    # =========================
    # 2. VALIDITE
    # =========================
    short_titles = (df["title"].fillna("").str.len() < 3).sum()

    invalid_urls = (
        ~df["url"].fillna("").str.startswith("http")
    ).sum()

    invalid_salary = (
        df["salary_min"].notna()
        & (df["salary_min"] < 0)
    ).sum()

    results["validity_title_length"] = short_titles == 0
    results["validity_url_format"] = invalid_urls == 0
    results["validity_salary"] = invalid_salary == 0

    if short_titles > 0:
        errors.append(f"⚠️ {short_titles} titres trop courts")

    if invalid_urls > 0:
        errors.append(f"⚠️ {invalid_urls} URLs invalides")

    if invalid_salary > 0:
        errors.append(f"⚠️ {invalid_salary} salaires invalides")

    # =========================
    # 3. COHERENCE
    # =========================
    duplicates = df.duplicated(subset=["url"]).sum()

    valid_langs = [
        "fr",
        "en",
        "ar",
        "es",
        "de",
        "unknown"
    ]

    invalid_lang = (
        ~df["language"].isin(valid_langs)
    ).sum()

    results["consistency_no_duplicates"] = duplicates == 0
    results["consistency_language"] = invalid_lang == 0

    if duplicates > 0:
        errors.append(f"⚠️ {duplicates} doublons détectés")

    if invalid_lang > 0:
        errors.append(f"⚠️ {invalid_lang} langues invalides")

    # =========================
    # 4. UNICITE
    # =========================
    dup_urls = df.duplicated(subset=["url"]).sum()

    dup_titles_company = df.duplicated(
        subset=["title", "company", "location"]
    ).sum()

    results["unicite_url"] = dup_urls == 0

    results["unicite_titre_entreprise"] = (
        dup_titles_company == 0
    )

    if dup_urls > 0:
        errors.append(f"⚠️ {dup_urls} URLs dupliquées")

    if dup_titles_company > 0:
        errors.append(
            f"⚠️ {dup_titles_company} doublons titre+entreprise"
        )

    # =========================
    # 5. VALIDITE FORMAT
    # =========================
    valid_sources = [
        "rekrute",
        "linkedin",
        "indeed",
        "wuzzuf"
    ]

    invalid_src = (
        ~df["source"].isin(valid_sources)
    ).sum()

    invalid_lang_format = (
        ~df["language"].isin(valid_langs)
    ).sum()

    results["format_source"] = invalid_src == 0
    results["format_language"] = invalid_lang_format == 0

    if invalid_src > 0:
        errors.append(f"⚠️ {invalid_src} sources invalides")

    if invalid_lang_format > 0:
        errors.append(
            f"⚠️ {invalid_lang_format} langues invalides"
        )

    # =========================
    # 6. INTEGRITE
    # =========================
    empty_titles = (
        df["title"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    results["integrite_titre"] = empty_titles == 0

    if empty_titles > 0:
        errors.append(f"⚠️ {empty_titles} titres vides")

    # =========================
    # RAPPORT FINAL
    # =========================
    passed = sum(results.values())
    total = len(results)

    print(f"\n📊 RAPPORT QUALITÉ : {passed}/{total} tests passés")

    if errors:
        print("\n⚠️ PROBLÈMES DÉTECTÉS :")

        for err in errors:
            print(f"   {err}")

    else:
        print("\n✅ Toutes les données sont valides")

    return {
        "results": results,
        "errors": errors,
        "score": passed / total
    }


# ======================================================
# EXECUTION PRINCIPALE
# ======================================================
if __name__ == "__main__":

    from datalake.minio_client import read_all_bronze
    from medallion.silver import transform_to_silver

    # =========================
    # CHARGEMENT
    # =========================
    raw = read_all_bronze()

    df = transform_to_silver(raw)

    print(f"📦 {len(raw)} offres lues depuis Bronze")
    print(f"✅ Silver : {len(df)} offres après nettoyage")

    # =========================
    # TESTS QUALITE
    # =========================
    report = run_quality_checks(df)

    # =========================
    # SCORE FINAL
    # =========================
    total_tests = len(report["results"])

    passed_tests = sum(report["results"].values())

    print(
        f"\n🎯 SCORE FINAL : "
        f"{report['score']*100:.0f}% "
        f"({passed_tests}/{total_tests} tests)"
    )

    # =========================
    # EXEMPLES URLS INVALIDES
    # =========================
    print("\n🔍 EXEMPLES D'URLS INVALIDES :")

    invalid_urls = df[
        ~df["url"]
        .fillna("")
        .str.startswith("http")
    ]["url"]

    if len(invalid_urls) > 0:

        for url in invalid_urls.head(5):
            print(f"   → {url}")

    else:
        print("   ✅ Aucune URL invalide")

    # =========================
    # SAUVEGARDE JSON
    # =========================
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = f"quality_report_{timestamp}.json"

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "timestamp": datetime.now().isoformat(),

                "score_percent": float(
                    round(report["score"] * 100, 2)
                ),

                "tests_passed": int(passed_tests),
                "tests_total": int(total_tests),

                "details": {
                    k: bool(v)
                    for k, v in report["results"].items()
                },

                "errors": (
                    [str(e) for e in report["errors"]]
                    if report["errors"]
                    else ["Aucune erreur"]
                ),

                "invalid_urls_sample": (
                    invalid_urls.head(10).tolist()
                    if len(invalid_urls) > 0
                    else []
                )
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"\n📄 Rapport sauvegardé dans : {filename}")