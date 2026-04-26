import sqlite3
import streamlit_authenticator as stauth

def get_db_connection():
    return sqlite3.connect('concilia.db')

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Crear tabla usuarios
    print("Creando tabla usuarios...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100)
        );
    """)
    
    # 2. Crear tabla historial_conciliaciones
    print("Creando tabla historial_conciliaciones...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historial_conciliaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cant_coincidencias INT,
            cant_solo_banco INT,
            cant_solo_libros INT
        );
    """)
    
    # 3. Crear usuario administrador por defecto si no existe
    admin_username = "admin"
    cur.execute("SELECT id FROM usuarios WHERE username = ?", (admin_username,))
    if not cur.fetchone():
        print("Insertando usuario admin por defecto...")
        password = "admin123"
        hashed_pwd = stauth.Hasher.hash(password)
        
        cur.execute("""
            INSERT INTO usuarios (username, name, password_hash, email) 
            VALUES (?, ?, ?, ?)
        """, (admin_username, "Administrador", hashed_pwd, "admin@concilia.com"))
        
    conn.commit()
    cur.close()
    conn.close()
    print("¡Base de datos inicializada correctamente!")

if __name__ == "__main__":
    setup_database()
