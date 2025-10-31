<?php
header('Content-Type: application/json');

$arquivo = 'dados_visitantes.json';

// Receber dados do JavaScript
$dados = json_decode(file_get_contents('php://input'), true);

if ($dados) {
    // Salvar no arquivo JSON
    file_put_contents($arquivo, json_encode($dados, JSON_PRETTY_PRINT));
    
    echo json_encode(['success' => true]);
} else {
    echo json_encode(['success' => false, 'error' => 'Dados inválidos']);
}
?>