DROP TABLE IF EXISTS visitantes_eventos;
DROP TABLE IF EXISTS visitantes_apartamento;
DROP TABLE IF EXISTS agendamento_evento;
DROP TABLE IF EXISTS moradores;

CREATE TABLE moradores (
    cpf INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    apartamento TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL,
    admin text Not Null
);

CREATE TABLE agendamento_evento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf_morador INTEGER NOT NULL,
    data DATE NOT NULL,
    local INTEGER NOT NULL,
    --Rever Salão de festas
    ambientes TEXT NOT NULL CHECK (ambientes IN ('churrasqueira', 'salao de festas')),
    apartamento TEXT NOT NULL,
    FOREIGN KEY (cpf_morador) REFERENCES moradores(cpf)
);

CREATE TABLE visitantes_apartamento (
    cpf_visitante INTEGER PRIMARY KEY,
    cpf_morador INTEGER NOT NULL,
    nome TEXT NOT NULL,
    apartamento TEXT NOT NULL,
    FOREIGN KEY (cpf_morador) REFERENCES moradores(cpf)
);

CREATE TABLE visitantes_eventos (
    id_visitante INTEGER PRIMARY KEY AUTOINCREMENT,    
    id_agendamento INTEGER NOT NULL,
    nome TEXT,
    apartamento TEXT,
    FOREIGN KEY (id_agendamento) REFERENCES agendamento_evento(id)
);