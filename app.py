from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_caching import Cache
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

# 12 Factor - Config
load_dotenv()

app = Flask(__name__)

# 12 Factor - Dependencies & Backing Services
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Redis bağlantısı
cache_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": os.getenv("REDIS_URL")
}
cache = Cache(config=cache_config)
cache.init_app(app)

# Log fonksiyonu (stdout)
def log(msg):
    print(f"📘 {msg}")


# Tabloları oluştur
def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL,
            role VARCHAR(20) NOT NULL,
            course VARCHAR(50)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES users(id),
            course VARCHAR(100),
            grade INTEGER
        );
    """)
    conn.commit()
    log("Veritabanı tabloları oluşturuldu")
    
    

# 🔐 Giriş Sayfası
@app.route('/')
def index():
    return render_template("login.html")



# 🔐 Giriş Kontrolü
@app.route('/login', methods=['POST'])
def login_web():
    username = request.form.get("username")
    password = request.form.get("password")

    cursor.execute("SELECT id, role, course FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        user_id, role, course = user

        if role == "teacher":
            cursor.execute("SELECT username FROM users WHERE id=%s", (user_id,))
            name = cursor.fetchone()[0]

            cursor.execute("SELECT student_id, course, grade FROM grades WHERE course=%s", (course,))
            grades = cursor.fetchall()

            cursor.execute("SELECT id, username FROM users WHERE role='student'")
            students = cursor.fetchall()

            # Ortalama hesapla
            cursor.execute("SELECT ROUND(AVG(grade), 1) FROM grades WHERE course = %s", (course,))
            course_avg = cursor.fetchone()[0] or 0

            return render_template("teacher.html",
                                   teacher_name=name,
                                   course=course,
                                   teacher_id=user_id,
                                   grades=grades,
                                   students=students,
                                   course_average=course_avg)

        else:
            return redirect(url_for('view_grades_web', student_id=user_id))

    return "<h3>❌ Hatalı giriş bilgisi. <a href='/'>Geri dön</a></h3>"



# 🧑‍🏫 Not Ekleme (Öğretmen Paneli)
# 🧑‍🏫 Not Ekleme (Güncellenmiş - UPSERT ile)
@app.route('/teacher/add-grade', methods=['POST'])
def add_grade_web():
    student_id = request.form.get("student_id")
    grade = request.form.get("grade")
    teacher_id = request.form.get("teacher_id")

    try:
        # Öğretmenin verdiği dersi ve adını çek
        cursor.execute("SELECT course, username FROM users WHERE id=%s", (teacher_id,))
        course, name = cursor.fetchone()

        # Notu ekle veya güncelle
        cursor.execute("""
            INSERT INTO grades (student_id, course, grade)
            VALUES (%s, %s, %s)
            ON CONFLICT (student_id, course)
            DO UPDATE SET grade = EXCLUDED.grade;
        """, (student_id, course, grade))
        conn.commit()

        # ✅ Öğrenciye ait not cache'i sil
        cache.delete(f"grades_{student_id}")

    except Exception as e:
        conn.rollback()
        print("❌ Not eklenirken hata:", e)
        return "<h3>❌ Not eklenemedi. Hata loga yazıldı. <a href='/'>Geri dön</a></h3>"

    # Notları tekrar çek
    cursor.execute("SELECT student_id, course, grade FROM grades WHERE course=%s", (course,))
    grades = cursor.fetchall()

    # Öğrenci listesini çek
    cursor.execute("SELECT id, username FROM users WHERE role='student'")
    students = cursor.fetchall()

    # Ortalama hesapla
    cursor.execute("SELECT ROUND(AVG(grade), 1) FROM grades WHERE course = %s", (course,))
    course_avg = cursor.fetchone()[0] or 0

    return render_template("teacher.html",
                           teacher_name=name,
                           course=course,
                           teacher_id=teacher_id,
                           grades=grades,
                           students=students,
                           course_average=course_avg)



# 🧑‍🏫 Not Silme (Öğretmen Paneli)
@app.route('/grades/<int:student_id>', methods=['DELETE'])
def delete_grade(student_id):
    cursor.execute("DELETE FROM grades WHERE student_id = %s", (student_id,))
    conn.commit()
    return jsonify({"message": f"Öğrenci {student_id} notları silindi."})

# 👨‍🎓 Öğrenci Paneli
@app.route('/students/<int:student_id>/grades')
@cache.cached(timeout=300, key_prefix=lambda: f"grades_{request.view_args['student_id']}")
def view_grades_web(student_id):
    # Öğrencinin notlarını al
    cursor.execute("SELECT course, grade FROM grades WHERE student_id=%s", (student_id,))
    student_grades = cursor.fetchall()

    # Öğrencinin adı
    cursor.execute("SELECT username FROM users WHERE id=%s", (student_id,))
    student_name = cursor.fetchone()[0]

    # Her ders için genel sınıf ortalamasını çek
    cursor.execute("""
        SELECT course, ROUND(AVG(grade), 1)
        FROM grades
        WHERE course IS NOT NULL
        GROUP BY course
    """)
    averages = cursor.fetchall()

    # Ortalamaları sözlük haline getir
    avg_dict = {course: avg for course, avg in averages}

    return render_template("student.html",
                           grades=student_grades,
                           student_id=student_id,
                           student_name=student_name,
                           averages=avg_dict)





# 🔁 API endpoints (opsiyonel, dıştan erişim için)
@app.route('/api/students/<int:student_id>/grades', methods=['GET'])
def get_grades_api(student_id):
    cursor.execute("SELECT course, grade FROM grades WHERE student_id=%s", (student_id,))
    result = cursor.fetchall()
    return jsonify([{"course": r[0], "grade": r[1]} for r in result])

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    
if __name__ == "__main__":
    app.run(debug=True)
