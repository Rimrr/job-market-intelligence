# Client MinIO — accès au Data Lake
from minio import Minio
import json

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def list_files(bucket: str, prefix: str = "") -> list:
    objects = client.list_objects(bucket, prefix=prefix, recursive=True)
    return [obj.object_name for obj in objects]

def read_json(bucket: str, filename: str) -> list:
    response = client.get_object(bucket, filename)
    return json.loads(response.read().decode("utf-8"))

def read_all_bronze(source: str = "") -> list:
    all_offers = []
    for fname in list_files("bronze", prefix=source):
        all_offers.extend(read_json("bronze", fname))
    print(f"📦 {len(all_offers)} offres lues depuis Bronze")
    return all_offers