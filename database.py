import sqlite3

def get_conn():
    return sqlite3.connect("usuarios.db")

def criar_tabelas():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS transcricoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        nome_pdf TEXT,
        texto TEXT,
        source_id TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")
    conn.commit()
    conn.close()

def verificar_usuario(login, senha, verify_func):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, senha FROM usuarios WHERE login=?", (login,))
    usuario = c.fetchone()
    conn.close()
    if usuario and verify_func(senha, usuario[1]):
        return usuario
    return None

def login_existe(login):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM usuarios WHERE login=?", (login,))
    existe = c.fetchone() is not None
    conn.close()
    return existe

def adicionar_usuario(login, senha_hash):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (login, senha) VALUES (?, ?)", (login, senha_hash))
    conn.commit()
    conn.close()

def adicionar_transcricao(usuario_id, nome_pdf, texto):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO transcricoes (usuario_id, nome_pdf, texto) VALUES (?, ?, ?)", (usuario_id, nome_pdf, texto))
    conn.commit()
    transcricao_id = c.lastrowid
    conn.close()
    return transcricao_id

def atualizar_source_id(transcricao_id, source_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE transcricoes SET source_id = ? WHERE id = ?", (source_id, transcricao_id))
    conn.commit()
    conn.close()

def listar_transcricoes(usuario_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, usuario_id, nome_pdf, texto, source_id FROM transcricoes WHERE usuario_id=?", (usuario_id,))
    resultados = c.fetchall()
    conn.close()
    return resultados

def excluir_transcricao(transcricao_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM transcricoes WHERE id=?", (transcricao_id,))
    conn.commit()
    conn.close()