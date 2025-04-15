import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        ALTER TABLE grades
        ADD CONSTRAINT unique_student_course
        UNIQUE (student_id, course);
    """)
    conn.commit()

    print("✅ UNIQUE constraint başarıyla eklendi.")
    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Hata:", e)
