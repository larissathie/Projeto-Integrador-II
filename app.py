from flask import Flask, render_template, request, url_for, flash, session, redirect, jsonify
import os
from datetime import datetime, timezone
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from flask_mail import Mail, Message
from werkzeug.exceptions import abort
from dotenv import load_dotenv
from werkzeug.exceptions import abort

load_dotenv()  # Carrega o .env

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  # string do Neon (com sslmode=require)
db = SQLAlchemy(app)



##Sistema de email para ajuda
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'grupopiunivespsala6grupo7@gmail.com'  
app.config['MAIL_PASSWORD'] = 'xxhchiyjtzalvbgs'  
app.config['MAIL_DEFAULT_SENDER'] = 'grupopiunivespsala6grupo7@gmail.com'

mail = Mail(app)

@app.route('/ajuda', methods=['GET', 'POST'])
def ajuda():
    if request.method == 'POST':
        nome = request.form['nome'].lower()
        email = request.form['email'].lower()
        telefone = request.form['telefone'].lower()
        mensagem = request.form['mensagem'].lower()

        msg = Message(subject='Nova mensagem do sistema de ajuda',
                      recipients=['grupopiunivespsala6grupo7@gmail.com'],  # E-mail de destino
                      body=f'Nome: {nome}\nEmail: {email}\nTelefone: {telefone}\n\nMensagem:\n{mensagem}')
        mail.send(msg)

        flash('Mensagem enviada com sucesso!', 'success')
        return redirect(url_for('ajuda'))
    return render_template('pagina_ajuda.html')



# Carregue a variável de ambiente (instale python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()

#Rota para o Recaptcha Google 
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
GOOGLE_RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

## Classes do banco de dados
class Usuario(db.Model):
    __tablename__ = 'moradores'
    cpf = db.Column(db.BigInteger, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.String(3), nullable=False)

class Familiar(db.Model):
    __tablename__ = 'visitantes_apartamento'
    cpf_visitante = db.Column(db.BigInteger, primary_key=True)
    cpf_morador = db.Column(db.BigInteger, db.ForeignKey('moradores.cpf'), nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)

    morador = db.relationship('Usuario', backref=db.backref('familiares', lazy=True))

class ConvidadoEvento(db.Model):
    __tablename__ = 'visitantes_eventos'
    id_visitante = db.Column(db.Integer, primary_key=True)
    id_agendamento = db.Column(db.Integer, db.ForeignKey('agendamento_evento.id'), nullable=False)   
    cpf = db.Column(db.String(14), nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)

class Espaco(db.Model):
    __tablename__ = 'agendamento_evento'    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cpf_morador = db.Column(db.BigInteger, nullable=False)
    data = db.Column(db.DateTime, nullable = False)
    local = db.Column(db.Integer)
    ambientes = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)
    convidados = db.relationship('ConvidadoEvento', backref='evento', cascade='all, delete-orphan')

##############################################################################################################
# Nova classe para Cadastro de Gastos
class Gasto(db.Model):
    __tablename__ = 'gastos_condominio'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    categoria = db.Column(db.String(50))
    data_gasto  = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())

# Nova classe para Cadastro de Entradas
class Entrada(db.Model):
    __tablename__ = 'entradas_condominio'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_entrada = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())

# Nova classe para Encomendas
class Encomenda(db.Model):
    __tablename__ = 'encomendas'
    id = db.Column(db.Integer, primary_key=True)
    apartamento_destino = db.Column(db.String(10), nullable=False)
    destinatario = db.Column(db.String(50), nullable=False)
    data_chegada = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pendente') # Pendente ou Retirado
##############################################################################################################
## Fim da classe de banco de dados

with app.app_context():
    db.create_all()

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
    #Verificação do reCAPTCHA
    recaptcha_response = request.form.get('g-recaptcha-response')
    
    if not recaptcha_response:
        return render_template('login.html', error="Por favor, complete a verificação de segurança (reCAPTCHA)!")
    
    # Validar reCAPTCHA com Google
    data = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
   }
    
    try:
        response = requests.post(GOOGLE_RECAPTCHA_VERIFY_URL, data=data)
        result = response.json()
        
        if not result.get('success'):
            # Aqui você pode verificar os códigos de erro específicos
            error_codes = result.get('error-codes', [])
            print(f"Erros reCAPTCHA: {error_codes}")
            
            if 'missing-input-response' in error_codes:
                error_msg = "Por favor, complete a verificação de segurança."
            else:
                error_msg = "Falha na verificação de segurança. Tente novamente."
            
            return render_template('login.html', error=error_msg)
            
    except Exception as e:
        print(f"Erro ao validar reCAPTCHA: {e}")
        return render_template('login.html', error="Erro na verificação de segurança. Tente novamente.")
    
  
    usuario = request.form['nomeUsuario'].lower()
    senha = request.form['senhaUsuario']
    
    if not usuario or not senha:
        return render_template('login.html', error="Por favor, preencha usuário e senha!")
    
    user = Usuario.query.filter_by(email=usuario, senha=senha).first()
    
    if user:
        session['usuario_cpf'] = user.cpf
        session['usuario_nome'] = user.nome
        session['usuario_apartamento'] = user.apartamento
        session['usuario_admin'] = user.admin

        if user.admin == 'sim':
            return redirect(url_for('pagina_admin'))
        else:
            return redirect(url_for('pagina_inicial'))
    else:
        return render_template('login.html', error="Usuário ou senha incorretos!")

