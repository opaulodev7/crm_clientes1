from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'crm_secret_key'


# CONFIG MYSQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'crm_clientes'
}


# CONEXÃO MYSQL
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# DASHBOARD
@app.route('/')
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # TOTAL CLIENTES
    cursor.execute("SELECT COUNT(*) AS total FROM clientes")
    total_clientes = cursor.fetchone()['total']

    # TOTAL SERVIÇOS
    cursor.execute("SELECT COUNT(*) AS total FROM servicos")
    total_servicos = cursor.fetchone()['total']

    # FATURAMENTO
    cursor.execute("SELECT SUM(valor) AS total FROM servicos")
    resultado = cursor.fetchone()

    valor_total = resultado['total'] if resultado['total'] else 0

    # ÚLTIMOS CLIENTES
    cursor.execute("""
        SELECT * FROM clientes
        ORDER BY id DESC
        LIMIT 5
    """)
    ultimos_clientes = cursor.fetchall()

    # ÚLTIMOS SERVIÇOS
    cursor.execute("""
        SELECT servicos.*, clientes.nome AS cliente_nome
        FROM servicos
        INNER JOIN clientes
        ON servicos.cliente_id = clientes.id
        ORDER BY servicos.id DESC
        LIMIT 5
    """)
    ultimos_servicos = cursor.fetchall()

    # GRÁFICO
    cursor.execute("""
        SELECT DATE_FORMAT(data, '%m/%Y') AS mes,
        SUM(valor) AS total
        FROM servicos
        GROUP BY DATE_FORMAT(data, '%m/%Y')
        ORDER BY MIN(data) ASC
    """)

    grafico = cursor.fetchall()

    labels = [item['mes'] for item in grafico]
    valores = [float(item['total']) for item in grafico]

    cursor.close()
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

# CLIENTES
@app.route('/clientes')
def clientes():

    busca = request.args.get('busca', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if busca:
        cursor.execute("""
            SELECT * FROM clientes
            WHERE nome LIKE %s
            ORDER BY id DESC
        """, (f'%{busca}%',))
    else:
        cursor.execute("""
            SELECT * FROM clientes
            ORDER BY id DESC
        """)

    clientes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'clientes.html',
        clientes=clientes
    )

# CADASTRAR CLIENTE
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
        VALUES (%s, %s, %s, %s)
    """, (nome, telefone, email, cidade))

    conn.commit()

    cursor.close()
    conn.close()

    flash('Cliente cadastrado com sucesso!', 'success')

    return redirect(url_for('clientes'))

# EDITAR CLIENTE
@app.route('/clientes/editar/<int:id>', methods=['POST'])
def editar_cliente(id):

    conn = None
    cursor = None

    try:

        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        cidade = request.form.get('cidade')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE clientes
            SET
                nome = %s,
                telefone = %s,
                email = %s,
                cidade = %s
            WHERE id = %s
        """, (
            nome,
            telefone,
            email,
            cidade,
            id
        ))

        conn.commit()

        flash(
            'Cliente atualizado com sucesso!',
            'success'
        )

    except Exception as erro:

        if conn:
            conn.rollback()

        flash(
            f'Erro ao atualizar cliente: {erro}',
            'danger'
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(url_for('clientes'))

# EXCLUIR CLIENTE
@app.route('/clientes/excluir/<int:id>')
def excluir_cliente(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM clientes WHERE id = %s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash('Cliente excluído com sucesso!', 'danger')

    return redirect(url_for('clientes'))

# SERVIÇOS
@app.route('/servicos')
def servicos():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT servicos.*, clientes.nome AS cliente_nome
        FROM servicos
        INNER JOIN clientes
        ON servicos.cliente_id = clientes.id
        ORDER BY servicos.id DESC
    """)

    servicos = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM clientes
        ORDER BY nome ASC
    """)

    clientes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'servicos.html',
        servicos=servicos,
        clientes=clientes
    )


# ADICIONAR SERVIÇO
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
        VALUES (%s, %s, %s, %s, %s)
    """, (nome, descricao, valor, data, cliente_id))

    conn.commit()

    cursor.close()
    conn.close()

    flash('Serviço cadastrado com sucesso!', 'success')

    return redirect(url_for('servicos'))

# EDITAR SERVIÇO
@app.route('/servicos/editar/<int:id>', methods=['POST'])
def editar_servico(id):

    conn = None
    cursor = None

    try:

        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        valor = request.form.get('valor')
        data = request.form.get('data')
        cliente_id = request.form.get('cliente_id')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE servicos
            SET
                nome = %s,
                descricao = %s,
                valor = %s,
                data = %s,
                cliente_id = %s
            WHERE id = %s
        """, (
            nome,
            descricao,
            valor,
            data,
            cliente_id,
            id
        ))

        conn.commit()

        flash(
            'Serviço atualizado com sucesso!',
            'success'
        )

    except Exception as erro:

        if conn:
            conn.rollback()

        flash(
            f'Erro ao atualizar serviço: {erro}',
            'danger'
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(url_for('servicos'))

# EXCLUIR SERVIÇO
@app.route('/servicos/excluir/<int:id>')
def excluir_servico(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM servicos WHERE id = %s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash('Serviço excluído com sucesso!', 'danger')

    return redirect(url_for('servicos'))


if __name__ == '__main__':
    app.run(debug=True)