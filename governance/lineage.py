# governance/lineage.py
import json
from datetime import datetime

LINEAGE_LOG = "governance/lineage_log.json"

LINEAGE_GRAPH = {
    "nodes": [
        {"id": "rekrute.ma",     "type": "source",    "label": "Rekrute.ma (Web)"},
        {"id": "linkedin",       "type": "source",    "label": "LinkedIn (JSearch API)"},
        {"id": "indeed",         "type": "source",    "label": "Indeed (JSearch API)"},
        {"id": "wuzzuf",         "type": "source",    "label": "Wuzzuf.net (Web)"},
        {"id": "kafka",          "type": "pipeline",  "label": "Kafka Topic: job-offers"},
        {"id": "bronze",         "type": "storage",   "label": "MinIO Bronze (JSON brut)"},
        {"id": "silver",         "type": "transform", "label": "Silver (Python + Pandas)"},
        {"id": "gold",           "type": "transform", "label": "Gold (Agregations SQL)"},
        {"id": "warehouse",      "type": "storage",   "label": "PostgreSQL Data Warehouse"},
        {"id": "metabase",       "type": "consumer",  "label": "Metabase Dashboard"},
        {"id": "quality_checks", "type": "control",   "label": "Quality Checks (9/9 tests)"},
    ],
    "edges": [
        {"from": "rekrute.ma", "to": "bronze",   "via": "batch_loader.py",   "mode": "batch"},
        {"from": "linkedin",   "to": "bronze",   "via": "batch_loader.py",   "mode": "batch"},
        {"from": "indeed",     "to": "bronze",   "via": "batch_loader.py",   "mode": "batch"},
        {"from": "wuzzuf",     "to": "bronze",   "via": "batch_loader.py",   "mode": "batch"},
        {"from": "rekrute.ma", "to": "kafka",    "via": "kafka_producer.py", "mode": "streaming"},
        {"from": "bronze",     "to": "silver",   "via": "silver.py",         "transform": "nettoyage, normalisation, detection langue, extraction skills"},
        {"from": "silver",     "to": "gold",     "via": "gold.py",           "transform": "agregation, GROUP BY, COUNT"},
        {"from": "gold",       "to": "warehouse","via": "loader.py",         "mode": "insert"},
        {"from": "warehouse",  "to": "metabase", "via": "SQL natif",         "mode": "read"},
        {"from": "silver",     "to": "quality_checks", "via": "expectations.py", "mode": "validation"},
    ]
}

def log_step(step: str, source: str, records_in: int,
             records_out: int, notes: str = ""):
    entry = {
        "timestamp":       datetime.now().isoformat(),
        "step":            step,
        "source":          source,
        "records_in":      records_in,
        "records_out":     records_out,
        "records_dropped": records_in - records_out,
        "drop_rate":       f"{round((records_in - records_out) / max(records_in,1) * 100, 1)}%",
        "notes":           notes
    }
    try:
        with open(LINEAGE_LOG, "r", encoding="utf-8") as f:
            log = json.load(f)
    except FileNotFoundError:
        log = []

    log.append(entry)

    with open(LINEAGE_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    dropped = records_in - records_out
    status = "OK" if dropped == 0 else f"ATTENTION {dropped} perdus"
    print(f"Lineage [{step}|{source}]: {records_in} -> {records_out} ({status})")

def get_lineage_report() -> list:
    try:
        with open(LINEAGE_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def print_lineage_report():
    print("\n" + "="*60)
    print("   DATA LINEAGE — Job Market Intelligence")
    print("="*60)
    print("""
Pipeline de donnees :

  rekrute.ma ──────────────────────────┐
  linkedin   ──── JSearch API ──────── ├──> Bronze (MinIO)
  indeed     ──────────────────────────┤         |
  wuzzuf     ──────────────────────────┘         v
                                           Silver (nettoyage)
  rekrute.ma ──── Kafka ──────────────>          |
                                                 v
                                           Gold (agregation)
                                                 |
                                                 v
                                        PostgreSQL Warehouse
                                                 |
                                                 v
                                        Metabase Dashboard
    """)

    log = get_lineage_report()
    if log:
        print(f"Etapes loggees  : {len(log)}")
        total_in  = sum(e["records_in"]  for e in log)
        total_out = sum(e["records_out"] for e in log)
        print(f"Total en entree : {total_in}")
        print(f"Total en sortie : {total_out}")
        print(f"Total perdus    : {total_in - total_out}")
        print("\nDernieres etapes :")
        for e in log[-5:]:
            print(f"  [{e['step']}|{e['source']}] "
                  f"{e['records_in']} -> {e['records_out']} "
                  f"({e['drop_rate']} perdus) — {e['timestamp'][:19]}")
    else:
        print("Aucun log — lancez d abord le pipeline ETL")
    print()

def save_lineage_graph():
    import os
    os.makedirs("governance", exist_ok=True)
    with open("governance/lineage_graph.json", "w", encoding="utf-8") as f:
        json.dump(LINEAGE_GRAPH, f, ensure_ascii=False, indent=2)
    print("Lineage graph sauvegarde : governance/lineage_graph.json")

if __name__ == "__main__":
    print_lineage_report()
    save_lineage_graph()