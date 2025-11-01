from flask import Flask, render_template, request, url_for, flash, session, redirect, jsonify
import os
from datetime import datetime
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import abort
from dotenv import load_dotenv

load_dotenv()  # Carrega o .env

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  # string do Neon (com sslmode=require)
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
    cpf = db.Column(db.String(14), nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)

class Espaco(db.Model):
    __tablename__ = 'agendamento_evento'    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cpf_morador = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, nullable = False)
    local = db.Column(db.Integer)
    ambientes = db.Column(db.String(50), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)
    convidados = db.relationship('ConvidadoEvento', backref='evento', cascade='all, delete-orphan')
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

        # Verifica se o usuário é admin
        if user.admin == 'sim':
            print('2 - Admin')
            return redirect(url_for('pagina_admin'))  # Redireciona para página de admin
        else:
            print('2 - Usuário normal')
            return redirect(url_for('pagina_inicial'))  # Redireciona para página normal
        #print('2')
        #return redirect(url_for('pagina_inicial')) 
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

# Rota para adicionar familiar (CORRIGIDA)
@app.route('/addFamiliar', methods=['GET','POST'])
def adicionarFamiliar():      
    if request.method == 'POST':     
        form_nome = request.form['nome'].lower()
        form_cpf = request.form['cpf']
        form_cpfMorador = session.get('usuario_cpf')  # Já deve ser int da session
        form_ap = session.get('usuario_apartamento')     
        
        # ✅ CORREÇÃO: Converter CPF para int
        try:
            cpf_visitante_int = int(form_cpf)
        except ValueError:
            flash('CPF do familiar deve conter apenas números!', 'error')
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
                cpf_visitante=cpf_visitante_int,  # AGORA É INT
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

