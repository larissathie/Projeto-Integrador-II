
from flask import Flask, render_template, request,url_for,flash,redirect
import os, datetime
import requests
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask import session
from werkzeug.exceptions import abort

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir,"database.db"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
db = SQLAlchemy(app)

# Carregue a variável de ambiente (instale python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()

#Rota para o Recaptcha Google 
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
GOOGLE_RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

## Classes do banco de dados
class Usuario(db.Model):
    __tablename__ = 'moradores'
    cpf = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.String(3), nullable=False)

class Familiar(db.Model):
    __tablename__ = 'visitantes_apartamento'
    cpf_visitante = db.Column(db.Integer, primary_key=True)
    cpf_morador = db.Column(db.Integer, db.ForeignKey('moradores.cpf'), nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)

    morador = db.relationship('Usuario', backref=db.backref('familiares', lazy=True))

class ConvidadoEvento(db.Model):
    __tablename__ = 'visitantes_eventos'
    id_visitante = db.Column(db.Integer, primary_key=True)
    id_agendamento = db.Column(db.Integer, db.ForeignKey('agendamento_evento.id'), nullable=False)   
    nome = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)

class Espaco(db.Model):
    __tablename__ = 'agendamento_evento'
    id = db.Column(db.Integer, primary_key=True)
    cpf_morador = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, nullable = False)
    local = db.Column(db.Integer)
    ambientes = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)
    convidados = db.relationship('ConvidadoEvento', backref='evento', cascade='all, delete-orphan')
## Fim da classe de banco de dados

#Rotas para as páginas
@app.route('/')
def index():
   return render_template('login.html')

#Rota para pagina de ajuda
@app.route('/ajuda')
def pagAjuda():
    return render_template ('pagina_ajuda.html')

#Rota para login
@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['nomeUsuario'].lower()
    senha = request.form['senhaUsuario']
    if not usuario or not senha:
        print('1')
        return render_template('login.html', error="Por favor, preencha usuário e senha!")
    user = Usuario.query.filter_by(email=usuario, senha=senha).first()
    if user:
        session['usuario_cpf'] = user.cpf
        session['usuario_nome'] = user.nome
        session['usuario_apartamento'] = user.apartamento #apresenta o nome do usuário no lado direito da tela
        session['usuario_admin'] = user.admin
        print('2')
        return redirect(url_for('pagina_inicial')) 
    else:
        print('3')
        return render_template('login.html', error="Usuário ou senha incorretos!")

#Rota para sucesso do loggin
@app.route('/pInicial')
def pagina_inicial():
    nome_usuario = session.get('usuario_nome')
    usuario_cpf = session.get('usuario_cpf')
    usuario_apartamento = session.get('usuario_apartamento')
    usuario_admin = session.get('usuario_admin')
    return render_template('pagina_inicial.html', nome=nome_usuario , cpf = usuario_cpf , apartamento = usuario_apartamento, admin = usuario_admin)

#Rota para página cadastrar familiares
@app.route('/cadastrar_familiares', methods=['GET', 'POST'])
def cadastrar_familiares():
    nome_usuario = session.get('usuario_nome')
    cpf_morador = session.get('usuario_cpf')
    familiares = Familiar.query.filter_by(cpf_morador = cpf_morador).all()
    error = request.args.get('error')
    return render_template('p_cadastrar_familiares.html', nome=nome_usuario, familiares=familiares , error = error) 

#Rota para adicionar familiar (Funcionando)
@app.route('/addFamiliar' , methods=['GET','POST'])
def adicionarFamiliar():      
    if request.method == 'POST':     
     form_nome = request.form['nome'].lower()
     form_cpf = request.form['cpf']
     form_cpfMorador = session.get('usuario_cpf')
     form_ap = session.get('usuario_apartamento')     
     familiar_existente = Familiar.query.filter_by(cpf_visitante=form_cpf).first()    
     if familiar_existente:
        return redirect(url_for('cadastrar_familiares', error="CPF Já Cadastrado!"))         
    if not form_nome:      
      flash('O título é obrigatório!')
    else:          
      familiar = Familiar(nome = form_nome ,cpf_morador = form_cpfMorador ,cpf_visitante = form_cpf , apartamento = form_ap)
      db.session.add(familiar)
      db.session.commit()      
      return redirect(url_for('cadastrar_familiares'))         
    return render_template('cadastrar_familiares')


#Rota para editar um familiar

@app.route('/<int:cpf>/delete', methods=('POST',))
def delete(cpf):
    familiarExcluido = get_familiar(cpf)
    db.session.delete(familiarExcluido)
    db.session.commit()    
    return redirect(url_for('cadastrar_familiares'))



#Rota para página salão de festas
@app.route('/salaoDeFestas', methods=['GET', 'POST'])
def salaoDeFestas():
    nome_usuario = session.get('usuario_nome')
    cpf_morador = session.get('usuario_cpf')
    familiares = Familiar.query.filter_by(cpf_morador = cpf_morador).all()
    error = request.args.get('error')
    return render_template('cad_con_salaoF.html', nome=nome_usuario, familiares=familiares , error = error) 

#Rota para página Churrasqueira
@app.route('/churrasqueira', methods=['GET', 'POST'])
def churrasqueira():
    nome_usuario = session.get('usuario_nome')
    cpf_morador = session.get('usuario_cpf')
    familiares = Familiar.query.filter_by(cpf_morador = cpf_morador).all()
    error = request.args.get('error')
    return render_template('cad_con_churrasqueira.html', nome=nome_usuario, familiares=familiares , error = error) 

@app.route('/seu-formulario', methods=['GET', 'POST'])
def handle_form():
    if request.method == 'POST':
        # Recebe o token do reCAPTCHA do formulário
        recaptcha_response = request.form.get('g-recaptcha-response')

        if recaptcha_response:
            # Dados para enviar ao Google para validação
            data = {
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            # Faz a requisição de validação para a API do Google
            response = requests.post(GOOGLE_RECAPTCHA_VERIFY_URL, data=data)
            result = response.json()
            if result.get('success'):
                # Validação bem-sucedida! Continue o processo
                return "Formulário enviado com sucesso e reCAPTCHA verificado!"
            else:
                # Falha na validação do reCAPTCHA
                return "Erro na validação do reCAPTCHA. Tente novamente."
        return "Token reCAPTCHA não recebido."
    return render_template('seu_formulario.html') # Renderiza o formulário





####### FUNÇÕES
### FUNÇÃO GET FAMILIAR
def get_familiar(familiar_cpf):
    familiar = Familiar.query.filter_by(cpf_visitante = familiar_cpf ).first()
    if familiar is None:
        abort(484)
    return familiar


if __name__ == '__main__':
    app.run(debug=True)

    #Fim da rota Recaptcha Google 