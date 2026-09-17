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
            data_limite TEXT,
            total_numeros INTEGER NOT NULL DEFAULT 25,
            quantidade_padrao INTEGER NOT NULL DEFAULT 25,
            mostrar_seletor_quantidade BOOLEAN NOT NULL DEFAULT FALSE,
            gerar_aleatorio BOOLEAN NOT NULL DEFAULT TRUE
        )
    """)

    colunas = {
        "total_numeros": "INTEGER NOT NULL DEFAULT 25",
        "quantidade_padrao": "INTEGER NOT NULL DEFAULT 25",
        "mostrar_seletor_quantidade": "BOOLEAN NOT NULL DEFAULT FALSE",
        "gerar_aleatorio": "BOOLEAN NOT NULL DEFAULT TRUE",
        "tema": "TEXT NOT NULL DEFAULT 'lotofacil'",
    }

    for nome_coluna, tipo_coluna in colunas.items():
        cursor.execute(
            """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = current_schema()
                    AND table_name = 'configuracoes'
                    AND column_name = %s
                )
            """,
            (nome_coluna,),
        )

        if not cursor.fetchone()[0]:
            cursor.execute(
                f"ALTER TABLE configuracoes ADD COLUMN {nome_coluna} {tipo_coluna}"
            )

    # Verifica se já existe a configuração principal
    cursor.execute("""
        SELECT * FROM configuracoes
        WHERE id = 1
    """)

    if not cursor.fetchone():

        cursor.execute("""
            INSERT INTO configuracoes (
                id,
                data_limite,
                total_numeros,
                quantidade_padrao,
                mostrar_seletor_quantidade,
                gerar_aleatorio,
                tema
            )
            VALUES (1, '31/12/2026', 25, 15, FALSE, TRUE, 'lotofacil')
        """)
    else:
        cursor.execute("""
            UPDATE configuracoes
            SET data_limite = COALESCE(data_limite, '31/12/2026'),
                total_numeros = COALESCE(total_numeros, 25),
                quantidade_padrao = COALESCE(quantidade_padrao, 25),
                mostrar_seletor_quantidade = COALESCE(mostrar_seletor_quantidade, FALSE),
                gerar_aleatorio = COALESCE(gerar_aleatorio, TRUE),
                tema = COALESCE(tema, 'lotofacil')
            WHERE id = 1
        """)

    conexao.commit()
    cursor.close()
    conexao.close()


if __name__ == "__main__":

    criar_banco()

    print("Banco Supabase criado/atualizado com sucesso!")