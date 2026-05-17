import psycopg2
import streamlit as st
import streamlit_authenticator as stauth

def get_db_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

def registrar_nuevo_usuario():
    print("\n=== REGISTRO DE NUEVO USUARIO (CONEXIÓN NEON) ===")
    
    # Pedir los datos por consola
    username = input("Ingresá el username (ej: juani): ").strip().lower()
    name = input("Ingresá el nombre completo (ej: Juan Pérez): ").strip()
    password = input("Ingresá la contraseña: ").strip()
    email = input("Ingresá el correo electrónico (@gmail.com): ").strip().lower()

    # 1. Validación de campos vacíos
    if not username or not name or not password or not email:
        print("\nError: Todos los campos son obligatorios. Intentá de nuevo.")
        return

    # 2. Validación estricta de dominio @gmail.com
    if not email.endswith("@gmail.com"):
        print("\nError: El correo electrónico debe pertenecer exclusivamente al dominio @gmail.com.")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 3. Verificar si el username ya existe en la base de datos
        cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            print(f"\nEl username '{username}' ya se encuentra registrado en Neon. Elegí otro.")
            return

        # 4. Encriptar contraseña de forma segura e insertar registro
        print("\nEncriptando contraseña y conectando con Neon...")
        hashed_pwd = stauth.Hasher.hash(password)
        
        cur.execute("""
            INSERT INTO usuarios (username, name, password_hash, email)
            VALUES (%s, %s, %s, %s)
        """, (username, name, hashed_pwd, email))
        
        conn.commit()
        print(f"\n¡Usuario '{username}' creado con éxito directamente en la nube!")
        print(f"   Ya puede iniciar sesión en Concilia usando su cuenta.")

    except Exception as e:
        print(f"\nOcurrió un error al interactuar con Neon: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    registrar_nuevo_usuario()