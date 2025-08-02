#!/usr/bin/env python3
"""
Script de demostración para mostrar cómo funcionaría la búsqueda semántica
Genera embeddings simulados para demostración sin usar OpenAI
"""

import sys
import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Costumbre

def generar_embeddings_demo():
    """Genera embeddings de demostración usando TF-IDF en lugar de OpenAI"""
    print("🎯 Generando embeddings de DEMOSTRACIÓN (sin OpenAI)")
    print("   Nota: Para producción real, necesitas configurar OPENAI_API_KEY")
    
    with app.app_context():
        # Obtener todas las costumbres
        costumbres = Costumbre.query.all()
        textos = [c.get_texto_completo() for c in costumbres]
        
        print(f"📊 Procesando {len(costumbres)} costumbres...")
        
        # Usar TF-IDF como embedding de demostración
        vectorizer = TfidfVectorizer(max_features=300, stop_words='english')
        embeddings_matrix = vectorizer.fit_transform(textos).toarray()
        
        # Guardar embeddings en la base de datos
        for i, costumbre in enumerate(costumbres):
            # Convertir a lista para JSON serialization
            embedding_vector = embeddings_matrix[i].tolist()
            costumbre.set_embedding(embedding_vector)
            
            if i % 20 == 0:
                print(f"   Procesadas {i+1}/{len(costumbres)} costumbres...")
        
        db.session.commit()
        print("✅ Embeddings de demostración generados exitosamente!")
        
        return vectorizer

def demo_busqueda_semantica():
    """Demostración de búsqueda semántica"""
    print("\n🔍 Demostración de Búsqueda Semántica")
    print("=" * 50)
    
    # Consultas de ejemplo
    consultas_demo = [
        "contratos de café en el huila",
        "pagos en agricultura",
        "costumbres bancarias",
        "comercio de flores"
    ]
    
    with app.app_context():
        # Verificar que tenemos embeddings
        con_embeddings = Costumbre.query.filter(Costumbre.embedding.isnot(None)).count()
        if con_embeddings == 0:
            print("❌ No hay embeddings generados. Ejecuta generar_embeddings_demo() primero")
            return
        
        print(f"📊 Costumbres con embeddings: {con_embeddings}")
        
        for consulta in consultas_demo:
            print(f"\n🔎 Consulta: '{consulta}'")
            resultados = buscar_semanticamente_demo(consulta)
            
            print("   📝 Resultados más relevantes:")
            for i, (costumbre, similitud) in enumerate(resultados[:3]):
                print(f"   {i+1}. [{similitud:.1%}] {costumbre.ciudad} - {costumbre.tipo}")
                print(f"      {costumbre.contenido[:100]}...")

def buscar_semanticamente_demo(consulta):
    """Búsqueda semántica usando TF-IDF (demostración)"""
    # Esta función simula lo que haría OpenAI
    costumbres_con_embedding = Costumbre.query.filter(Costumbre.embedding.isnot(None)).all()
    
    if not costumbres_con_embedding:
        return []
    
    # Para la demo, usamos una métrica simple basada en palabras clave
    resultados = []
    consulta_lower = consulta.lower()
    
    for costumbre in costumbres_con_embedding:
        texto_costumbre = costumbre.get_texto_completo().lower()
        
        # Cálculo simple de similitud basado en palabras comunes
        palabras_consulta = set(consulta_lower.split())
        palabras_costumbre = set(texto_costumbre.split())
        
        # Similitud Jaccard simple
        interseccion = len(palabras_consulta.intersection(palabras_costumbre))
        union = len(palabras_consulta.union(palabras_costumbre))
        similitud = interseccion / union if union > 0 else 0
        
        # Boost para coincidencias exactas
        if any(palabra in texto_costumbre for palabra in palabras_consulta):
            similitud += 0.2
        
        resultados.append((costumbre, similitud))
    
    # Ordenar por similitud
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados

def main():
    print("🎭 DEMOSTRACIÓN: Búsqueda Semántica sin OpenAI")
    print("=" * 60)
    print("Esta demostración muestra cómo funcionaría la búsqueda semántica")
    print("usando TF-IDF en lugar de OpenAI para propósitos educativos.")
    print()
    
    # Verificar si ya tenemos embeddings
    with app.app_context():
        con_embeddings = Costumbre.query.filter(Costumbre.embedding.isnot(None)).count()
        
        if con_embeddings == 0:
            print("📦 Generando embeddings de demostración...")
            generar_embeddings_demo()
        else:
            print(f"✅ Ya existen {con_embeddings} embeddings de demostración")
    
    # Hacer demostración de búsqueda
    demo_busqueda_semantica()
    
    print("\n🎉 ¡Demostración completada!")
    print("💡 Para usar IA real, configura OPENAI_API_KEY con créditos disponibles")
    print("🌐 Ve a: http://localhost:5002 para probar la interfaz")

if __name__ == "__main__":
    main()
