const INTERVALO_MS = 2000;
let contando = null;

// Carregar dados ao iniciar e atualizar periodicamente
window.addEventListener('load', () => {
    atualizar();
    setInterval(atualizar, INTERVALO_MS);
});

// Mesmo botão inicia e encerra a contagem
document.getElementById('btnContagem').addEventListener('click', async () => {
    if (contando && !confirm('Encerrar a contagem?\nO relatório de hoje será salvo.')) {
        return;
    }
    const acao = contando ? 'encerrar' : 'iniciar';
    try {
        const resposta = await fetch(`/api/contagem/${acao}`, { method: 'POST' });
        mostrar(await resposta.json());
    } catch (erro) {
        mostrarAviso('⚠ Sistema fora do ar');
    }
});

document.getElementById('btnRelatorio').addEventListener('click', () => {
    window.location.href = '/relatorio';
});

document.getElementById('btnArea').addEventListener('click', () => {
    window.location.href = '/camera';
});

async function atualizar() {
    try {
        const resposta = await fetch('/api/contagem');
        mostrar(await resposta.json());
    } catch (erro) {
        mostrarAviso('⚠ Sistema fora do ar');
    }
}

function mostrar(dados) {
    document.querySelector('.quantidade').textContent = `[${formatarNumero(dados.hoje)}]`;
    document.getElementById('totalVisitantes').textContent = formatarNumero(dados.acumulado);
    document.getElementById('diasFuncionando').textContent = dados.dias;
    document.getElementById('dataAtual').textContent = formatarData(dados.data);

    if (dados.contando !== contando) {
        contando = dados.contando;
        const botao = document.getElementById('btnContagem');
        botao.textContent = contando ? '■ ENCERRAR CONTAGEM' : '▶ INICIAR CONTAGEM';
        botao.classList.toggle('ativo', contando);
        document.getElementById('acoesParado').hidden = contando;

        // A imagem da câmera só fica no telão enquanto conta
        const camera = document.getElementById('cameraAoVivo');
        camera.hidden = !contando;
        if (contando) {
            camera.src = '/video';
        } else {
            camera.removeAttribute('src');
        }
    }

    if (contando && !dados.camera_ok) {
        mostrarAviso('⚠ Câmera sem sinal');
    } else {
        document.getElementById('avisoCamera').hidden = true;
    }
}

function mostrarAviso(texto) {
    const aviso = document.getElementById('avisoCamera');
    aviso.textContent = texto;
    aviso.hidden = false;
}

function formatarNumero(numero) {
    return numero.toLocaleString('pt-BR');
}

function formatarData(dataIso) {
    const [ano, mes, dia] = dataIso.split('-');
    return `${dia}/${mes}/${ano}`;
}
