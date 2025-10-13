import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()


cur.execute("INSERT INTO moradores (cpf, nome, apartamento, email, senha , admin) VALUES (?, ?, ?, ?, ?, ?)",
            (22587939745, 'gabriel', '101', 'gabriel@email.com', '1234' , 'nao'))

cur.execute("INSERT INTO moradores (cpf, nome, apartamento, email, senha , admin) VALUES (?, ?, ?, ?, ?, ?)",
            (28964851257, 'fabiana', '102', 'fabiana@email.com', '5678' , 'nao'))

cur.execute("INSERT INTO visitantes_apartamento (cpf_visitante, cpf_morador, nome, apartamento) VALUES (?, ?, ?, ?)",
            (22587939745, 1231233, 'visitante', '101'))

cur.execute("INSERT INTO moradores (cpf, nome, apartamento, email, senha , admin) VALUES (?, ?, ?, ?, ?, ?)",
            (99999999999, 'admin', '999', 'admin@admin.com', 'admin', 'sim'))



connection.commit()
connection.close()
print("Banco criado com sucesso com dados de teste.")
