#!/usr/bin/env python3
"""
Script para exportar datos reales de la base de datos local SQLite
y convertirlos en datos que se puedan cargar en producción
"""

import sqlite3
import json
import os

def export_real_data():
    """
    Exporta los datos reales de la base de datos local
    """
    db_file = 'costumbre.db'  # Base de datos con los datos reales
    
    if not os.path.exists(db_file):
        print(f"❌ No se encontró el archivo {db_file}")
        return None
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Obtener todos los datos
        cursor.execute("SELECT ciudad, tipo, contenido FROM costumbres ORDER BY ciudad, tipo")
        datos = cursor.fetchall()
        
        # Convertir a formato de diccionario
        datos_exportados = []
        for ciudad, tipo, contenido in datos:
            datos_exportados.append({
                "ciudad": ciudad,
                "tipo": tipo,
                "contenido": contenido
            })
        
        conn.close()
        
        print(f"✅ Se exportaron {len(datos_exportados)} registros de {db_file}")
        return datos_exportados
        
    except Exception as e:
        print(f"❌ Error al exportar datos: {e}")
        return None

def save_as_python_file(datos, filename='real_data.py'):
    """
    Guarda los datos en un archivo Python
    """
    if not datos:
        return
    
    content = '''#!/usr/bin/env python3
"""
Datos reales de costumbres mercantiles exportados de la base de datos local
Total de registros: {}
"""

REAL_DATA = [
'''.format(len(datos))
    
    for dato in datos:
        content += '    {\n'
        content += f'        "ciudad": "{dato["ciudad"]}",\n'
        content += f'        "tipo": "{dato["tipo"]}",\n'
        content += f'        "contenido": "{dato["contenido"].replace(chr(34), chr(39))}"\n'  # Escapar comillas
        content += '    },\n'
    
    content += ''']

def create_real_data(app, db, Costumbre):
    """
    Carga los datos reales en la base de datos
    """
    with app.app_context():
        # Verificar si ya hay datos
        current_count = Costumbre.query.count()
        if current_count == 0:
            print("🗄️ Cargando datos reales de costumbres mercantiles...")
            
            for data in REAL_DATA:
                costumbre = Costumbre(
                    ciudad=data["ciudad"],
                    tipo=data["tipo"],
                    contenido=data["contenido"]
                )
                db.session.add(costumbre)
            
            try:
                db.session.commit()
                print(f"✅ Se cargaron {len(REAL_DATA)} costumbres reales")
            except Exception as e:
                print(f"❌ Error al cargar datos reales: {e}")
                db.session.rollback()
        else:
            print(f"ℹ️ Base de datos ya contiene {current_count} registros")
'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"💾 Datos guardados en {filename}")

if __name__ == "__main__":
    print("🚀 Exportando datos reales de la base de datos...")
    datos = export_real_data()
    if datos:
        save_as_python_file(datos, 'real_data.py')
        print("✨ Exportación completada!")
    else:
        print("❌ No se pudo completar la exportación")
