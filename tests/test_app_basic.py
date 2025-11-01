#Testes básicos de rota inicial, login, JSON de reserva

import json

def test_index_carrega_login(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"login" in resp.data.lower()

def test_login_campos_obrigatorios(client):
    resp = client.post("/login", data={"nomeUsuario": "", "senhaUsuario": ""})
    assert resp.status_code == 200
    html = resp.data.lower()
    assert b'<form' in html
    assert b'name="nomeusuario"' in html  # campo do formulário

def test_login_sucesso_redireciona(client, usuario_padrao):
    resp = client.post(
        "/login",
        data={"nomeUsuario": "user@exemplo.com", "senhaUsuario": "senha123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/pInicial" in resp.headers.get("Location", "")

def test_processar_reserva_json_ok(sessao_logada):
    payload = {"data_reserva": "Mon Jan 06 2025 10:00:00 GMT-0300"}
    resp = sessao_logada.post(
        "/cadastro_Salao",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert body["data_salva"] == "06/01/2025" 


def test_processar_reserva_sem_json(sessao_logada):
    resp = sessao_logada.post("/cadastro_Salao", data="sem json")
    assert resp.status_code == 400