const CONFIGURACAO_PADRAO = {
    total_numeros: 25,
    quantidade_padrao: 25,
    mostrar_seletor_quantidade: false,
    gerar_aleatorio: true,
};

const CONFIGURACAO_JOGO = window.CONFIGURACAO_JOGO || CONFIGURACAO_PADRAO;
let TOTAL_NUMEROS = Number(CONFIGURACAO_JOGO.total_numeros) || CONFIGURACAO_PADRAO.total_numeros;
let NUMEROS_ESCOLHER = Number(CONFIGURACAO_JOGO.quantidade_padrao) || CONFIGURACAO_PADRAO.quantidade_padrao;
let MODO_JOGO = "manual";

if (NUMEROS_ESCOLHER > TOTAL_NUMEROS) {
    NUMEROS_ESCOLHER = TOTAL_NUMEROS;
}

function atualizarValorPadrao() {
    const valorPadrao = Number(CONFIGURACAO_JOGO.quantidade_padrao) || CONFIGURACAO_PADRAO.quantidade_padrao;
    NUMEROS_ESCOLHER = Math.min(Math.max(valorPadrao, 1), TOTAL_NUMEROS);
}

function criarListaQuantidade() {
    const seletor = document.getElementById("quantidade-jogo");

    if (!seletor) {
        return;
    }

    const valorAtual = Number(seletor.value) || NUMEROS_ESCOLHER || 1;
    seletor.innerHTML = "";

    for (let i = 1; i <= TOTAL_NUMEROS; i++) {
        const option = document.createElement("option");
        option.value = String(i);
        option.textContent = `${i} números`;
        seletor.appendChild(option);
    }

    const valorSelecionado = Math.min(Math.max(valorAtual, 1), TOTAL_NUMEROS);
    seletor.value = String(valorSelecionado);
    NUMEROS_ESCOLHER = valorSelecionado;
}

function configurarSeletorQuantidade() {
    const container = document.getElementById("controle-quantidade");

    if (!container) {
        return;
    }

    if (CONFIGURACAO_JOGO.mostrar_seletor_quantidade) {
        container.style.display = "flex";
        criarListaQuantidade();
        return;
    }

    container.style.display = "none";
    atualizarValorPadrao();
}

function limparSelecionados() {
    document.querySelectorAll(".numero.selecionado").forEach(numero => {
        numero.classList.remove("selecionado");
    });
}

// =====================================
// CRIAR TABELA
// =====================================

function criarTabela() {

    const tabela = document.getElementById("tabela");

    if (!tabela) {
        return;
    }

    tabela.innerHTML = "";

    for (let i = 1; i <= TOTAL_NUMEROS; i++) {

        const numero = document.createElement("div");

        numero.classList.add("numero");

        numero.textContent = i;

        numero.addEventListener("click", function () {

            if (numero.classList.contains("selecionado")) {

                numero.classList.remove("selecionado");

                atualizarMensagem();

                return;
            }

            const selecionados =
                document.querySelectorAll(".numero.selecionado").length;

            if (selecionados >= NUMEROS_ESCOLHER) {

                alert(`Você só pode escolher ${NUMEROS_ESCOLHER} números.`);

                return;
            }

            numero.classList.add("selecionado");

            atualizarMensagem();

        });

        tabela.appendChild(numero);
    }
}


// =====================================
// GERAR JOGO ALEATÓRIO
// =====================================

function gerarAleatorio() {

    MODO_JOGO = "aleatorio";

    criarTabela();

    const numeros = [];

    while (numeros.length < NUMEROS_ESCOLHER) {

        const numero =
            Math.floor(Math.random() * TOTAL_NUMEROS) + 1;

        if (!numeros.includes(numero)) {

            numeros.push(numero);
        }
    }

    const elementos =
        document.querySelectorAll(".numero");

    numeros.forEach(numero => {

        elementos[numero - 1].classList.add("selecionado");

    });

    atualizarMensagem();
}


// =====================================
// ATUALIZAR MENSAGEM
// =====================================

function atualizarMensagem() {

    const selecionados =
        document.querySelectorAll(".numero.selecionado");

    const numeros = [];

    selecionados.forEach(numero => {

        numeros.push(Number(numero.textContent));

    });

    numeros.sort((a, b) => a - b);

    const mensagem =
        document.getElementById("mensagem");

    if (!mensagem) {
        return;
    }

    if (numeros.length === 0) {

        mensagem.innerHTML = `Escolha seus ${NUMEROS_ESCOLHER} números`;

        return;
    }

    const nome =
        document.getElementById("nome").value.trim();

    if (numeros.length < NUMEROS_ESCOLHER) {

        mensagem.innerHTML =
            `${nome ? nome + ", " : ""}você escolheu ${numeros.length} de ${NUMEROS_ESCOLHER} números`;

        return;
    }

    mensagem.innerHTML =
        `${nome ? nome + ", seus números são:" : "Seus números são:"} ${numeros.join(" - ")}`;
}


// =====================================
// SALVAR JOGO
// =====================================

function salvarJogo() {

    const nome =
        document.getElementById("nome").value.trim();

    const email = "teste@gmail.com";

    if (!nome) {
        alert("Digite seu nome.");
        return;
    }

    const selecionados =
        document.querySelectorAll(".numero.selecionado");

    const numeros = [];

    selecionados.forEach(numero => {

        numeros.push(Number(numero.textContent));

    });

    numeros.sort((a, b) => a - b);

    if (!email) {

        alert("Digite seu e-mail.");

        return;
    }

    if (numeros.length !== NUMEROS_ESCOLHER) {

        alert(`Você precisa escolher exatamente ${NUMEROS_ESCOLHER} números.`);

        return;
    }

    const confirmar = confirm(
        `CONFIRMAR JOGO?\n\n` +
        `Nome: ${nome}\n` +
        `Números escolhidos:\n` +
        `${numeros.join(" - ")}\n\n` +
        `Deseja salvar este jogo?`
    );

    if (!confirmar) {
        return;
    }

    fetch("/salvar-jogo", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                nome: nome,
                email: email,
                numeros: numeros,
                quantidade: NUMEROS_ESCOLHER,
                modo: MODO_JOGO
            })

        })

        .then(resposta => resposta.json())

        .then(dados => {

            alert(dados.mensagem);

            if (dados.sucesso) {

                document.getElementById("nome").value = "";
                limparSelecionados();
                MODO_JOGO = "manual";
                atualizarMensagem();
            }

        })

        .catch(erro => {

            console.error(erro);

            alert("Erro ao salvar o jogo.");

        });

    }
// =====================================
// INICIAR
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    const seletor = document.getElementById("quantidade-jogo");
    if (seletor) {
        seletor.addEventListener("change", function () {
            const valor = Number(this.value) || NUMEROS_ESCOLHER;
            NUMEROS_ESCOLHER = Math.min(Math.max(valor, 1), TOTAL_NUMEROS);
            limparSelecionados();
            atualizarMensagem();
        });
    }

    const botaoAleatorio = document.getElementById("gerar-aleatorio");
    if (botaoAleatorio) {
        if (!CONFIGURACAO_JOGO.gerar_aleatorio) {
            botaoAleatorio.style.display = "none";
        }
    }

    configurarSeletorQuantidade();
    criarTabela();
    atualizarMensagem();

});


// =====================================
// LIMPAR JOGO
// =====================================

function limparJogo() {

    limparSelecionados();
    atualizarMensagem();
}