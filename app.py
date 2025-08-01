from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Conectar a la base de datos en la misma carpeta del proyecto
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
