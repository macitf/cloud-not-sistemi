import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("UPDATE users SET course = 'Türkçe' WHERE username = 'mehmet'")
conn.commit()

print("✅ mehmet kullanıcısının dersi Türkçe olarak güncellendi.")
cursor.close()
conn.close()
