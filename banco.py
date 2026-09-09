import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def conectar_banco():
    return psycopg.connect(DATABASE_URL)


def criar_banco():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Cria a tabela caso ainda não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT,
            numeros TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            modo TEXT,
            data TEXT NOT NULL
        )
    """)

    # Cria a tabela de configurações caso ainda não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY,
            data_limite TEXT
        )
    """)

    # Verifica se já existe a configuração principal
    cursor.execute("""
        SELECT * FROM configuracoes
        WHERE id = 1
    """)

    if not cursor.fetchone():

        cursor.execute("""
            INSERT INTO configuracoes (id, data_limite)
            VALUES (1, '31/12/2026')
        """)

    conexao.commit()
    cursor.close()
    conexao.close()


if __name__ == "__main__":

    criar_banco()

    print("Banco Supabase criado/atualizado com sucesso!")