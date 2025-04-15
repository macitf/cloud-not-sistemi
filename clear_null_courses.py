import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # NULL olan dersleri sil
    cursor.execute("DELETE FROM grades WHERE course IS NULL;")
    conn.commit()

    print("🧹 NULL (None) olan ders kayıtları başarıyla silindi.")
    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Hata oluştu:", e)
