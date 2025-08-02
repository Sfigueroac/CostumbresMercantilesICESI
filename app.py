from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from urllib.parse import quote
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Configuración de OpenAI (solo si está disponible)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI no disponible. Funcionalidades de IA deshabilitadas.")

app = Flask(__name__)

# Configuración de base de datos para producción y desarrollo
if os.environ.get('RENDER'):
    # Configuración para Render (producción)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///costumbres.db'
else:
    # Configuración para desarrollo local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///costumbres.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo: costumbres (en plural para que coincida con la base real)
class Costumbre(db.Model):
    __tablename__ = 'costumbres'  # <- esto es clave para evitar el error
    id = db.Column(db.Integer, primary_key=True)
    ciudad = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    contenido = db.Column(db.String(255), nullable=False)
    embedding = db.Column(db.Text)  # Almacenar embedding como JSON string
    
    def set_embedding(self, embedding_vector):
        """Almacena el vector embedding como JSON string"""
        if embedding_vector is not None:
            self.embedding = json.dumps(embedding_vector)
    
    def get_embedding(self):
        """Recupera el vector embedding desde JSON string"""
        if self.embedding:
            return np.array(json.loads(self.embedding))
        return None
    
    def get_texto_completo(self):
        """Genera el texto completo para embedding"""
        return f"Ciudad: {self.ciudad}. Tipo: {self.tipo}. Contenido: {self.contenido}"

# Clase para búsqueda semántica
class BusquedaSemantica:
    def __init__(self):
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.habilitado = True
        else:
            self.habilitado = False
            print("⚠️  Búsqueda semántica deshabilitada. Configure OPENAI_API_KEY para habilitarla.")
    
    def generar_embedding(self, texto):
        """Genera embedding para un texto usando OpenAI"""
        if not self.habilitado:
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generando embedding: {e}")
            return None
    
    def buscar_similar(self, query, top_k=10):
        """Busca costumbres similares usando embeddings"""
        if not self.habilitado:
            return []
        
        query_embedding = self.generar_embedding(query)
        if query_embedding is None:
            return []
        
        resultados = []
        costumbres_con_embedding = Costumbre.query.filter(Costumbre.embedding.isnot(None)).all()
        
        for costumbre in costumbres_con_embedding:
            embedding_costumbre = costumbre.get_embedding()
            if embedding_costumbre is not None:
                # Calcular similitud coseno
                similarity = cosine_similarity([query_embedding], [embedding_costumbre])[0][0]
                resultados.append((costumbre, float(similarity)))
        
        # Ordenar por similitud descendente
        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados[:top_k]
    
    def generar_embeddings_faltantes(self):
        """Genera embeddings para todas las costumbres que no los tienen"""
        if not self.habilitado:
            print("⚠️  No se pueden generar embeddings sin OpenAI API configurada")
            return
        
        costumbres_sin_embedding = Costumbre.query.filter(
            (Costumbre.embedding.is_(None)) | (Costumbre.embedding == '')
        ).all()
        
        print(f"🔄 Generando embeddings para {len(costumbres_sin_embedding)} costumbres...")
        
        for i, costumbre in enumerate(costumbres_sin_embedding):
            texto = costumbre.get_texto_completo()
            embedding = self.generar_embedding(texto)
            
            if embedding:
                costumbre.set_embedding(embedding)
                print(f"✅ Embedding generado para costumbre {costumbre.id} ({i+1}/{len(costumbres_sin_embedding)})")
            else:
                print(f"❌ Error generando embedding para costumbre {costumbre.id}")
        
        db.session.commit()
        print("🎉 Proceso completado!")

# Instancia global de búsqueda semántica
busqueda_semantica = BusquedaSemantica()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ciudad = request.form.get('ciudad')
        tipo = request.form.get('tipo')
        contenido = request.form.get('contenido')

        nueva = Costumbre(ciudad=ciudad, tipo=tipo, contenido=contenido)
        db.session.add(nueva)
        db.session.commit()
        return redirect('/')

    # Búsqueda tradicional
    ciudad_q = request.args.get('search_ciudad', '')
    tipo_q = request.args.get('search_tipo', '')
    contenido_q = request.args.get('search_contenido', '')
    
    # Búsqueda semántica
    busqueda_semantica_q = request.args.get('search_semantica', '')
    
    resultados = []
    es_busqueda_semantica = False
    similitudes = {}
    
    if busqueda_semantica_q and busqueda_semantica.habilitado:
        # Realizar búsqueda semántica
        resultados_semanticos = busqueda_semantica.buscar_similar(busqueda_semantica_q, top_k=20)
        resultados = [costumbre for costumbre, similitud in resultados_semanticos]
        similitudes = {costumbre.id: similitud for costumbre, similitud in resultados_semanticos}
        es_busqueda_semantica = True
    else:
        # Búsqueda tradicional
        resultados = Costumbre.query.filter(
            Costumbre.ciudad.ilike(f'%{ciudad_q}%'),
            Costumbre.tipo.ilike(f'%{tipo_q}%'),
            Costumbre.contenido.ilike(f'%{contenido_q}%')
        ).all()

    return render_template('index.html', 
                         lascostumbres=resultados,
                         es_busqueda_semantica=es_busqueda_semantica,
                         similitudes=similitudes,
                         busqueda_semantica_habilitada=busqueda_semantica.habilitado)

