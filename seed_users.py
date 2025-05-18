import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Kullanıcıları temizle (opsiyonel)
    cur.execute("DELETE FROM grades;")
    cur.execute("DELETE FROM users;")

    # 2 öğretmen
    teachers = [
        ("ayse", "1234", "teacher", "Matematik"),
        ("mehmet", "1234", "teacher", "Türkçe")
    ]

    # 3 öğrenci
    students = [
        ("furkan", "1234", "student", None),
        ("elif", "1234", "student", None),
        ("ahmet", "1234", "student", None)
    ]

    # 1 admin
    admin = [("admin", "admin123", "admin", None)]

    # Tüm kullanıcıları ekle
    for user in teachers + students + admin:
        cur.execute("INSERT INTO users (username, password, role, course) VALUES (%s, %s, %s, %s);", user)

    conn.commit()
    print("✅ Test kullanıcıları başarıyla eklendi.")

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Hata:", e)
