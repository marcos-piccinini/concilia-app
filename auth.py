import psycopg2
import datetime
import streamlit as st
import streamlit_authenticator as stauth  # Importación vital para que no dé error

def get_db_connection():
    # Conexión directa a Neon usando los secrets
    return psycopg2.connect(st.secrets["DATABASE_URL"])

def _ensure_feedback_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_dia DATE NOT NULL,
            rating_interfaz INTEGER,
            rating_resultados INTEGER,
            comentario TEXT
        )
    """)
    conn.commit()
    cur.close()

def get_users_for_auth():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT username, name, password_hash, email FROM usuarios")
        users = cur.fetchall()
        credentials = {"usernames": {}}
        for username, name, pwd_hash, email in users:
            credentials["usernames"][username] = {
                "name": name,
                "password": pwd_hash,
                "email": email,
            }
        return credentials
    except Exception as e:
        st.error(f"Error al obtener usuarios desde BD: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def registrar_nuevo_usuario_db(username, name, password, email):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Verificar si el usuario ya existe
        cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            return False, "El username ya esta registrado."
        
        # Encriptar contraseña usando stauth
        hashed_pwd = stauth.Hasher.hash(password)
        
        cur.execute("""
            INSERT INTO usuarios (username, name, password_hash, email)
            VALUES (%s, %s, %s, %s)
        """, (username, name, hashed_pwd, email))
        
        conn.commit()
        return True, "Cuenta creada con exito."
    except Exception as e:
        return False, f"Error en BD: {e}"
    finally:
        cur.close()
        conn.close()

def registrar_historial(username, cant_coincidencias, cant_solo_banco, cant_solo_libros):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO historial_conciliaciones
            (username, fecha, cant_coincidencias, cant_solo_banco, cant_solo_libros)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, datetime.datetime.now(), cant_coincidencias, cant_solo_banco, cant_solo_libros))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error guardando historial: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_conciliaciones_hoy(username):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        today = datetime.date.today().isoformat()
        # En Postgres se usa ::DATE para filtrar por fecha
        cur.execute("""
            SELECT COUNT(*) FROM historial_conciliaciones
            WHERE username = %s AND fecha::DATE = %s
        """, (username, today))
        return cur.fetchone()[0]
    except Exception:
        return 0
    finally:
        cur.close()
        conn.close()

def feedback_completado_hoy(username):
    conn = get_db_connection()
    _ensure_feedback_table(conn)
    cur = conn.cursor()
    try:
        today = datetime.date.today().isoformat()
        cur.execute("""
            SELECT COUNT(*) FROM feedback
            WHERE username = %s AND fecha_dia = %s
        """, (username, today))
        return cur.fetchone()[0] > 0
    except Exception:
        return False
    finally:
        cur.close()
        conn.close()

def guardar_feedback(username, rating_interfaz, rating_resultados, comentario):
    conn = get_db_connection()
    _ensure_feedback_table(conn)
    cur = conn.cursor()
    try:
        today = datetime.date.today().isoformat()
        cur.execute("""
            INSERT INTO feedback (username, fecha, fecha_dia, rating_interfaz, rating_resultados, comentario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, datetime.datetime.now(), today, rating_interfaz, rating_resultados, comentario))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error guardando feedback: {e}")
        return False
    finally:
        cur.close()
        conn.close()