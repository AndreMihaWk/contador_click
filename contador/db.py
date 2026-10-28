import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

CAMINHO = Path(__file__).resolve().parent.parent / 'dados' / 'contador.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS dias (
    data TEXT PRIMARY KEY,
    iniciado_em TEXT NOT NULL,
    relatorio_gerado_em TEXT
);
CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL REFERENCES dias(data),
    momento TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entradas_data ON entradas(data);
CREATE TABLE IF NOT EXISTS estado (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
"""


@contextmanager
def conexao():
    # Uma conexão por operação: a thread da câmera e o Flask usam o banco ao mesmo tempo
    con = sqlite3.connect(CAMINHO, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()


def agora():
    return datetime.now().isoformat(timespec='seconds')


def iniciar():
    CAMINHO.parent.mkdir(exist_ok=True)
    with conexao() as con:
        con.execute('PRAGMA journal_mode=WAL')
        con.executescript(SCHEMA)


def ler_estado(chave, padrao=None):
    with conexao() as con:
        linha = con.execute('SELECT valor FROM estado WHERE chave = ?', (chave,)).fetchone()
    return linha['valor'] if linha else padrao


def salvar_estado(chave, valor):
    with conexao() as con:
        con.execute('INSERT OR REPLACE INTO estado (chave, valor) VALUES (?, ?)', (chave, valor))


def dia_existe(data):
    with conexao() as con:
        return con.execute('SELECT 1 FROM dias WHERE data = ?', (data,)).fetchone() is not None


def criar_dia(data):
    with conexao() as con:
        con.execute('INSERT OR IGNORE INTO dias (data, iniciado_em) VALUES (?, ?)', (data, agora()))


def dias_sem_relatorio(antes_de):
    with conexao() as con:
        linhas = con.execute(
            'SELECT data FROM dias WHERE relatorio_gerado_em IS NULL AND data < ? ORDER BY data',
            (antes_de,),
        ).fetchall()
    return [linha['data'] for linha in linhas]


def marcar_relatorio_gerado(data):
    with conexao() as con:
        con.execute('UPDATE dias SET relatorio_gerado_em = ? WHERE data = ?', (agora(), data))


def registrar_entrada():
    momento = agora()
    with conexao() as con:
        con.execute('INSERT INTO entradas (data, momento) VALUES (?, ?)', (momento[:10], momento))


def contagem_atual():
    hoje = date.today().isoformat()
    with conexao() as con:
        linha = con.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM entradas WHERE data = ?) AS hoje,
                (SELECT COUNT(*) FROM entradas) AS acumulado,
                (SELECT COUNT(*) FROM dias) AS dias
            """,
            (hoje,),
        ).fetchone()
    return {'data': hoje, **dict(linha)}


def historico():
    with conexao() as con:
        linhas = con.execute(
            """
            SELECT d.data, d.relatorio_gerado_em,
                   COUNT(e.id) AS total,
                   SUM(COUNT(e.id)) OVER (ORDER BY d.data) AS acumulado
            FROM dias d LEFT JOIN entradas e ON e.data = d.data
            GROUP BY d.data
            ORDER BY d.data
            """
        ).fetchall()
    return [dict(linha) for linha in linhas]


def total_do_dia(data):
    with conexao() as con:
        return con.execute('SELECT COUNT(*) FROM entradas WHERE data = ?', (data,)).fetchone()[0]


def acumulado_ate(data):
    with conexao() as con:
        return con.execute('SELECT COUNT(*) FROM entradas WHERE data <= ?', (data,)).fetchone()[0]


def entradas_por_hora(data):
    with conexao() as con:
        linhas = con.execute(
            """
            SELECT substr(momento, 12, 2) AS hora, COUNT(*) AS total
            FROM entradas WHERE data = ?
            GROUP BY hora ORDER BY hora
            """,
            (data,),
        ).fetchall()
    return [(linha['hora'], linha['total']) for linha in linhas]
