<?php
header('Content-Type: application/json');

$arquivo = 'dados_visitantes.json';

if (file_exists($arquivo)) {
    $dados = file_get_contents($arquivo);
    echo $dados;
} else {
    // Retornar dados iniciais se arquivo não existe
    echo json_encode([
        'visitantesDia' => 0,
        'totalVisitantes' => 0,
        'data' => date('d/m/Y'),
        'diaEncerrado' => false
    ]);
}
?>