import sqlite3


def conectar_banco():
    return sqlite3.connect("loteria.db")


def criar_banco():

    conexao = sqlite3.connect("loteria.db")
    cursor = conexao.cursor()

    # Cria a tabela caso ela ainda não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            numeros TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            modo TEXT,
            data TEXT NOT NULL
        )
    """)

    # Verifica quais colunas já existem
    cursor.execute("PRAGMA table_info(jogos)")

    colunas = [coluna[1] for coluna in cursor.fetchall()]

    # Se o banco antigo não tiver email, adiciona
    if "email" not in colunas:

        cursor.execute("""
            ALTER TABLE jogos
            ADD COLUMN email TEXT
        """)

        print("Coluna 'email' adicionada ao banco.")

    # Se por algum motivo o banco antigo não tiver modo
    if "modo" not in colunas:

        cursor.execute("""
            ALTER TABLE jogos
            ADD COLUMN modo TEXT
        """)

        print("Coluna 'modo' adicionada ao banco.")


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY,
            data_limite TEXT
        )
    """)

    cursor.execute("SELECT * FROM configuracoes WHERE id = 1")

    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO configuracoes (id, data_limite)
            VALUES (1, '31/12/2026')
        """)

    conexao.commit()
    conexao.close()


if __name__ == "__main__":

    criar_banco()

    print("Banco criado/atualizado com sucesso!")