@app.route('/acerca-de')
def acerca_de():
    """Página informativa sobre las costumbres mercantiles"""
    return render_template('acerca_de.html')

@app.route('/api/busqueda-semantica')
def api_busqueda_semantica():
    """API para búsqueda semántica AJAX"""
    query = request.args.get('q', '')
    
    if not query or not busqueda_semantica.habilitado:
        return jsonify({'error': 'Consulta vacía o búsqueda semántica no disponible'}), 400
    
    try:
        resultados = busqueda_semantica.buscar_similar(query, top_k=10)
        
        response_data = []
        for costumbre, similitud in resultados:
            response_data.append({
                'id': costumbre.id,
                'ciudad': costumbre.ciudad,
                'tipo': costumbre.tipo,
                'contenido': costumbre.contenido,
                'similitud': round(similitud * 100, 1)  # Convertir a porcentaje
            })
        
        return jsonify({
            'resultados': response_data,
            'total': len(response_data),
            'query': query
        })
    
    except Exception as e:
        return jsonify({'error': f'Error en búsqueda: {str(e)}'}), 500

@app.route('/admin/generar-embeddings')
def generar_embeddings():
    """Endpoint para generar embeddings (solo desarrollo)"""
    if os.environ.get('RENDER'):
        return jsonify({'error': 'No disponible en producción'}), 403
    
    if not busqueda_semantica.habilitado:
        return jsonify({'error': 'OpenAI API no configurada'}), 400
    
    try:
        busqueda_semantica.generar_embeddings_faltantes()
        
        total_costumbres = Costumbre.query.count()
        con_embeddings = Costumbre.query.filter(Costumbre.embedding.isnot(None)).count()
        
        return jsonify({
            'success': True,
            'mensaje': 'Embeddings generados exitosamente',
            'total_costumbres': total_costumbres,
            'con_embeddings': con_embeddings
        })
    
    except Exception as e:
        return jsonify({'error': f'Error generando embeddings: {str(e)}'}), 500

@app.route('/admin/estado-embeddings')
def estado_embeddings():
    """Endpoint para verificar el estado de los embeddings"""
    total_costumbres = Costumbre.query.count()
    con_embeddings = Costumbre.query.filter(Costumbre.embedding.isnot(None)).count()
    sin_embeddings = total_costumbres - con_embeddings
    
    return jsonify({
        'total_costumbres': total_costumbres,
        'con_embeddings': con_embeddings,
        'sin_embeddings': sin_embeddings,
        'porcentaje_completado': round((con_embeddings / total_costumbres) * 100, 1) if total_costumbres > 0 else 0,
        'busqueda_semantica_habilitada': busqueda_semantica.habilitado
    })

@app.route('/debug')
def debug_info():
    """Página de debug para verificar el estado de la base de datos"""
    if not os.environ.get('RENDER'):  # Solo en desarrollo
        with app.app_context():
            total_records = Costumbre.query.count()
            all_records = Costumbre.query.limit(5).all()
            
            debug_data = {
                'total_records': total_records,
                'database_uri': app.config['SQLALCHEMY_DATABASE_URI'],
                'sample_records': [
                    {'ciudad': c.ciudad, 'tipo': c.tipo, 'contenido': c.contenido[:50] + '...'}
                    for c in all_records
                ],
                'environment': 'Local Development'
            }
            
            return f"""
            <h1>Debug Info</h1>
            <p><strong>Total records:</strong> {debug_data['total_records']}</p>
            <p><strong>Database URI:</strong> {debug_data['database_uri']}</p>
            <p><strong>Environment:</strong> {debug_data['environment']}</p>
            <h2>Sample Records:</h2>
            <ul>
            {''.join([f'<li><strong>{r["ciudad"]}</strong> - {r["tipo"]}: {r["contenido"]}</li>' for r in debug_data['sample_records']])}
            </ul>
            <a href="/">← Volver al inicio</a>
            """
