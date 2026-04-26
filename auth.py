import sqlite3
import streamlit as st
import datetime

def get_db_connection():
    # Usar sqlite3, se conectará al archivo local concilia.db
    # check_same_thread=False es necesario para streamlit
    return sqlite3.connect('concilia.db', check_same_thread=False)

def get_users_for_auth():
    """
    Se conecta a la DB y devuelve el diccionario de credenciales
    requerido por streamlit-authenticator.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT username, name, password_hash, email FROM usuarios")
        users = cur.fetchall()
        
        credentials = {"usernames": {}}
        for u in users:
            username, name, pwd_hash, email = u
            credentials["usernames"][username] = {
                "name": name,
                "password": pwd_hash,
                "email": email
            }
        return credentials
    except Exception as e:
        st.error(f"Error al obtener usuarios desde BD: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def registrar_historial(username, cant_coincidencias, cant_solo_banco, cant_solo_libros):
    """
    Guarda en la base de datos el historial de la conciliación.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO historial_conciliaciones 
            (username, fecha, cant_coincidencias, cant_solo_banco, cant_solo_libros)
            VALUES (?, ?, ?, ?, ?)
        """, (username, datetime.datetime.now(), cant_coincidencias, cant_solo_banco, cant_solo_libros))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error guardando historial en BD: {e}")
        return False
    finally:
        cur.close()
        conn.close()