#Rota para sucesso do loggin
@app.route('/pInicial')
def pagina_inicial():
    nome_usuario = session.get('usuario_nome')
    usuario_cpf = session.get('usuario_cpf')
    usuario_apartamento = session.get('usuario_apartamento')
    usuario_admin = session.get('usuario_admin')
    return render_template('pagina_inicial.html', nome=nome_usuario , cpf = usuario_cpf , apartamento = usuario_apartamento, admin = usuario_admin)

#Rota para sucesso do login admin
@app.route('/pInicial_admin')
def pagina_admin():
    nome_usuario = session.get('usuario_nome')
    usuario_cpf = session.get('usuario_cpf')
    usuario_apartamento = session.get('usuario_apartamento')
    usuario_admin = session.get('usuario_admin')
    return render_template('p_inicial_administrador.html', nome=nome_usuario , cpf = usuario_cpf , apartamento = usuario_apartamento, admin = usuario_admin)

#Rota para cadastro de moradores
@app.route('/cadastro_moradores')
def Cadastrar_moradores():
    nome_usuario = session.get('usuario_nome')
    usuario_cpf = session.get('usuario_cpf')
    usuario_apartamento = session.get('usuario_apartamento')
    usuario_admin = session.get('usuario_admin')
    moradores = Usuario.query.all()
    return render_template('p_cadastrar_morador.html', nome=nome_usuario , cpf = usuario_cpf , apartamento = usuario_apartamento, admin = usuario_admin, moradores=moradores)

#Rota para pesquisar acessos
@app.route('/Pesquisar_acessos')
def Pesquisa_acessos():
    nome_usuario = session.get('usuario_nome')
    usuario_cpf = session.get('usuario_cpf')
    usuario_apartamento = session.get('usuario_apartamento')
    usuario_admin = session.get('usuario_admin')
    return render_template('pesquisar_acessos.html', nome=nome_usuario , cpf = usuario_cpf , apartamento = usuario_apartamento, admin = usuario_admin)

#Rota para página cadastrar familiares
@app.route('/cadastrar_familiares', methods=['GET', 'POST'])
def cadastrar_familiares():
    nome_usuario = session.get('usuario_nome')
    cpf_morador = session.get('usuario_cpf')
    familiares = Familiar.query.filter_by(cpf_morador = cpf_morador).all()
    error = request.args.get('error')
    return render_template('p_cadastrar_familiares.html', nome=nome_usuario, familiares=familiares , error = error) 

# Rota para adicionar familiar (CORRIGIDA PARA BIGINT)
@app.route('/addFamiliar', methods=['GET','POST'])
def adicionarFamiliar():      
    if request.method == 'POST':     
        form_nome = request.form['nome'].lower()
        form_cpf = request.form['cpf']
        form_cpfMorador = session.get('usuario_cpf')  # Já deve ser BIGINT da session
        form_ap = session.get('usuario_apartamento')     
        
        # ✅ VALIDAÇÃO: Verificar se CPF tem 11 dígitos ANTES de converter
        if len(form_cpf) != 11 or not form_cpf.isdigit():
            flash('CPF deve conter exatamente 11 números!', 'error')
            return redirect(url_for('cadastrar_familiares'))
        
        # ✅ CORREÇÃO: Converter CPF para BIGINT
        try:
            cpf_visitante_int = int(form_cpf)  # ✅ Agora funciona com BIGINT
        except ValueError:
            flash('CPF do familiar deve conter apenas números!', 'error')
            return redirect(url_for('cadastrar_familiares'))

        # ✅ VALIDAÇÃO ADICIONAL: Garantir que é um CPF válido
        if cpf_visitante_int < 10000000000 or cpf_visitante_int > 99999999999:
            flash('CPF inválido!', 'error')
            return redirect(url_for('cadastrar_familiares'))
        
        # ✅ CORREÇÃO: Usar cpf_visitante_int na consulta
        familiar_existente = Familiar.query.filter_by(cpf_visitante=cpf_visitante_int).first()    
        
        if familiar_existente:
            flash('CPF já cadastrado!', 'error')
            return redirect(url_for('cadastrar_familiares'))
         
        if not form_nome:      
            flash('O nome é obrigatório!', 'error')
            return redirect(url_for('cadastrar_familiares'))
        else:          
            # ✅ CORREÇÃO: Usar cpf_visitante_int na criação
            familiar = Familiar(
                nome=form_nome,
                cpf_morador=form_cpfMorador, 
                cpf_visitante=cpf_visitante_int,  # ✅ AGORA É BIGINT
                apartamento=form_ap
            )
            db.session.add(familiar)
            db.session.commit()      
            flash('Familiar adicionado com sucesso!', 'success')
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

    eventos = Espaco.query.filter_by(cpf_morador=cpf_morador).all()
    todosEventos = Espaco.query.all()

    error = request.args.get('error')
    return render_template('cad_con_salaoF.html', nome=nome_usuario, familiares=familiares, eventos = eventos , todosEventos = todosEventos, error = error) 

