from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

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
    else:
        return "Debug no disponible en producción", 404

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
