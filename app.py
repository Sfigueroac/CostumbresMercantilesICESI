from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from urllib.parse import quote

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

    ciudad_q = request.args.get('search_ciudad', '')
    tipo_q = request.args.get('search_tipo', '')
    contenido_q = request.args.get('search_contenido', '')

    resultados = Costumbre.query.filter(
        Costumbre.ciudad.ilike(f'%{ciudad_q}%'),
        Costumbre.tipo.ilike(f'%{tipo_q}%'),
        Costumbre.contenido.ilike(f'%{contenido_q}%')
    ).all()

    return render_template('index.html', lascostumbres=resultados)

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
