from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///costumbres.db'
db = SQLAlchemy(app)

class Costumbres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ciudad = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    contenido = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'<Costumbre {self.id}>'

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        costumbre_ciudad = request.form['ciudad'].upper()
        costumbre_tipo = request.form['tipo'].upper()
        costumbre_contenido = request.form['contenido'].upper()
        new_costumbre = Costumbres(ciudad=costumbre_ciudad, tipo=costumbre_tipo, contenido=costumbre_contenido)

        try:
            db.session.add(new_costumbre)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f"Error: {e}")
            return 'No se pudo agregar la costumbre'
    else:
        search_ciudad = request.args.get('search_ciudad')
        search_tipo = request.args.get('search_tipo')
        search_contenido = request.args.get('search_contenido')
        query = Costumbres.query

        if search_ciudad:
            query = query.filter(db.func.upper(Costumbres.ciudad).like(f'%{search_ciudad.upper()}%'))
        if search_tipo:
            query = query.filter(db.func.upper(Costumbres.tipo).like(f'%{search_tipo.upper()}%'))
        if search_contenido:
            query = query.filter(db.func.upper(Costumbres.contenido).like(f'%{search_contenido.upper()}%'))

        lascostumbres = query.order_by(Costumbres.ciudad).all()
        return render_template('index.html', lascostumbres=lascostumbres)
