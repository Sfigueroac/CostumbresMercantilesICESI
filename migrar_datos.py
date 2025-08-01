import sqlite3
from app import app, db, Costumbres  # Asegúrate de que tu clase modelo se llama Costumbres

# Conectar a la base antigua (con datos)
conexion_antigua = sqlite3.connect('costumbre.db')
cursor = conexion_antigua.cursor()

# Leer los datos existentes
cursor.execute("SELECT ciudad, tipo, contenido FROM costumbres")
datos = cursor.fetchall()

# Insertar en la nueva base de datos con SQLAlchemy
with app.app_context():
    for ciudad, tipo, contenido in datos:
        nueva_costumbre = Costumbres(ciudad=ciudad, tipo=tipo, contenido=contenido)
        db.session.add(nueva_costumbre)
    db.session.commit()

print(f"{len(datos)} costumbres migradas exitosamente.")
