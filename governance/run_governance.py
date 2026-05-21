# governance/run_governance.py
# Lance tous les modules de gouvernance en une commande
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from governance.catalogue import print_catalogue, print_glossaire, save_catalogue
from governance.lineage    import print_lineage_report, save_lineage_graph
from governance.raci       import print_raci

def run_all():
    print("\n" + "="*60)
    print("   GOUVERNANCE COMPLETE — Job Market Intelligence")
    print("   Inspire du cadre DAMA-DMBOK (cours EMSI)")
    print("="*60)

    print("\n[1/4] CATALOGUE DE DONNEES")
    print_catalogue()
    save_catalogue()

    print("\n[2/4] GLOSSAIRE METIER")
    print_glossaire()

    print("\n[3/4] DATA LINEAGE")
    print_lineage_report()
    save_lineage_graph()

    print("\n[4/4] MATRICE RACI")
    print_raci()

    print("="*60)
    print("Gouvernance complete executee avec succes !")
    print("Fichiers generes :")
    print("  - governance/data_catalogue.json")
    print("  - governance/lineage_graph.json")
    print("  - governance/lineage_log.json")
    print("="*60)

if __name__ == "__main__":
    run_all()