#!/usr/bin/env python3
"""
Script para probar la configuración de OpenAI y generar embeddings de prueba
"""

import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openai_config():
    """Prueba la configuración de OpenAI"""
    print("🔍 Verificando configuración de OpenAI...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY no encontrada en variables de entorno")
        print("💡 Edita el archivo .env y agrega tu API key:")
        print("   OPENAI_API_KEY=sk-tu_api_key_aqui")
        return False
    
    if api_key == "sk-coloca_tu_api_key_aqui":
        print("❌ Por favor reemplaza la API key de ejemplo con tu API key real")
        print("💡 Edita el archivo .env y agrega tu API key:")
        print("   OPENAI_API_KEY=sk-tu_api_key_real")
        return False
    
    print(f"✅ API key encontrada: {api_key[:10]}...{api_key[-4:]}")
    
    # Probar importación de OpenAI
    try:
        from openai import OpenAI
        print("✅ Biblioteca OpenAI importada correctamente")
    except ImportError:
        print("❌ Error importando OpenAI. ¿Está instalada?")
        return False
    
    # Probar conexión con OpenAI
    try:
        client = OpenAI(api_key=api_key)
        print("✅ Cliente OpenAI creado correctamente")
        
        # Hacer una prueba simple
        print("🧪 Probando generación de embedding...")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="Esta es una prueba de embedding"
        )
        
        if response.data and len(response.data) > 0:
            embedding_length = len(response.data[0].embedding)
            print(f"✅ ¡Embedding generado exitosamente! Dimensiones: {embedding_length}")
            return True
        else:
            print("❌ Error: respuesta vacía de OpenAI")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con OpenAI: {e}")
        if "api_key" in str(e).lower():
            print("💡 Verifica que tu API key sea correcta y tenga créditos disponibles")
        return False

def test_app_integration():
    """Prueba la integración con la aplicación"""
    print("\n🔍 Verificando integración con la aplicación...")
    
    try:
        from app import app, busqueda_semantica, Costumbre
        print("✅ Aplicación importada correctamente")
        
        if busqueda_semantica.habilitado:
            print("✅ Búsqueda semántica HABILITADA")
        else:
            print("❌ Búsqueda semántica DESHABILITADA")
            return False
        
        # Verificar base de datos
        with app.app_context():
            total_costumbres = Costumbre.query.count()
            con_embeddings = Costumbre.query.filter(Costumbre.embedding.isnot(None)).count()
            
            print(f"📊 Costumbres en base de datos: {total_costumbres}")
            print(f"📊 Con embeddings: {con_embeddings}")
            print(f"📊 Sin embeddings: {total_costumbres - con_embeddings}")
            
            if total_costumbres - con_embeddings > 0:
                print("💡 Hay costumbres sin embeddings. Ve a: http://localhost:5002/admin/generar-embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False

def main():
    print("🚀 Prueba de configuración de IA para Costumbres Mercantiles")
    print("=" * 60)
    
    openai_ok = test_openai_config()
    
    if openai_ok:
        app_ok = test_app_integration()
        
        if app_ok:
            print("\n🎉 ¡Configuración completa exitosa!")
            print("🌐 Abre: http://localhost:5002")
            print("⚙️  Para generar embeddings: http://localhost:5002/admin/generar-embeddings")
            print("📊 Para ver estado: http://localhost:5002/admin/estado-embeddings")
        else:
            print("\n💥 Error en la integración con la aplicación")
    else:
        print("\n💥 Error en la configuración de OpenAI")

if __name__ == "__main__":
    main()
