import psycopg2
import streamlit as st
import streamlit_authenticator as stauth

def get_db_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()

    print("Creando tabla usuarios...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100)
        );
    """)

    print("Creando tabla historial_conciliaciones...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historial_conciliaciones (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cant_coincidencias INT,
            cant_solo_banco INT,
            cant_solo_libros INT
        );
    """)

    print("Creando tabla feedback...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_dia DATE NOT NULL,
            rating_interfaz INTEGER,
            rating_resultados INTEGER,
            comentario TEXT
        );
    """)

    admin_username = "admin"
    # OJO: en Postgres se usa %s en lugar de ?
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (admin_username,))
    if not cur.fetchone():
        print("Insertando usuario admin por defecto...")
        hashed_pwd = stauth.Hasher.hash("admin123")
        cur.execute("""
            INSERT INTO usuarios (username, name, password_hash, email)
            VALUES (%s, %s, %s, %s)
        """, (admin_username, "Administrador", hashed_pwd, "admin@concilia.com"))

    conn.commit()
    cur.close()
    conn.close()
    print("¡Base de datos inicializada correctamente!")

if __name__ == "__main__":
    setup_database()