#Rota para cadastro de evento no salão
@app.route('/cadastro_Salao', methods=['GET', 'POST'])
def CadEventoSalao():
    nome_usuario = session.get('usuario_nome')
    cpf_morador = session.get('usuario_cpf')
    ap_morador = session.get('usuario_apartamento')
    error = request.args.get('error')
    eventos = Espaco.query.filter_by(cpf_morador=cpf_morador).all()
    todosEventos = Espaco.query.filter(
        Espaco.ambientes == 'salao de festas',
        Espaco.data >= datetime.now()
    ).order_by(Espaco.data.asc()).all()

    if request.method == 'POST':
        try:
            dados = request.get_json()
            data_selecionada = dados.get('data_reserva')
            
            if data_selecionada:
                # Converter data
                data_convertida = data_selecionada.split(' GMT')[0]
                data_obj = datetime.strptime(data_convertida, '%a %b %d %Y %H:%M:%S')
                
                # VERIFICAR SE JÁ EXISTE EVENTO NESTA DATA
                evento_existente = Espaco.query.filter(
                    Espaco.ambientes == 'salao de festas',
                    Espaco.data == data_obj
                ).first()
                
                if evento_existente:
                    return jsonify({
                        'status': 'error', 
                        'message': f'Já existe um evento agendado para {data_obj.strftime("%d/%m/%Y")}!'
                    }), 400
                
                # SALVAR NO BANCO
                novo_evento = Espaco(
                    nome=nome_usuario,
                    cpf_morador=cpf_morador,
                    data=data_obj,
                    local=1,
                    ambientes='salao de festas',
                    apartamento=ap_morador
                )
                
                db.session.add(novo_evento)
                db.session.commit()               
                
                return jsonify({
                    'status': 'success', 
                    'message': f'Evento agendado para {data_obj.strftime("%d/%m/%Y")}!',
                    'data_salva': data_obj.strftime('%d/%m/%Y')
                })
            else:
                return jsonify({'status': 'error', 'message': 'Data não selecionada'}), 400
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return render_template('p_agend_salaoF.html',
                         nome=nome_usuario, 
                         cpf=cpf_morador, 
                         apartamento=ap_morador, 
                         eventos=eventos, 
                         todosEventos=todosEventos,
                         error=error)

## ROTA PARA DELETAR EVENTO
@app.route('/evento/<int:id>/deleteSalao', methods=('POST',))
def deleteEventoSalao(id):   
    EventoExcluido = get_eventos(id)       
    db.session.delete(EventoExcluido)
    db.session.commit()
    return redirect(url_for('CadEventoSalao'))

#Rota para página Churrasqueira
@app.route('/churrasqueira', methods=['GET', 'POST'])
def churrasqueira():
    nome_usuario = session.get('usuario_nome')
    cpf_morador = session.get('usuario_cpf')
    familiares = Familiar.query.filter_by(cpf_morador = cpf_morador).all()
    error = request.args.get('error')
    return render_template('cad_con_churrasqueira.html', nome=nome_usuario, familiares=familiares , error = error) 

