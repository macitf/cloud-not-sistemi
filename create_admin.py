import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'admin')
        ON CONFLICT (username) DO NOTHING;
    """)

    conn.commit()
    print("✅ Admin kullanıcısı başarıyla eklendi (veya zaten vardı).")

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Hata oluştu:", e)
