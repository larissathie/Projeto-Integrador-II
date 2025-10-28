#Valida listagem e inclusão de familiar usando a sessão autenticada.

from projeto_integrador_ll.app import db, Familiar

def test_pagina_cadastrar_familiares_renderiza(sessao_logada):
    resp = sessao_logada.get("/cadastrar_familiares")
    assert resp.status_code == 200
    assert b"familia" in resp.data.lower()

def test_adicionar_familiar_fluxo_basico(sessao_logada):
    # Inclui um familiar novo
    resp = sessao_logada.post(
        "/addFamiliar",
        data={"nome": "maria", "cpf": "22222222222"},
        follow_redirects=False,
    )
    # Deve redirecionar de volta à página de cadastro
    assert resp.status_code in (302, 303)
    assert "/cadastrar_familiares" in resp.headers.get("Location", "")

    #usa a aplicação do cliente de teste, sem importar `app`
    with sessao_logada.application.app_context():
        f = Familiar.query.filter_by(cpf_visitante=22222222222).first()
        assert f is not None
        assert f.nome == "maria"