### ROTA PARA CADASTRO DE EVENTO CHURRASQUEIRA
@app.route('/cadastro_churrasqueira', methods=['GET', 'POST'])
def cadEventoChurras():
    nome_usuario = session.get('usuario_nome')
    cpf_morador = session.get('usuario_cpf')
    ap_morador = session.get('usuario_apartamento')
    error = request.args.get('error')
    
    # Meus eventos da churrasqueira
    meus_eventos = Espaco.query.filter_by(
        cpf_morador=cpf_morador,
        ambientes='churrasqueira'
    ).order_by(Espaco.data.desc()).all()
    
    # Todos os eventos da churrasqueira (futuros)
    todosEventos = Espaco.query.filter(
        Espaco.ambientes == 'churrasqueira',
        Espaco.data >= datetime.now()
    ).order_by(Espaco.data.asc()).all()
    
    print(f"🎯 Churrasqueira - Meus eventos: {len(meus_eventos)}")
    print(f"🎯 Churrasqueira - Todos os eventos: {len(todosEventos)}")
    
    # SE FOR POST (JavaScript)
    if request.method == 'POST':
        try:
            dados = request.get_json()
            data_selecionada = dados.get('data_reserva')
            
            if data_selecionada:
                data_convertida = data_selecionada.split(' GMT')[0]
                data_obj = datetime.strptime(data_convertida, '%a %b %d %Y %H:%M:%S')
                
                # 🔥 VERIFICAR SE JÁ EXISTE CHURRASQUEIRA NESTA DATA
                evento_existente = Espaco.query.filter(
                    Espaco.ambientes == 'churrasqueira',
                    Espaco.data == data_obj
                ).first()
                
                if evento_existente:
                    return jsonify({
                        'status': 'error', 
                        'message': f'Já existe uma churrasqueira agendada para {data_obj.strftime("%d/%m/%Y")}!'
                    }), 400
                
                # 🔥 VERIFICAÇÃO OPCIONAL: Usuário já tem churrasqueira agendada?
                churras_usuario = Espaco.query.filter(
                    Espaco.ambientes == 'churrasqueira',
                    Espaco.cpf_morador == cpf_morador,
                    Espaco.data >= datetime.now()
                ).first()
                
                if churras_usuario:
                    return jsonify({
                        'status': 'error', 
                        'message': 'Você já possui uma churrasqueira agendada!'
                    }), 400
                
                # 🔥 VERIFICAR SE A DATA NÃO É NO PASSADO
                if data_obj < datetime.now():
                    return jsonify({
                        'status': 'error', 
                        'message': 'Não é possível agendar para datas passadas!'
                    }), 400
                
                # ✅ SALVAR COMO CHURRASQUEIRA
                novo_evento = Espaco(
                    nome=nome_usuario,
                    cpf_morador=cpf_morador,
                    data=data_obj,
                    local=2,  # Local da churrasqueira
                    ambientes='churrasqueira',
                    apartamento=ap_morador
                )
                
                db.session.add(novo_evento)
                db.session.commit()
                
                print(f"✅ Churrasqueira salva: {data_obj.strftime('%d/%m/%Y')}")
                
                return jsonify({
                    'status': 'success', 
                    'message': f'Churrasqueira agendada para {data_obj.strftime("%d/%m/%Y")}!'
                })
            else:
                return jsonify({'status': 'error', 'message': 'Data não selecionada'}), 400
                
        except Exception as e:
            print(f"❌ ERRO na churrasqueira: {e}")
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    # SE FOR GET (mostrar a página)
    return render_template('p_agend_churrasqueira.html', 
                         nome=nome_usuario, 
                         cpf=cpf_morador, 
                         apartamento=ap_morador, 
                         eventos=meus_eventos, 
                         todosEventos=todosEventos,
                         error=error)

## ROTA PARA DELETAR EVENTO
@app.route('/evento/<int:id>/deleteChurras', methods=('POST',))
def deleteEventoChurras(id):   
    EventoExcluido = get_eventos(id)       
    db.session.delete(EventoExcluido)
    db.session.commit()
    return redirect(url_for('cadEventoChurras'))

##Cadastro de convidados para enventos
## Rota para tela de convidados salao
@app.route('/cad_con_salaoF.html/<int:id>')
def cadastrar_visitantes_Salao(id):
    eventoCarregado = get_eventos(id) 
    convidadosCarregados = get_convidados(id)
    nome = session.get('usuario_nome')

    return render_template('cad_con_salaoF.html', evento = eventoCarregado , convidados = convidadosCarregados , nome=nome)

## ROTA PARA DELETAR CONVIDADO SALÃO
@app.route('/<int:id>/deleteConvidadoSalao', methods=('POST',))
def deleteConvidadoSalao(id):
    convidadoExcluido = get_convidado_unico(id)    
    idEvento = convidadoExcluido.id_agendamento 
    db.session.delete(convidadoExcluido)
    db.session.commit()
    
    return redirect(url_for('cadastrar_visitantes_Salao', id = idEvento))

## Rota para tela de convidados churrasco
@app.route('/cad_con_churrasqueira.html/<int:id>')
def cadastrar_visitantes_Churras(id):
    eventoCarregado = get_eventos(id) 
    convidadosCarregados = get_convidados(id)
    nome = session.get('usuario_nome')
    return render_template('cad_con_churrasqueira.html', evento = eventoCarregado , convidados = convidadosCarregados, nome=nome)

