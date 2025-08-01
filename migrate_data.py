#!/usr/bin/env python3
"""
Script para migrar datos existentes a la nueva instancia de base de datos
Solo ejecutar si tienes datos importantes en tu base de datos local
"""

import sqlite3
import os
from app import app, db, Costumbre

def migrar_datos_locales():
    """Migra datos desde costumbres.db local a la nueva base de datos"""
    
    # Verificar si existe la base de datos local
    if not os.path.exists('costumbres.db'):
        print("No se encontró la base de datos local costumbres.db")
        return
    
    try:
        # Conectar a la base de datos local
        conn = sqlite3.connect('costumbres.db')
        cursor = conn.cursor()
        
        # Obtener todos los datos
        cursor.execute("SELECT ciudad, tipo, contenido FROM costumbres")
        datos = cursor.fetchall()
        
        if not datos:
            print("No hay datos para migrar")
            return
        
        # Crear la nueva base de datos y migrar datos
        with app.app_context():
            db.create_all()
            
            # Insertar datos
            for ciudad, tipo, contenido in datos:
                nueva_costumbre = Costumbre(
                    ciudad=ciudad,
                    tipo=tipo,
                    contenido=contenido
                )
                db.session.add(nueva_costumbre)
            
            db.session.commit()
            print(f"✅ Se migraron {len(datos)} registros exitosamente")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    migrar_datos_locales()