@app.route('/cita/<int:costumbre_id>')
def generar_cita(costumbre_id):
    """Página para generar citas en diferentes formatos"""
    costumbre = Costumbre.query.get_or_404(costumbre_id)
    
    # URL actual para la cita
    url_actual = request.url_root.rstrip('/') + url_for('generar_cita', costumbre_id=costumbre_id)
    
    # Fecha actual para la cita
    fecha_consulta = datetime.now()
    
    # Generar diferentes formatos de cita
    citas = generar_formatos_cita(costumbre, fecha_consulta, url_actual)
    
    return render_template('cita_legal.html', 
                         costumbre=costumbre, 
                         citas=citas,
                         fecha_consulta=fecha_consulta)

@app.route('/api/cita/<int:costumbre_id>')
def api_generar_cita(costumbre_id):
    """API para generar citas en formato JSON"""
    formato = request.args.get('formato', 'apa')
    costumbre = Costumbre.query.get_or_404(costumbre_id)
    
    url_actual = request.url_root.rstrip('/') + url_for('generar_cita', costumbre_id=costumbre_id)
    fecha_consulta = datetime.now()
    
    citas = generar_formatos_cita(costumbre, fecha_consulta, url_actual)
    
    return jsonify({
        'costumbre_id': costumbre_id,
        'formato_solicitado': formato,
        'cita': citas.get(formato, citas['apa']),
        'todos_los_formatos': citas,
        'fecha_generacion': fecha_consulta.isoformat()
    })

def generar_formatos_cita(costumbre, fecha_consulta, url):
    """Genera citas en diferentes formatos académicos"""
    
    # Mes en español
    meses = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    
    dia = fecha_consulta.day
    mes = meses[fecha_consulta.month]
    año = fecha_consulta.year
    fecha_es = f"{dia} de {mes} de {año}"
    
    return {
        'apa': f"Costumbres Mercantiles de Colombia. ({año}). Costumbre mercantil de {costumbre.ciudad} - {costumbre.tipo}. Base de Datos de Costumbres Mercantiles de Colombia. Recuperado el {fecha_es}, de {url}",
        
        'chicago': f"\"Costumbre Mercantil de {costumbre.ciudad} - {costumbre.tipo}\". Base de Datos de Costumbres Mercantiles de Colombia. Consultado el {fecha_es}. {url}.",
        
        'mla': f"\"Costumbre Mercantil de {costumbre.ciudad} - {costumbre.tipo}\". Base de Datos de Costumbres Mercantiles de Colombia, {año}, {url}. Consultado el {fecha_es}.",
        
        'vancouver': f"Costumbres Mercantiles de Colombia. Costumbre mercantil de {costumbre.ciudad} - {costumbre.tipo} [Internet]. Colombia: Base de Datos de Costumbres Mercantiles; {año} [citado {fecha_es}]. Disponible en: {url}",
        
        'iso690': f"Costumbres Mercantiles de Colombia. Costumbre mercantil de {costumbre.ciudad} - {costumbre.tipo}. Base de Datos de Costumbres Mercantiles de Colombia [en línea]. {año} [consulta: {fecha_consulta.strftime('%Y-%m-%d')}]. Disponible en: {url}",
        
        'juridica_colombiana': f"COLOMBIA. Costumbre Mercantil de {costumbre.ciudad}. {costumbre.tipo}. En: Base de Datos de Costumbres Mercantiles de Colombia [en línea]. Bogotá: {año} [consultado el {fecha_es}]. Disponible en Internet: {url}"
    }

# Crear tablas al iniciar la aplicación
with app.app_context():
    db.create_all()
    
    # Cargar datos reales solo en Render (producción) o si la base está vacía
    if os.environ.get('RENDER') or Costumbre.query.count() == 0:
        try:
            from real_data import create_real_data
            create_real_data(app, db, Costumbre)
        except ImportError:
            print("⚠️ No se pudo importar real_data.py, intentando con datos de muestra...")
            try:
                from sample_data import create_sample_data
                create_sample_data(app, db, Costumbre)
            except ImportError:
                print("⚠️ No se pudieron cargar datos de respaldo")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = not os.environ.get('RENDER')
    app.run(debug=debug, host='0.0.0.0', port=port)
