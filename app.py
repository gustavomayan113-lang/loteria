from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    session,
    send_file
)

import json
from datetime import datetime

from banco import conectar_banco, criar_banco


app = Flask(__name__)

# =====================================
# CONFIGURAÇÕES DO ADMINISTRADOR
# =====================================

app.secret_key = "loteria_nior_admin"

LOGIN_ADMIN = "ADm778"
SENHA_ADMIN = "Loto_ria"



# =====================================
# LIMPAR BANCO
# =====================================

@app.route("/limpar-banco", methods=["POST"])
def limpar_banco():

    if not session.get("admin"):
        return redirect("/login")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM jogos")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='jogos'")

    conexao.commit()
    conexao.close()

    return redirect("/banco")


# =====================================
# PÁGINA INICIAL
# =====================================

@app.route("/")
def inicio():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT data_limite
        FROM configuracoes
        WHERE id = 1
    """)

    resultado = cursor.fetchone()

    data_limite = resultado[0]

    conexao.close()

    return render_template(
        "index.html",
        data_limite=data_limite
    )


# =====================================
# SALVAR JOGO
# =====================================

@app.route("/salvar-jogo", methods=["POST"])
def salvar_jogo():

    dados = request.get_json()

    nome = dados.get("nome")
    email = dados.get("email")
    numeros = dados.get("numeros")


    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT data_limite
        FROM configuracoes
        WHERE id = 1
    """)

    resultado = cursor.fetchone()

    conexao.close()

    if resultado:

        data_limite = datetime.strptime(
            resultado[0],
            "%d/%m/%Y"
        )

        data_limite = data_limite.replace(
            hour=23,
            minute=59,
            second=59
        )

        if datetime.now() > data_limite:

            return jsonify({
                "sucesso": False,
                "mensagem": "O prazo para envio dos jogos já foi encerrado."
            }), 403




    # Validação
    if not nome or not email or not numeros:

        return jsonify({
            "sucesso": False,
            "mensagem": "Nome, e-mail e números são obrigatórios."
        }), 400


    # Sempre serão exatamente 15 números
    if len(numeros) != 15:

        return jsonify({
            "sucesso": False,
            "mensagem": "O jogo precisa ter exatamente 15 números."
        }), 400


    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({
            "sucesso": False,
            "mensagem": "E-mail inválido."
        }), 400

    # Conecta ao banco
    conexao = conectar_banco()
    cursor = conexao.cursor()


    # Salva o jogo
    cursor.execute("""
        INSERT INTO jogos (
            nome,
            email,
            numeros,
            quantidade,
            modo,
            data
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        nome,
        email,
        json.dumps(numeros),
        15,
        "manual",
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ))


    conexao.commit()
    conexao.close()


    return jsonify({
        "sucesso": True,
        "mensagem": "Jogo salvo com sucesso!"
    })


# =====================================
# LOGIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login = request.form.get("login")
        senha = request.form.get("senha")


        if login == LOGIN_ADMIN and senha == SENHA_ADMIN:

            session["admin"] = True

            return redirect("/banco")


        return render_template(
            "login.html",
            erro="Login ou senha incorretos."
        )


    return render_template("login.html")


# =====================================
# BANCO DE DADOS
# =====================================

@app.route("/banco")
def banco():

    # Impede acesso sem login
    if not session.get("admin"):

        return redirect("/login")


    conexao = conectar_banco()
    cursor = conexao.cursor()


    cursor.execute("""
        SELECT
            id,
            nome,
            email,
            numeros,
            quantidade,
            data
        FROM jogos
        ORDER BY id DESC
    """)


    jogos = cursor.fetchall()

    conexao.close()


    return render_template(
        "banco.html",
        jogos=jogos
    )


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")




#==========================
#alterar data do jogo
#==========================

@app.route("/alterar-data", methods=["POST"])
def alterar_data():

    if not session.get("admin"):
        return redirect("/login")

    data = request.form.get("data_limite")

    data = datetime.strptime(
        data,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE configuracoes
        SET data_limite = ?
        WHERE id = 1
    """, (data,))

    conexao.commit()
    conexao.close()

    return redirect("/banco")


#=========================
#Baixar jogo em planilha
#=========================

@app.route("/exportar-planilha")
def exportar_planilha():

    if not session.get("admin"):
        return redirect("/login")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            email,
            numeros,
            quantidade,
            data
        FROM jogos
        ORDER BY id ASC
    """)

    jogos = cursor.fetchall()

    conexao.close()

    # Criar planilha
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Jogos"

    # Cabeçalho
    ws.append([
        "ID",
        "Nome",
        "E-mail",
        "Números",
        "Quantidade",
        "Data"
    ])

    # Dados
    for jogo in jogos:

        numeros = jogo[3]

        try:
            numeros = json.loads(numeros)
            numeros = " - ".join(
                str(numero) for numero in numeros
            )
        except:
            pass

        ws.append([
            jogo[0],
            jogo[1],
            jogo[2],
            numeros,
            jogo[4],
            jogo[5]
        ])

    # Ajustar largura das colunas
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 45
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["F"].width = 22

    # Salvar temporariamente
    caminho = "jogos_loteria_nior.xlsx"
    wb.save(caminho)

    from flask import send_file

    return send_file(
        caminho,
        as_attachment=True,
        download_name="jogos_loteria_nior.xlsx"
    )





# =====================================
# INICIAR SERVIDOR
# =====================================

if __name__ == "__main__":

    criar_banco()

    app.run(debug=True)