## Rota para adicionar visitantes ao evento
@app.route('/addVisitanteSalao/<int:id>' , methods=['GET','POST'])
def adicionarVisitanteSalao(id):
    if request.method == 'POST':
     
     eventoAtual = get_eventos(id)
     idEvento =  eventoAtual.id
     form_nome = request.form['nome'].lower()
     form_cpf = request.form['cpf'].lower()
     apartamento = eventoAtual.apartamento
     
    if not form_nome:      
      flash('O Nome é obrigatório!')
    else: 
           
      convidado = ConvidadoEvento(id_agendamento = idEvento, nome = form_nome, cpf = form_cpf , apartamento = apartamento)
      db.session.add(convidado)
      db.session.commit()
      return redirect(url_for('cadastrar_visitantes_Salao', id = idEvento))         
    return render_template('cad_con_salaoF.html')

## ROTA PARA DELETAR CONVIDADO SALÃO
@app.route('/<int:id>/deleteConvidadoChurras', methods=('POST',))
def deleteConvidadoChurras(id):
    convidadoExcluido = get_convidado_unico(id)    
    idEvento = convidadoExcluido.id_agendamento 
    db.session.delete(convidadoExcluido)
    db.session.commit()
    
    return redirect(url_for('cadastrar_visitantes_Churras', id = idEvento))

## Rota para adicionar visitantes ao evento
@app.route('/addVisitanteChurrasqueira/<int:id>' , methods=['GET','POST'])
def adicionarVisitanteChurras(id):
    if request.method == 'POST':
     
     eventoAtual = get_eventos(id)
     idEvento =  eventoAtual.id
     form_nome = request.form['nome'].lower()
     form_cpf = request.form['cpf'].lower()
     apartamento = eventoAtual.apartamento
     
    if not form_nome:      
      flash('O Nome é obrigatório!')
    else: 
           
      convidado = ConvidadoEvento(id_agendamento = idEvento, nome = form_nome , cpf = form_cpf ,apartamento = apartamento)
      db.session.add(convidado)
      db.session.commit()
      return redirect(url_for('cadastrar_visitantes_Churras', id = idEvento))         
    return render_template('cad_con_churrasqueira.html')

### ROTA PARA CRIAR USUÁRIOS / MORADORES
@app.route('/criar', methods=['GET','POST'])
def cadastrar_usuario():
    if request.method == 'POST':        
        form_nome = request.form['nome'].lower()
        form_email = request.form['email'].lower()
        form_cpf = request.form['cpf']
        form_ap = request.form['apartamento'] 
        form_senha = request.form['senha']    
        form_admin = request.form['usuario']   

        # Validações
        if not all([form_nome, form_email, form_cpf, form_ap, form_senha, form_admin]):
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('Cadastrar_moradores'))
        
        # ✅ VALIDAÇÃO: Verificar se CPF tem 11 dígitos ANTES de converter
        if len(form_cpf) != 11 or not form_cpf.isdigit():
            flash('CPF deve conter exatamente 11 números!', 'error')
            return redirect(url_for('Cadastrar_moradores'))
        
        # Converte CPF para int (BIGINT)
        try:
            cpf_int = int(form_cpf)  # ✅ Agora funciona com CPFs grandes
        except ValueError:
            flash('CPF deve conter apenas números!', 'error')
            return redirect(url_for('Cadastrar_moradores'))

        # ✅ VALIDAÇÃO ADICIONAL: Garantir que é um CPF válido (opcional)
        if cpf_int < 10000000000 or cpf_int > 99999999999:
            flash('CPF inválido!', 'error')
            return redirect(url_for('Cadastrar_moradores'))

        # Usar cpf_int na consulta
        usuario_existente = Usuario.query.filter_by(cpf=cpf_int).first()      
        if usuario_existente:            
            flash('CPF já cadastrado no sistema!', 'error')
            return redirect(url_for('Cadastrar_moradores'))
        
        # Verificar se email já existe
        email_existente = Usuario.query.filter_by(email=form_email).first()
        if email_existente:
            flash('Email já cadastrado no sistema!', 'error')
            return redirect(url_for('Cadastrar_moradores'))
        
        # Criar novo usuário
        try:
            novo_usuario = Usuario(
                cpf=cpf_int,  # ✅ Agora é BIGINT
                nome=form_nome, 
                apartamento=form_ap, 
                email=form_email, 
                senha=form_senha, 
                admin=form_admin
            )
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('Cadastrar_moradores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {str(e)}', 'error')
            return redirect(url_for('Cadastrar_moradores'))
    
    return redirect(url_for('Cadastrar_moradores'))

