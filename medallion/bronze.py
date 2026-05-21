# Bronze : sauvegarde brute telle quelle (aucune transformation)
from ingestion.batch_loader import upload_to_bronze

def save_raw(offers: list, source: str):
    """Envoie les données brutes dans le bucket Bronze sans aucun traitement."""
    upload_to_bronze(offers, source)