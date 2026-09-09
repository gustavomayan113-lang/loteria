const TOTAL_NUMEROS = 25;
const NUMEROS_ESCOLHER = 15;


// =====================================
// CRIAR TABELA
// =====================================

function criarTabela() {

    const tabela = document.getElementById("tabela");

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

                alert("Você só pode escolher 15 números.");

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

    // Garante que a tabela existe
    criarTabela();

    const numeros = [];

    // Sorteia 15 números diferentes
    while (numeros.length < NUMEROS_ESCOLHER) {

        const numero =
            Math.floor(Math.random() * TOTAL_NUMEROS) + 1;

        if (!numeros.includes(numero)) {

            numeros.push(numero);
        }
    }

    // Seleciona os números sorteados
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

    if (numeros.length === 0) {

        mensagem.innerHTML = "Escolha seus 15 números";

        return;
    }

    const nome =
        document.getElementById("nome").value.trim();

    if (numeros.length < 15) {

        mensagem.innerHTML =
            `${nome ? nome + ", " : ""}você escolheu ${numeros.length} de 15 números`;

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

    // resto da função continua aqui...

    const selecionados =
        document.querySelectorAll(".numero.selecionado");

    const numeros = [];

    selecionados.forEach(numero => {

        numeros.push(Number(numero.textContent));

    });

    numeros.sort((a, b) => a - b);


    // =================================
    // VALIDAÇÕES
    // =================================

    if (!nome) {

        alert("Digite seu nome.");

        return;
    }

    if (!email) {

        alert("Digite seu e-mail.");

        return;
    }

    if (numeros.length !== 15) {

        alert("Você precisa escolher exatamente 15 números.");

        return;
    }


    // =================================
    // CONFIRMAÇÃO
    // =================================

    const confirmar = confirm(
        `CONFIRMAR JOGO?\n\n` +
        `Nome: ${nome}\n` +
        `Números escolhidos:\n` +
        `${numeros.join(" - ")}\n\n` +
        `Deseja salvar este jogo?`
    );


    // Se clicar em cancelar
    if (!confirmar) {

        return;

    }


    // =================================
    // ENVIA PARA O FLASK
    // =================================

   fetch("/salvar-jogo", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                nome: nome,

                email: email,

                numeros: numeros

            })

        })

        .then(resposta => resposta.json())

        .then(dados => {

            alert(dados.mensagem);

            if (dados.sucesso) {

                // Limpa nome
                document.getElementById("nome").value = "";

                // Remove todos os números selecionados
                document.querySelectorAll(".numero.selecionado")
                    .forEach(numero => {
                        numero.classList.remove("selecionado");
                    });

                // Atualiza a mensagem da tela
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

    criarTabela();

    atualizarMensagem();

});


// =====================================
// LIMPAR JOGO
// =====================================

function limparJogo() {

    const selecionados =
        document.querySelectorAll(".numero.selecionado");

    selecionados.forEach(numero => {

        numero.classList.remove("selecionado");

    });

    atualizarMensagem();

}