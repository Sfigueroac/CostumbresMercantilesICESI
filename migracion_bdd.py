import sqlite3
from app import app, db, Costumbre  # Asegúrate que la clase se llama 'Costumbre'

# Conectar a la base antigua con datos
conexion_antigua = sqlite3.connect('costumbre.db')
cursor = conexion_antigua.cursor()

cursor.execute("SELECT ciudad, tipo, contenido FROM costumbres")
datos = cursor.fetchall()

with app.app_context():
    db.create_all()  # ✅ Asegura que la tabla exista antes de insertar

    for ciudad, tipo, contenido in datos:
        nueva = Costumbre(ciudad=ciudad, tipo=tipo, contenido=contenido)
        db.session.add(nueva)

    db.session.commit()

print(f"{len(datos)} costumbres migradas exitosamente.")
