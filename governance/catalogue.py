# governance/catalogue.py
# Inspiré du concept DataHub/Apache Atlas du cours (section 08)
import json
from datetime import datetime

CATALOGUE = {
    "fact_job_offers": {
        "description": "Table de faits centrale — toutes les offres d'emploi collectees",
        "layer": "Gold / Data Warehouse",
        "source": "rekrute.ma, linkedin, indeed, wuzzuf.net",
        "owner": "Data Engineer — Rim",
        "steward": "Rim",
        "columns": {
            "id":           {"type": "SERIAL",    "nullable": False, "description": "Identifiant unique"},
            "title":        {"type": "TEXT",      "nullable": False, "description": "Intitule du poste"},
            "company":      {"type": "TEXT",      "nullable": True,  "description": "Nom de l entreprise"},
            "location":     {"type": "TEXT",      "nullable": True,  "description": "Ville ou region"},
            "salary_min":   {"type": "INTEGER",   "nullable": True,  "description": "Salaire minimum en MAD"},
            "salary_max":   {"type": "INTEGER",   "nullable": True,  "description": "Salaire maximum en MAD"},
            "language":     {"type": "VARCHAR",   "nullable": True,  "description": "Langue detectee (fr/en/ar)"},
            "source":       {"type": "TEXT",      "nullable": False, "description": "Site source de l offre"},
            "url":          {"type": "TEXT",      "nullable": False, "description": "Lien unique vers l offre"},
            "published_at": {"type": "TIMESTAMP", "nullable": True,  "description": "Date de publication"},
            "scraped_at":   {"type": "TIMESTAMP", "nullable": True,  "description": "Date de collecte"},
        },
        "quality_score": 100,
        "last_updated": datetime.now().isoformat(),
        "row_count": 0,
        "tags": ["emploi", "maroc", "big-data", "scraping"],
        "conformite": "Donnees publiques — pas de PII — conforme Loi 09-08"
    },
    "dim_skills": {
        "description": "Dimension referentiel des competences techniques",
        "layer": "Gold / Data Warehouse",
        "owner": "Data Engineer — Rim",
        "columns": {
            "id":   {"type": "SERIAL", "nullable": False, "description": "Identifiant unique"},
            "name": {"type": "TEXT",   "nullable": False, "description": "Nom de la competence (python, sql...)"},
        },
        "quality_score": 100,
        "last_updated": datetime.now().isoformat(),
    },
    "bronze_rekrute": {
        "description": "Donnees brutes JSON scrappees depuis Rekrute.ma",
        "layer": "Bronze / Data Lake MinIO",
        "format": "JSON",
        "path": "minio://bronze/rekrute/YYYY/MM/DD/HH/offers.json",
        "owner": "Data Engineer — Rim",
        "quality_score": None,
        "note": "Aucune transformation — donnees brutes conservees",
        "last_updated": datetime.now().isoformat(),
    },
}

GLOSSAIRE = {
    "offre_emploi": {
        "definition": "Annonce publiee par une entreprise pour recruter un profil specifique",
        "synonymes":  ["job offer", "offre de poste", "annonce RH"],
        "tables_liees": ["fact_job_offers"],
    },
    "competence": {
        "definition": "Technologie ou savoir-faire technique mentionne dans une offre d emploi",
        "exemples":   ["python", "sql", "docker", "machine learning"],
        "tables_liees": ["dim_skills", "offer_skills"],
        "regle_metier": "Extraite depuis titre + description via liste SKILLS_LIST",
    },
    "salary_min": {
        "definition": "Salaire minimum extrait de la fourchette salariale en MAD (Dirham marocain)",
        "contrainte": "Doit etre > 0 si renseigne",
        "tables_liees": ["fact_job_offers"],
    },
    "source": {
        "definition": "Site web d origine de l offre d emploi",
        "valeurs_valides": ["rekrute", "linkedin", "indeed", "wuzzuf"],
        "tables_liees": ["fact_job_offers"],
    },
    "language": {
        "definition": "Langue detectee automatiquement dans la description de l offre",
        "valeurs_valides": ["fr", "en", "ar", "es", "de", "unknown"],
        "outil": "langdetect Python library",
        "tables_liees": ["fact_job_offers"],
    },
}

def print_catalogue():
    print("\n" + "="*60)
    print("   CATALOGUE DE DONNEES — Job Market Intelligence")
    print("="*60)
    for table, meta in CATALOGUE.items():
        print(f"\n📋 Table : {table}")
        print(f"   Description : {meta['description']}")
        print(f"   Couche      : {meta.get('layer', 'N/A')}")
        print(f"   Owner       : {meta.get('owner', 'N/A')}")
        score = meta.get('quality_score')
        if score:
            print(f"   Score qualite: {score}/100")
    print()

def print_glossaire():
    print("\n" + "="*60)
    print("   GLOSSAIRE METIER — Job Market Intelligence")
    print("="*60)
    for terme, meta in GLOSSAIRE.items():
        print(f"\n📖 Terme : {terme}")
        print(f"   Definition : {meta['definition']}")
        if "valeurs_valides" in meta:
            print(f"   Valeurs    : {meta['valeurs_valides']}")
    print()

def save_catalogue():
    with open("governance/data_catalogue.json", "w", encoding="utf-8") as f:
        json.dump({"catalogue": CATALOGUE, "glossaire": GLOSSAIRE}, f,
                  ensure_ascii=False, indent=2)
    print("Catalogue sauvegarde : governance/data_catalogue.json")

if __name__ == "__main__":
    print_catalogue()
    print_glossaire()
    save_catalogue()