# Streaming ingestion : envoi offre par offre vers Kafka
import json
import dataclasses
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(
        v, ensure_ascii=False
    ).encode("utf-8")
)

def send_offer(offer):
    producer.send("job-offers", value=dataclasses.asdict(offer))
    producer.flush()
    print(f"📨 Kafka: envoyé → {offer.title} ({offer.source})")