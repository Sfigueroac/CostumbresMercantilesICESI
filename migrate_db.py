#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar la columna embedding
"""

import sys
import os

# Agregar el directorio actual al path para importar app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Costumbre

def migrar_base_datos():
    """Migra la base de datos para agregar la columna embedding"""
    with app.app_context():
        try:
            # Verificar si la columna embedding ya existe
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('costumbres')]
            
            if 'embedding' not in columns:
                print("🔄 Agregando columna 'embedding' a la tabla costumbres...")
                
                # Agregar la columna embedding
                db.engine.execute("ALTER TABLE costumbres ADD COLUMN embedding TEXT")
                
                print("✅ Columna 'embedding' agregada exitosamente!")
            else:
                print("✅ La columna 'embedding' ya existe en la base de datos.")
            
            # Verificar el total de costumbres
            total = Costumbre.query.count()
            con_embeddings = Costumbre.query.filter(Costumbre.embedding.isnot(None)).count()
            
            print(f"📊 Estado actual:")
            print(f"   Total de costumbres: {total}")
            print(f"   Con embeddings: {con_embeddings}")
            print(f"   Sin embeddings: {total - con_embeddings}")
            
            if total - con_embeddings > 0:
                print(f"\n💡 Para generar embeddings, configura OPENAI_API_KEY y visita:")
                print(f"   http://localhost:5000/admin/generar-embeddings")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando migración de base de datos...")
    if migrar_base_datos():
        print("🎉 Migración completada exitosamente!")
    else:
        print("💥 Error en la migración!")
        sys.exit(1)
