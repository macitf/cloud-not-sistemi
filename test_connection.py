import psycopg2

DATABASE_URL = "postgresql://notadmin:furkan.Amazon1@student-not-db.cd64e8oeslay.eu-north-1.rds.amazonaws.com:5432/not_sistemi"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Veritabanına başarıyla bağlanıldı!")
    conn.close()
except Exception as e:
    print("❌ Bağlantı hatası:", e)
