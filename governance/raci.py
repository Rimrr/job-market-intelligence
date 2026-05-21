# governance/raci.py
# Matrice RACI — section 03 du cours DAMA-DMBOK

RACI = {
    "Scraping des offres d emploi": {
        "R_Responsable":  "Data Engineer (Rim)",
        "A_Accountable":  "Data Engineer (Rim)",
        "C_Consulte":     "Professeur encadrant",
        "I_Informe":      "Jury de soutenance",
    },
    "Validation qualite des donnees": {
        "R_Responsable":  "Data Engineer (Rim)",
        "A_Accountable":  "Data Engineer (Rim)",
        "C_Consulte":     "Data Steward",
        "I_Informe":      "Professeur encadrant",
    },
    "Stockage Data Lake Bronze": {
        "R_Responsable":  "Data Engineer (Rim) via batch_loader.py",
        "A_Accountable":  "Data Engineer (Rim)",
        "C_Consulte":     "Architecte donnees",
        "I_Informe":      "Jury de soutenance",
    },
    "Transformation Silver Gold": {
        "R_Responsable":  "Data Engineer (Rim) via silver.py + gold.py",
        "A_Accountable":  "Data Engineer (Rim)",
        "C_Consulte":     "Professeur encadrant",
        "I_Informe":      "Jury de soutenance",
    },
    "Acces au Data Warehouse": {
        "R_Responsable":  "Data Engineer (Rim)",
        "A_Accountable":  "Data Engineer (Rim)",
        "C_Consulte":     "Professeur encadrant",
        "I_Informe":      "Jury de soutenance",
        "Note": "Acces restreint : user=jobuser, droits SELECT uniquement pour Metabase",
    },
    "Dashboard Metabase": {
        "R_Responsable":  "Data Engineer (Rim)",
        "A_Accountable":  "Data Engineer (Rim)",
        "C_Consulte":     "Utilisateur final",
        "I_Informe":      "Professeur encadrant",
    },
}

def print_raci():
    print("\n" + "="*60)
    print("   MATRICE RACI — Job Market Intelligence")
    print("="*60)
    for tache, roles in RACI.items():
        print(f"\nTache : {tache}")
        print(f"  R (Responsable) : {roles['R_Responsable']}")
        print(f"  A (Accountable) : {roles['A_Accountable']}")
        print(f"  C (Consulte)    : {roles['C_Consulte']}")
        print(f"  I (Informe)     : {roles['I_Informe']}")
        if "Note" in roles:
            print(f"  Note            : {roles['Note']}")
    print()

if __name__ == "__main__":
    print_raci()