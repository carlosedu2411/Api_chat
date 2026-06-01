import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Substitua pela sua URL diretamente se não estiver usando arquivo .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgres-production-81533.up.railway.app")

def conectar():
    return psycopg2.connect(DATABASE_URL)

conn = conectar()
cursor = conn.cursor()

# Criar tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE,
    senha TEXT
);
""")

# Criar tabela de mensagens
cursor.execute("""
CREATE TABLE IF NOT EXISTS mensagens (
    id SERIAL PRIMARY KEY,
    remetente_id INTEGER,
    destinatario_id INTEGER,
    mensagem TEXT,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
cursor.close()
conn.close()

print("Banco de dados configurado no PostgreSQL com sucesso!")