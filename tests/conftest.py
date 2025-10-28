#Cria a app em modo teste, aponta o SQLAlchemy para sqlite:///:memory:, cria/derruba as tabelas por teste e expõe fixtures úteis.

import pytest
from projeto_integrador_ll.app import app as flask_app, db, Usuario


@pytest.fixture
def app():
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    with flask_app.app_context():
        db.create_all()
        db.session.expire_on_commit = False
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def usuario_padrao(app):
     with app.app_context():
        u = Usuario(
            cpf=11111111111,
            nome="Guilherme",
            apartamento="101",
            email="user@exemplo.com",
            senha="senha123",
            admin="sim",
        )
        db.session.add(u)
        db.session.commit()

        #Captura os valores antes de sair do contexto
        dados = {
            "cpf": u.cpf,
            "nome": u.nome,
            "apartamento": u.apartamento,
            "email": u.email,
            "senha": u.senha,
            "admin": u.admin,
        }
        return dados

@pytest.fixture
def sessao_logada(client, usuario_padrao):
    with client.session_transaction() as sess:
        sess["usuario_cpf"] = usuario_padrao["cpf"]
        sess["usuario_nome"] = usuario_padrao["nome"]
        sess["usuario_apartamento"] = usuario_padrao["apartamento"]
        sess["usuario_admin"] = usuario_padrao["admin"]
    return client
