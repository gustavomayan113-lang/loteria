from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    session,
    send_file
)

import os
import json
from datetime import datetime

from dotenv import load_dotenv

from banco import conectar_banco, criar_banco

load_dotenv()


app = Flask(__name__)

criar_banco()

# =====================================
# CONFIGURAÇÕES DO ADMINISTRADOR
# =====================================

app.secret_key = os.getenv("SECRET_KEY")

LOGIN_ADMIN = os.getenv("LOGIN_ADMIN")
SENHA_ADMIN = os.getenv("SENHA_ADMIN")


# =====================================
# CONFIGURAÇÃO DO JOGO
# =====================================


def obter_configuracao_jogo():

    configuracao_padrao = {
        "data_limite": "31/12/2026",
        "total_numeros": 25,
        "quantidade_padrao": 25,
        "mostrar_seletor_quantidade": False,
        "gerar_aleatorio": True,
    }

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            data_limite,
            total_numeros,
            quantidade_padrao,
            mostrar_seletor_quantidade,
            gerar_aleatorio
        FROM configuracoes
        WHERE id = 1
    """)

    resultado = cursor.fetchone()
    conexao.close()

    if not resultado:
        return configuracao_padrao

    data_limite, total_numeros, quantidade_padrao, mostrar_seletor_quantidade, gerar_aleatorio = resultado

    try:
        total_numeros = int(total_numeros)
    except (TypeError, ValueError):
        total_numeros = configuracao_padrao["total_numeros"]

    try:
        quantidade_padrao = int(quantidade_padrao)
    except (TypeError, ValueError):
        quantidade_padrao = configuracao_padrao["quantidade_padrao"]

    if total_numeros < 1:
        total_numeros = configuracao_padrao["total_numeros"]

    if quantidade_padrao < 1:
        quantidade_padrao = min(configuracao_padrao["quantidade_padrao"], total_numeros)
    else:
        quantidade_padrao = min(quantidade_padrao, total_numeros)

    mostrar_seletor_quantidade = bool(mostrar_seletor_quantidade)
    gerar_aleatorio = bool(gerar_aleatorio)

    return {
        "data_limite": data_limite or configuracao_padrao["data_limite"],
        "total_numeros": total_numeros,
        "quantidade_padrao": quantidade_padrao,
        "mostrar_seletor_quantidade": mostrar_seletor_quantidade,
        "gerar_aleatorio": gerar_aleatorio,
    }



def normalizar_inteiro(valor, padrao):

    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return padrao

    if numero < 1:
        return padrao

    return numero



def validacao_numeros(numeros, total_numeros, quantidade_esperada):

    if not isinstance(numeros, list):
        return False, "Lista de números inválida."

    if len(numeros) != quantidade_esperada:
        return False, f"Você precisa escolher exatamente {quantidade_esperada} números."

    numeros_convertidos = []

    for numero in numeros:
        try:
            numero_int = int(numero)
        except (TypeError, ValueError):
            return False, "Você só pode escolher números válidos."

        if numero_int < 1 or numero_int > total_numeros:
            return False, f"Os números devem estar entre 1 e {total_numeros}."

        numeros_convertidos.append(numero_int)

    if len(set(numeros_convertidos)) != len(numeros_convertidos):
        return False, "Não é permitido repetir números."

    return True, numeros_convertidos



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

    conexao.commit()
    conexao.close()

    return redirect("/banco")


# =====================================
# PÁGINA INICIAL
# =====================================

@app.route("/")
def inicio():

    configuracao = obter_configuracao_jogo()

    return render_template(
        "index.html",
        data_limite=configuracao["data_limite"],
        configuracao=configuracao
    )


# =====================================
# SALVAR JOGO
# =====================================

@app.route("/salvar-jogo", methods=["POST"])
def salvar_jogo():

    dados = request.get_json(silent=True) or {}

    nome = (dados.get("nome") or "").strip()
    email = "teste@gmail.com"
    numeros = dados.get("numeros") or []
    quantidade = dados.get("quantidade")
    modo = (dados.get("modo") or "manual").strip() or "manual"

    configuracao = obter_configuracao_jogo()

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT data_limite
        FROM configuracoes
        WHERE id = 1
    """)

    resultado = cursor.fetchone()
    conexao.close()

    if resultado and resultado[0]:

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

    if not nome or not numeros:

        return jsonify({
            "sucesso": False,
            "mensagem": "Nome e números são obrigatórios."
        }), 400

    quantidade_esperada = normalizar_inteiro(
        quantidade,
        configuracao["quantidade_padrao"]
    )

    total_numeros = configuracao["total_numeros"]

    if quantidade_esperada > total_numeros:
        quantidade_esperada = total_numeros

    valido, resultado_validacao = validacao_numeros(
        numeros,
        total_numeros,
        quantidade_esperada
    )

    if not valido:
        return jsonify({
            "sucesso": False,
            "mensagem": resultado_validacao
        }), 400

    numeros_normalizados = resultado_validacao

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
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        nome,
        email,
        json.dumps(numeros_normalizados),
        quantidade_esperada,
        modo,
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

    configuracao = obter_configuracao_jogo()

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
        jogos=jogos,
        configuracao=configuracao
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

    if not data:
        return redirect("/banco")

    data = datetime.strptime(
        data,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE configuracoes
        SET data_limite = %s
        WHERE id = 1
    """, (data,))

    conexao.commit()
    conexao.close()

    return redirect("/banco")


@app.route("/alterar-configuracao-jogo", methods=["POST"])
def alterar_configuracao_jogo():

    if not session.get("admin"):
        return redirect("/login")

    total_numeros = normalizar_inteiro(
        request.form.get("total_numeros"),
        25
    )
    quantidade_padrao = normalizar_inteiro(
        request.form.get("quantidade_padrao"),
        25
    )
    mostrar_seletor_quantidade = request.form.get("mostrar_seletor_quantidade") == "on"
    gerar_aleatorio = request.form.get("gerar_aleatorio") == "on"

    if quantidade_padrao > total_numeros:
        quantidade_padrao = total_numeros

    if total_numeros < 1:
        total_numeros = 25

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE configuracoes
        SET total_numeros = %s,
            quantidade_padrao = %s,
            mostrar_seletor_quantidade = %s,
            gerar_aleatorio = %s
        WHERE id = 1
    """, (
        total_numeros,
        quantidade_padrao,
        mostrar_seletor_quantidade,
        gerar_aleatorio,
    ))

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
    from io import BytesIO

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

    # Criar o arquivo em memória
    arquivo = BytesIO()

    wb.save(arquivo)

    # Voltar para o início do arquivo
    arquivo.seek(0)

    # Enviar a planilha para o navegador
    return send_file(
        arquivo,
        as_attachment=True,
        download_name="jogos_loteria_nior.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )




# =====================================
# INICIAR SERVIDOR
# =====================================

if __name__ == "__main__":

    criar_banco()

    app.run(debug=True)






