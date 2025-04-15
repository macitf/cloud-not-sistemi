import psycopg2
import traceback

print("🚀 Kod başlatıldı")

try:
    print("🔌 RDS'e bağlanılıyor...")
    conn = psycopg2.connect(
        dbname="postgres",
        user="notadmin",
        password="furkan.Amazon1",
        host="student-not-db.cd64e8oeslay.eu-north-1.rds.amazonaws.com",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()

    print("📦 'not_sistemi' veritabanı oluşturuluyor...")
    cur.execute("CREATE DATABASE not_sistemi;")
    print("✅ 'not_sistemi' veritabanı başarıyla oluşturuldu.")

    cur.close()
    conn.close()
except Exception as e:
    print("❌ Hata oluştu:")
    traceback.print_exc()

print("🔚 Kod tamamlandı.")
