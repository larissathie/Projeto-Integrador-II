from app import app, db, Usuario

with app.app_context():
    u = Usuario(
        cpf=11111111111,
        nome="Larissa",
        apartamento="101",
        email="gabriel@email.com",
        senha="1234",
        admin="sim",
    )
    db.session.add(u)
    db.session.commit()
    print("✅ Usuário de teste criado")