### Cadastrar evento salão
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

    # SE FOR POST (só vai vir do JavaScript)
    if request.method == 'POST':
        try:
            # Sempre vem como JSON do JavaScript
            dados = request.get_json()
            data_selecionada = dados.get('data_reserva')
            
            print(f"🎯 DADOS DO JAVASCRIPT:")
            print(f"👤 Usuário: {nome_usuario}")
            print(f" Apartamento: {ap_morador}")
            print(f"📅 Data: {data_selecionada}")
            
            if data_selecionada:
                # Converter data
                data_convertida = data_selecionada.split(' GMT')[0]
                data_obj = datetime.strptime(data_convertida, '%a %b %d %Y %H:%M:%S')
                
                print(f"📅 DATA CONVERTIDA: {data_obj.strftime('%d/%m/%Y')}")
                
                # SALVAR NO BANCO
                novo_evento = Espaco(
                     nome = nome_usuario,
                     cpf_morador=cpf_morador,
                     data=data_obj,
                     local = 1,
                     ambientes = 'salao de festas',
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
            
    
    # SE FOR GET (mostrar a página)
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


###ROTA PARA CADASTRO DE EVENTO CHURRASQUEIRA
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
    return render_template('cad_con_salaoF.html', evento = eventoCarregado , convidados = convidadosCarregados)

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
    return render_template('cad_con_churrasqueira.html', evento = eventoCarregado , convidados = convidadosCarregados)


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
        # Corrigindo os nomes dos campos (devem ser iguais ao "name" no HTML)
        form_nome = request.form['nome'].lower()
        form_email = request.form['email'].lower()
        form_cpf = request.form['cpf']
        form_ap = request.form['apartamento'] 
        form_senha = request.form['senha']    
        form_admin = request.form['usuario']   

        # Validações
        if not all([form_nome, form_email, form_cpf, form_ap, form_senha, form_admin]):
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template('p_cadastrar_morador.html', error="Todos os campos são obrigatórios!")
        
        # ✅ CORREÇÃO: Converter CPF para int e validar
        try:
            cpf_int = int(form_cpf)
        except ValueError:
            flash('CPF deve conter apenas números!', 'error')
            return render_template('p_cadastrar_morador.html', error="CPF deve conter apenas números!")

        # ✅ CORREÇÃO: Usar cpf_int na consulta
        usuario_existente = Usuario.query.filter_by(cpf=cpf_int).first()      
        if usuario_existente:            
            flash('CPF já cadastrado no sistema!', 'error')
            return render_template('p_cadastrar_morador.html', error="CPF Já Cadastrado!")
        
        # Verificar se email já existe
        email_existente = Usuario.query.filter_by(email=form_email).first()
        if email_existente:
            flash('Email já cadastrado no sistema!', 'error')
            return render_template('p_cadastrar_morador.html', error="Email Já Cadastrado!")

        # ✅ CORREÇÃO: Usar cpf_int na criação do usuário
        # Criar novo usuário
        try:
            novo_usuario = Usuario(
                cpf=cpf_int,  # ✅ AGORA É INT
                nome=form_nome, 
                apartamento=form_ap, 
                email=form_email, 
                senha=form_senha, 
                admin=form_admin
            )
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastrar_usuario'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {str(e)}', 'error')
            return render_template('p_cadastrar_morador.html', error="Erro ao cadastrar usuário")    
    
    return render_template('p_cadastrar_morador.html')




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
    if request.method == 'POST':
        form_nome = request.form['nome'].strip().lower() if request.form['nome'] else None
        form_cpf = request.form['cpf'].strip() if request.form['cpf'] else None
        
        # Se ambos os campos estão vazios
        if not form_nome and not form_cpf:
            flash('Preencha pelo menos um campo para pesquisar!', 'error')
            return render_template('pesquisar_acessos.html')
        
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
                    tipoDeAcesso = 'Familiar'
                    return render_template('pesquisar_acessos.html', pessoa=familiar, tipoDePessoa=tipoDeAcesso)
                
                # Buscar em Convidados (CPF é string aqui)
                convidado = ConvidadoEvento.query.filter_by(cpf=form_cpf).all()
                if convidado:
                    tipoDeAcesso = 'Convidado'
                    convidadoEncontrado = convidado[0] if convidado else None
                    eventoEncontrado = Espaco.query.filter_by(id=convidadoEncontrado.id_agendamento).first() if convidadoEncontrado else None
                    return render_template('pesquisar_acessos.html', pessoa=convidado, tipoDePessoa=tipoDeAcesso, evento=eventoEncontrado)
                    
            except ValueError:
                flash('CPF deve conter apenas números!', 'error')
                return render_template('pesquisar_acessos.html')
        
        # Pesquisa por NOME (se CPF não foi preenchido ou não encontrou)
        if form_nome:
            # Buscar em Moradores
            morador = Usuario.query.filter(Usuario.nome.ilike(f'%{form_nome}%')).all()
            if morador:
                tipoDeAcesso = 'Morador'
                return render_template('pesquisar_acessos.html', pessoa=morador, tipoDePessoa=tipoDeAcesso)
            
            # Buscar em Convidados
            convidado = ConvidadoEvento.query.filter(ConvidadoEvento.nome.ilike(f'%{form_nome}%')).all()
            if convidado:
                tipoDeAcesso = 'Convidado'
                convidadoEncontrado = convidado[0] if convidado else None
                eventoEncontrado = Espaco.query.filter_by(id=convidadoEncontrado.id_agendamento).first() if convidadoEncontrado else None
                return render_template('pesquisar_acessos.html', pessoa=convidado, tipoDePessoa=tipoDeAcesso, evento=eventoEncontrado)
            
            # Buscar em Familiares
            familiar = Familiar.query.filter(Familiar.nome.ilike(f'%{form_nome}%')).all()
            if familiar:
                tipoDeAcesso = 'Familiar'
                return render_template('pesquisar_acessos.html', pessoa=familiar, tipoDePessoa=tipoDeAcesso)
        
        # Se não encontrou nada
        flash('Nenhum resultado encontrado!', 'error')
        return render_template('pesquisar_acessos.html')
    
    return render_template('pesquisar_acessos.html')

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

# Rota para sair da página
@app.route('/logout')
def logout():
    session.clear()  # limpa a sessão do usuário
    return redirect(url_for('index'))  # volta para a tela de login (que está na rota '/')

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
