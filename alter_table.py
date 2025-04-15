import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("URL:", DATABASE_URL)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("ALTER TABLE users ADD COLUMN course VARCHAR(50);")
    conn.commit()

    print("✅ 'course' sütunu başarıyla eklendi.")
    cur.close()
    conn.close()

except Exception as e:
    print("❌ Hata:", e)
