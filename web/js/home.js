let visitantesDia = 0;
let totalVisitantes = 0;
let dataAtual = new Date().toLocaleDateString('pt-BR');
let diaEncerrado = false;

// Carregar dados ao iniciar
window.addEventListener('load', () => {
    carregarDados();
    atualizarDisplay();
    document.getElementById('dataAtual').textContent = dataAtual;
});

// Contabilizar visita ao clicar na tela
document.addEventListener('click', (e) => {
    // Não contar cliques nos botões do modal e botão encerrar
    if (e.target.id === 'btnEncerrar' || 
        e.target.id === 'btnConfirmar' || 
        e.target.id === 'btnCancelar' ||
        e.target.id === 'btnRelatorio'||
        e.target.closest('.modal')) {
        return;
    }
    
    if (!diaEncerrado) {
        visitantesDia++;
        totalVisitantes++;
        atualizarDisplay();
        salvarDados();
    }
});

// Botão encerrar dia
document.getElementById('btnEncerrar').addEventListener('click', (e) => {
    e.stopPropagation();
    document.getElementById('visitantesHoje').textContent = visitantesDia;
    document.getElementById('modalEncerrar').style.display = 'block';
});

// Confirmar encerramento
document.getElementById('btnConfirmar').addEventListener('click', (e) => {
    e.stopPropagation();
    encerrarDia();
    document.getElementById('modalEncerrar').style.display = 'none';
});

// Cancelar encerramento
document.getElementById('btnCancelar').addEventListener('click', (e) => {
    e.stopPropagation();
    document.getElementById('modalEncerrar').style.display = 'none';
});
// ver relarotirio
document.getElementById('btnRelatorio').addEventListener('click', (e) => {
    e.stopPropagation();
    window.location.href = 'relatorio.html';
})
// Funções auxiliares
function atualizarDisplay() {
    document.querySelector('.quantidade').textContent = `[${visitantesDia}]`;
    document.getElementById('totalVisitantes').textContent = totalVisitantes;
}

function salvarDados() {
    fetch('salvar.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            visitantesDia: visitantesDia,
            totalVisitantes: totalVisitantes,
            data: dataAtual,
            diaEncerrado: diaEncerrado
        })
    });
}

function carregarDados() {
    fetch('carregar.php')
        .then(response => response.json())
        .then(data => {
            if (data) {
                const dataArmazenada = data.data;
                const hoje = new Date().toLocaleDateString('pt-BR');
                
                // Se a data mudou, resetar contagem do dia
                if (dataArmazenada !== hoje) {
                    visitantesDia = 0;
                    dataAtual = hoje;
                    diaEncerrado = false;
                    totalVisitantes = data.totalVisitantes || 0;
                } else {
                    // Mesma data, carregar dados
                    visitantesDia = data.visitantesDia || 0;
                    totalVisitantes = data.totalVisitantes || 0;
                    diaEncerrado = data.diaEncerrado || false;
                }
            }
            atualizarDisplay();
        });
}

function encerrarDia() {
    diaEncerrado = true;
    salvarDados();
    alert('Dia encerrado com sucesso!\nVisitantes do dia: ' + visitantesDia);
}