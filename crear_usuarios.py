import psycopg2
import streamlit as st
import streamlit_authenticator as stauth

# Lista de usuarios de tu archivo original
usuarios = [
    # (username, nombre completo, password, email)
    ("admin",    "Administrador",   "admin123",   "admin@concilia.com"),
    ("santi",    "Santino",         "santi123",   "santi@concilia.com"),
    ("demo",     "Usuario Demo",    "demo123",    "demo@concilia.com"),
    ("tester",   "QA Tester",       "test123",    "tester@concilia.com"),
    ("martin",   "Martín López",    "martin123",  "martin@concilia.com"),
]

# Conexión a Neon usando los secrets de Streamlit
conn = psycopg2.connect(st.secrets["DATABASE_URL"])
cur  = conn.cursor()

creados   = []
existente = []

for username, name, password, email in usuarios:
    # En Postgres usamos %s en lugar de ?
    cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    if cur.fetchone():
        existente.append(username)
        continue
    
    hashed = stauth.Hasher.hash(password)
    cur.execute(
        "INSERT INTO usuarios (username, name, password_hash, email) VALUES (%s, %s, %s, %s)",
        (username, name, hashed, email),
    )
    creados.append(username)

conn.commit()
cur.close()
conn.close()

print("\nUsuarios migrados a Neon:")
for u in creados:
    match = next(x for x in usuarios if x[0] == u)
    print(f"   usuario: {match[0]:<12}  contraseña: {match[2]}")

if existente:
    print(f"\nYa existían en Neon (no se tocaron): {', '.join(existente)}")
print()