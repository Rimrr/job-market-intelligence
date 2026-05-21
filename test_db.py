import pg8000.native

try:
    conn = pg8000.native.Connection(
        host="localhost",
        port=5432,
        database="jobmarket",
        user="jobuser",
        password="",
    )
    result = conn.run("SELECT version()")
    print("✅ Connexion OK :", result)
    conn.close()
except Exception as e:
    print("❌ Erreur :", e)