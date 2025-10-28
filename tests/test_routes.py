from app import db, Usuario


def test_index_renders_login_page(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    corpo = resposta.get_data(as_text=True)
    assert "<title>Login</title>" in corpo


def test_login_com_campos_vazios_retorna_login(client):
    resposta = client.post(
        "/login",
        data={"nomeUsuario": "", "senhaUsuario": ""},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    corpo = resposta.get_data(as_text=True)
    assert "<form method=\"POST\" action=\"/login\"" in corpo


def test_login_admin_redireciona_para_pagina_admin(client):
    usuario = Usuario(
        cpf=111111111,
        nome="admin",
        apartamento="101",
        email="admin@condo.com",
        senha="segredo",
        admin="sim",
    )
    db.session.add(usuario)
    db.session.commit()

    resposta = client.post(
        "/login",
        data={"nomeUsuario": "admin@condo.com", "senhaUsuario": "segredo"},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    corpo = resposta.get_data(as_text=True)
    assert "Cadastrar Morador" in corpo


def test_criar_usuario_persistente_no_banco(client):
    resposta = client.post(
        "/criar",
        data={
            "nome": "Maria da Silva",
            "email": "maria@example.com",
            "cpf": "222222222",
            "apartamento": "202",
            "senha": "123456",
            "usuario": "nao",
        },
    )

    assert resposta.status_code == 302
    criado = Usuario.query.filter_by(email="maria@example.com").one()
    assert criado.nome == "maria da silva"
    assert criado.admin == "nao"


def test_logout_limpa_sessao(client):
    with client.session_transaction() as flask_session:
        flask_session["usuario_nome"] = "Convidado"

    resposta = client.get("/logout")

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")

    with client.session_transaction() as flask_session:
        assert "usuario_nome" not in flask_session