### ROTA PARA EXCLUIR USUÁRIOS / MORADORES
@app.route('/excluir_morador/<int:cpf>', methods=['POST'])
def excluir_morador(cpf):
    # Verificar se o usuário atual é admin
    if session.get('usuario_admin') != 'sim':
        flash('Apenas administradores podem excluir moradores!', 'error')
        return redirect(url_for('Cadastrar_moradores'))
    
    try:
        morador = Usuario.query.filter_by(cpf=cpf).first()
        
        if morador:
            # Impedir que o admin exclua a si mesmo
            if morador.cpf == session.get('usuario_cpf'):
                flash('Você não pode excluir seu próprio usuário!', 'error')
                return redirect(url_for('Cadastrar_moradores'))
            
            db.session.delete(morador)
            db.session.commit()
            flash('Morador excluído com sucesso!', 'success')
        else:
            flash('Morador não encontrado!', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir morador!', 'error')
    
    return redirect(url_for('Cadastrar_moradores'))

## ROTA PARA PESQUISAR ACESSO
@app.route('/pesquisaNome', methods=['GET','POST'])
def pesquisaAcesso():
    nome = session.get('usuario_nome')   
    if request.method == 'POST':
        form_nome = request.form['nome'].strip().lower() if request.form['nome'] else None
        form_cpf = request.form['cpf'].strip() if request.form['cpf'] else None
        
        # Se ambos os campos estão vazios
        if not form_nome and not form_cpf:
            flash('Preencha pelo menos um campo para pesquisar!', 'error')
            return render_template('pesquisar_acessos.html', nome=nome)
        
        # Pesquisa por CPF (tem prioridade)
        if form_cpf:
            try:
                cpf_int = int(form_cpf)
                
                # Buscar em Moradores
                morador = Usuario.query.filter_by(cpf=cpf_int).all()
                if morador:
                    tipoDeAcesso = 'Morador'
                    return render_template('pesquisar_acessos.html', pessoa=morador, tipoDePessoa=tipoDeAcesso)
                
                # Buscar em Familiares
                familiar = Familiar.query.filter_by(cpf_visitante=cpf_int).all()
                if familiar:
                    tipoDeAcesso = 'Visitante'
                    return render_template('pesquisar_acessos.html', pessoa=familiar, tipoDePessoa=tipoDeAcesso)
                
                # Buscar em Convidados (CPF é string aqui)
                convidado = ConvidadoEvento.query.filter_by(cpf=form_cpf).all()
                if convidado:
                    tipoDeAcesso = 'Convidado'
                    convidadoEncontrado = convidado[0] if convidado else None
                    eventoEncontrado = Espaco.query.filter_by(id=convidadoEncontrado.id_agendamento).first() if convidadoEncontrado else None
                    return render_template('pesquisar_acessos.html', pessoa=convidado, tipoDePessoa=tipoDeAcesso, evento=eventoEncontrado, nome=nome)
                    
            except ValueError:
                flash('CPF deve conter apenas números!', 'error')
                return render_template('pesquisar_acessos.html', nome=nome)
        
        # Pesquisa por NOME (se CPF não foi preenchido ou não encontrou)
        if form_nome:
            # Buscar em Moradores
            morador = Usuario.query.filter(Usuario.nome.ilike(f'%{form_nome}%')).all()
            if morador:
                tipoDeAcesso = 'Morador'
                return render_template('pesquisar_acessos.html', pessoa=morador, tipoDePessoa=tipoDeAcesso, nome=nome)
            
            # Buscar em Convidados
            convidado = ConvidadoEvento.query.filter(ConvidadoEvento.nome.ilike(f'%{form_nome}%')).all()
            if convidado:
                tipoDeAcesso = 'Convidado'
                convidadoEncontrado = convidado[0] if convidado else None
                eventoEncontrado = Espaco.query.filter_by(id=convidadoEncontrado.id_agendamento).first() if convidadoEncontrado else None
                return render_template('pesquisar_acessos.html', pessoa=convidado, tipoDePessoa=tipoDeAcesso, evento=eventoEncontrado, nome=nome)
            
            # Buscar em Familiares
            familiar = Familiar.query.filter(Familiar.nome.ilike(f'%{form_nome}%')).all()
            if familiar:
                tipoDeAcesso = 'Visitante'
                return render_template('pesquisar_acessos.html', pessoa=familiar, tipoDePessoa=tipoDeAcesso, nome=nome)
        
        # Se não encontrou nada
        flash('Nenhum resultado encontrado!', 'error')
        return render_template('pesquisar_acessos.html', nome=nome)
    
    return render_template('pesquisar_acessos.html', nome=nome)

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


# ROTA PARA ACESSAR TELA DE CADASTRO DE GASTOS (APENAS PARA ADMIN)
@app.route('/cadastrar_entrada', methods=['POST'])
def cadastrar_entrada():
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    
    nova_entrada = Entrada(descricao=descricao, valor=valor)
    db.session.add(nova_entrada)
    db.session.commit()
    flash('Entrada registrada!', 'success')
    return redirect(url_for('gestao_financeira'))



@app.route('/cadastrar_gasto', methods=['POST'])
def cadastrar_gasto():
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    categoria = request.form.get('categoria')
    
    novo_gasto = Gasto(descricao=descricao, valor=valor, categoria=categoria)
    db.session.add(novo_gasto)
    db.session.commit()
    flash('Gasto registrado!', 'success')
    return redirect(url_for('gestao_financeira'))

@app.route('/gestao_financeira')
def gestao_financeira():
    mes_entrada = request.args.get('filtro_entrada')
    mes_saida = request.args.get('filtro_saida')

    query_entradas = Entrada.query
    query_gastos = Gasto.query

    # Aplicar filtros
    if mes_entrada:
        ano, mes = mes_entrada.split('-')
        query_entradas = query_entradas.filter(extract('year', Entrada.data_entrada) == int(ano), extract('month', Entrada.data_entrada) == int(mes))
    
    if mes_saida:
        ano, mes = mes_saida.split('-')
        query_gastos = query_gastos.filter(extract('year', Gasto.data_gasto) == int(ano), extract('month', Gasto.data_gasto) == int(mes))

    # Executa as buscas
    lista_entradas = query_entradas.all()
    lista_gastos = query_gastos.all()

    # CÁLCULO DOS TOTAIS    
    total_entradas = sum(float(e.valor) for e in lista_entradas)
    total_gastos = sum(float(g.valor) for g in lista_gastos)

    return render_template('p_cadastrar_gastos.html', 
                           entradas=lista_entradas, 
                           gastos=lista_gastos,
                           total_entradas=total_entradas, 
                           total_gastos=total_gastos,     
                           nome=session.get('usuario_nome'))


# Rota para Excluir Gasto
@app.route('/excluir_gasto/<int:id>', methods=['POST'])
def excluir_gasto(id):
    if session.get('usuario_admin') != 'sim':
        abort(403)
    
    gasto = Gasto.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    flash('Gasto excluído com sucesso!', 'success')
    return redirect(url_for('gestao_financeira'))

# Rota para Editar Gasto (Processamento)
@app.route('/editar_gasto/<int:id>', methods=['POST'])
def editar_gasto(id):
    if session.get('usuario_admin') != 'sim':
        abort(403)
        
    gasto = Gasto.query.get_or_404(id)
    gasto.descricao = request.form['descricao']
    gasto.valor = request.form['valor']
    gasto.categoria = request.form['categoria']
    
    db.session.commit()
    flash('Gasto atualizado com sucesso!', 'success')
    return redirect(url_for('gestao_financeira'))

# Rota para Editar Entrada (Processamento)
@app.route('/editar_entrada/<int:id>', methods=['POST'])
def editar_entrada(id):
    if session.get('usuario_admin') != 'sim':
        abort(403)
        
    entrada = Entrada.query.get_or_404(id)
    entrada.descricao = request.form['descricao']
    entrada.valor = request.form['valor']
    
    db.session.commit()
    flash('Receita atualizada com sucesso!', 'success')
    return redirect(url_for('gestao_financeira'))

# Rota para Excluir Entrada
@app.route('/excluir_entrada/<int:id>', methods=['POST'])
def excluir_entrada(id):
    if session.get('usuario_admin') != 'sim':
        abort(403)
    
    entrada = Entrada.query.get_or_404(id)
    db.session.delete(entrada)
    db.session.commit()
    flash('Receita excluída!', 'success')
    return redirect(url_for('gestao_financeira'))

# ROTA PARA ACESSAR TELA DE CHEGADA DE ENCOMENDAS
@app.route('/encomendas', methods=['GET', 'POST'])
def encomendas():
    if session.get('usuario_admin') != 'sim':
        flash('Acesso negado!', 'error')
        return redirect(url_for('pagina_inicial'))

    if request.method == 'POST':
        apartamento = request.form['apartamento']
        destinatario = request.form['destinatario']
        
        nova_encomenda = Encomenda(
            apartamento_destino=apartamento,
            destinatario=destinatario,
            status='Pendente'
        )
        db.session.add(nova_encomenda)
        db.session.commit()
        flash('Encomenda registrada! O morador será avisado pelo App.', 'success')
        return redirect(url_for('encomendas'))

    # Filtra para exibir apenas as que estão com status 'Pendente'
    encomendas_pendentes = Encomenda.query.filter_by(status='Pendente').order_by(Encomenda.data_chegada.desc()).all()
    
    nome_usuario = session.get('usuario_nome')
    # Passamos a lista filtrada para o HTML
    return render_template('p_encomendas.html', nome=nome_usuario, encomendas=encomendas_pendentes)

# Rota para o morador/admin marcar como "Retirado"
@app.route('/retirar_encomenda/<int:id>', methods=['POST'])
def retirar_encomenda(id):
    encomenda = Encomenda.query.get_or_404(id)
    encomenda.status = 'Retirado'
    db.session.commit()
    flash('Status da encomenda atualizado!', 'success')
    return redirect(url_for('encomendas'))

# FIM DA ROTA DE CADASTRO DE ENCOMENDAS 
@app.route('/financeiro_morador')
def financeiro_morador():
    # Verifica se o usuário está logado
    if 'usuario_cpf' not in session:
        return redirect(url_for('index'))

    mes_referencia = request.args.get('filtro_mes')
    query_entradas = Entrada.query
    query_gastos = Gasto.query

    if mes_referencia:
        ano, mes = mes_referencia.split('-')
        query_entradas = query_entradas.filter(extract('year', Entrada.data_entrada) == int(ano), extract('month', Entrada.data_entrada) == int(mes))
        query_gastos = query_gastos.filter(extract('year', Gasto.data_gasto) == int(ano), extract('month', Gasto.data_gasto) == int(mes))

    lista_entradas = query_entradas.order_by(Entrada.data_entrada.desc()).all()
    lista_gastos = query_gastos.order_by(Gasto.data_gasto.desc()).all()

    total_in = sum(float(e.valor) for e in lista_entradas)
    total_out = sum(float(g.valor) for g in lista_gastos)

    return render_template('p_financeiro_morador.html', 
                           entradas=lista_entradas, 
                           gastos=lista_gastos,
                           total_entradas=total_in,
                           total_gastos=total_out,
                           nome=session.get('usuario_nome'))

## Rota para encomendas
@app.route('/encomendas_morador')
def listar_encomendas():
    if 'usuario_cpf' not in session:
        return redirect(url_for('index'))
    
    # O morador só deve ver as encomendas destinadas ao seu próprio apartamento
    apartamento_usuario = session.get('usuario_apartamento')
    
    # Busca encomendas pendentes e retiradas para aquele apartamento
    minhas_encomendas = Encomenda.query.filter_by(apartamento_destino=apartamento_usuario).order_by(Encomenda.data_chegada.desc()).all()
    
    return render_template('p_encomendas_morador.html', 
                           encomendas=minhas_encomendas, 
                           nome=session.get('usuario_nome'))


# Rota para sair da página
@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('index'))  

