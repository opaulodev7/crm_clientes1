from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'crm_secret_key'

DATABASE = 'database.db'


# =========================
# CONEXÃO SQLITE
# =========================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================
# CRIAR BANCO AUTOMATICAMENTE
# =========================

def criar_banco():

    conn = get_db_connection()
    cursor = conn.cursor()

    # CLIENTES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            telefone TEXT NOT NULL,

            email TEXT NOT NULL,

            cidade TEXT NOT NULL,

            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # SERVIÇOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            descricao TEXT,

            valor REAL NOT NULL,

            data DATE NOT NULL,

            cliente_id INTEGER NOT NULL,

            FOREIGN KEY(cliente_id)
            REFERENCES clientes(id)
        )
    """)

    conn.commit()
    conn.close()


criar_banco()


# =========================
# DASHBOARD
# =========================

@app.route('/')
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    # TOTAL CLIENTES
    cursor.execute(
        "SELECT COUNT(*) as total FROM clientes"
    )

    total_clientes = cursor.fetchone()['total']

    # TOTAL SERVIÇOS
    cursor.execute(
        "SELECT COUNT(*) as total FROM servicos"
    )

    total_servicos = cursor.fetchone()['total']

    # FATURAMENTO
    cursor.execute(
        "SELECT SUM(valor) as total FROM servicos"
    )

    resultado = cursor.fetchone()

    valor_total = (
        resultado['total']
        if resultado['total']
        else 0
    )

    # ÚLTIMOS CLIENTES
    cursor.execute("""
        SELECT *
        FROM clientes
        ORDER BY id DESC
        LIMIT 5
    """)

    ultimos_clientes = cursor.fetchall()

    # ÚLTIMOS SERVIÇOS
    cursor.execute("""
        SELECT servicos.*,
               clientes.nome AS cliente_nome

        FROM servicos

        INNER JOIN clientes
        ON servicos.cliente_id = clientes.id

        ORDER BY servicos.id DESC
        LIMIT 5
    """)

    ultimos_servicos = cursor.fetchall()

    # GRÁFICO
    cursor.execute("""
        SELECT
            strftime('%m/%Y', data) AS mes,
            SUM(valor) AS total

        FROM servicos

        GROUP BY strftime('%m/%Y', data)

        ORDER BY data ASC
    """)

    grafico = cursor.fetchall()

    labels = [item['mes'] for item in grafico]

    valores = [
        float(item['total'])
        for item in grafico
    ]

    conn.close()

    return render_template(
        'dashboard.html',

        total_clientes=total_clientes,

        total_servicos=total_servicos,

        valor_total=valor_total,

        ultimos_clientes=ultimos_clientes,

        ultimos_servicos=ultimos_servicos,

        labels=labels,

        valores=valores
    )


# =========================
# CLIENTES
# =========================

@app.route('/clientes')
def clientes():

    busca = request.args.get('busca', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    if busca:

        cursor.execute("""
            SELECT *
            FROM clientes
            WHERE nome LIKE ?
            ORDER BY id DESC
        """, (f'%{busca}%',))

    else:

        cursor.execute("""
            SELECT *
            FROM clientes
            ORDER BY id DESC
        """)

    clientes = cursor.fetchall()

    conn.close()

    return render_template(
        'clientes.html',
        clientes=clientes
    )


# =========================
# ADICIONAR CLIENTE
# =========================

@app.route('/clientes/adicionar', methods=['POST'])
def adicionar_cliente():

    nome = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']
    cidade = request.form['cidade']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes
        (nome, telefone, email, cidade)

        VALUES (?, ?, ?, ?)
    """, (
        nome,
        telefone,
        email,
        cidade
    ))

    conn.commit()
    conn.close()

    flash(
        'Cliente cadastrado com sucesso!',
        'success'
    )

    return redirect(url_for('clientes'))


# =========================
# EDITAR CLIENTE
# =========================

@app.route('/clientes/editar/<int:id>', methods=['POST'])
def editar_cliente(id):

    try:

        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        cidade = request.form['cidade']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE clientes

            SET
                nome = ?,
                telefone = ?,
                email = ?,
                cidade = ?

            WHERE id = ?
        """, (
            nome,
            telefone,
            email,
            cidade,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            'Cliente atualizado com sucesso!',
            'success'
        )

    except Exception as erro:

        flash(
            f'Erro ao atualizar cliente: {erro}',
            'danger'
        )

    return redirect(url_for('clientes'))


# =========================
# EXCLUIR CLIENTE
# =========================

@app.route('/clientes/excluir/<int:id>')
def excluir_cliente(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM clientes WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        'Cliente excluído com sucesso!',
        'danger'
    )

    return redirect(url_for('clientes'))


# =========================
# SERVIÇOS
# =========================

@app.route('/servicos')
def servicos():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT servicos.*,
               clientes.nome AS cliente_nome

        FROM servicos

        INNER JOIN clientes
        ON servicos.cliente_id = clientes.id

        ORDER BY servicos.id DESC
    """)

    servicos = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM clientes
        ORDER BY nome ASC
    """)

    clientes = cursor.fetchall()

    conn.close()

    return render_template(
        'servicos.html',
        servicos=servicos,
        clientes=clientes
    )


# =========================
# ADICIONAR SERVIÇO
# =========================

@app.route('/servicos/adicionar', methods=['POST'])
def adicionar_servico():

    nome = request.form['nome']
    descricao = request.form['descricao']
    valor = request.form['valor']
    data = request.form['data']
    cliente_id = request.form['cliente_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO servicos
        (nome, descricao, valor, data, cliente_id)

        VALUES (?, ?, ?, ?, ?)
    """, (
        nome,
        descricao,
        valor,
        data,
        cliente_id
    ))

    conn.commit()
    conn.close()

    flash(
        'Serviço cadastrado com sucesso!',
        'success'
    )

    return redirect(url_for('servicos'))


# =========================
# EDITAR SERVIÇO
# =========================

@app.route('/servicos/editar/<int:id>', methods=['POST'])
def editar_servico(id):

    try:

        nome = request.form['nome']
        descricao = request.form['descricao']
        valor = request.form['valor']
        data = request.form['data']
        cliente_id = request.form['cliente_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE servicos

            SET
                nome = ?,
                descricao = ?,
                valor = ?,
                data = ?,
                cliente_id = ?

            WHERE id = ?
        """, (
            nome,
            descricao,
            valor,
            data,
            cliente_id,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            'Serviço atualizado com sucesso!',
            'success'
        )

    except Exception as erro:

        flash(
            f'Erro ao atualizar serviço: {erro}',
            'danger'
        )

    return redirect(url_for('servicos'))


# =========================
# EXCLUIR SERVIÇO
# =========================

@app.route('/servicos/excluir/<int:id>')
def excluir_servico(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM servicos WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        'Serviço excluído com sucesso!',
        'danger'
    )

    return redirect(url_for('servicos'))


# =========================
# EXECUTAR
# =========================

if __name__ == '__main__':
    app.run(debug=True)