# --- ROTA DE API PARA GASTOS ---
@app.route('/api/financeiro/relatorio', methods=['GET'])
def api_financeiro_relatorio():
    entradas = Entrada.query.all()
    gastos = Gasto.query.all()

    dados_entradas = [
        {"id": e.id, "descricao": e.descricao, "valor": float(e.valor), "data": e.data_entrada.strftime('%Y-%m-%d')} 
        for e in entradas
    ]

    dados_gastos = [
        {"id": g.id, "descricao": g.descricao, "valor": float(g.valor), "categoria": g.categoria, "data": g.data_gasto.strftime('%Y-%m-%d')} 
        for g in gastos
    ]

    return jsonify({
        "status": "sucesso",
        "resumo": {
            "total_entradas": sum(float(e.valor) for e in entradas),
            "total_saidas": sum(float(g.valor) for g in gastos),
            "saldo_atual": sum(float(e.valor) for e in entradas) - sum(float(g.valor) for g in gastos)
        },
        "detalhes": {"entradas": dados_entradas, "saidas": dados_gastos}
    })


# --- ROTA DE API PARA ENCOMENDAS ---
@app.route('/api/encomendas/<string:apartamento>', methods=['GET'])
def api_encomendas(apartamento):
    # Busca encomendas apenas daquele apartamento que estão pendentes
    encomendas_morador = Encomenda.query.filter_by(
        apartamento_destino=apartamento, 
        status='Pendente'
    ).all()
    
    lista = []
    for enc in encomendas_morador:
        lista.append({
            'id': enc.id,
            'destinatario': enc.destinatario,
            'data': enc.data_chegada.strftime('%d/%m/%Y %H:%M')
        })
    
    return jsonify(lista)


####### FUNÇÕES
### FUNÇÃO GET FAMILIAR
def get_familiar(familiar_cpf):
    familiar = Familiar.query.filter_by(cpf_visitante = familiar_cpf ).first()
    if familiar is None:
        abort(484)
    return familiar

### FUNÇÃO GET EVENTOS
def get_eventos(id):
    eventos = Espaco.query.filter_by(id = id).first()
    if eventos is None:
        abort(484)
    return eventos

### FUNÇÃO GET CONVIDADOS   
def get_convidados(id_agendamento):
    convidados = ConvidadoEvento.query.filter_by(id_agendamento = id_agendamento).all()
    if convidados is None:
        abort(484)
    return convidados

### FUNÇÃO GET CONVIDADO UNICO  
def get_convidado_unico(idConvidado):
    convidadoUnico = ConvidadoEvento.query.filter_by(id_visitante = idConvidado).first()
    if convidadoUnico is None:
        abort(484)
    return convidadoUnico



if __name__ == '__main__':
    app.run(debug=True)
