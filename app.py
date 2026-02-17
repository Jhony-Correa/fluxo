from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.template_filter('moeda')
def fmt_moeda(v):
    if v is None: return "0,00"
    return f"{v:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")


@app.template_filter('data_br')
def fmt_data(d):
    if d is None: return ""
    return d.strftime('%d/%m/%Y')


def logado():
    return 'id_usr' in session


@app.route('/cadastro', methods=['GET', 'POST'])
def cad():
    if request.method == 'POST':
        u = request.form['usuario']
        s_hash = generate_password_hash(request.form['senha'])
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)", (u, s_hash))
            mysql.connection.commit()
            flash('Conta criada! Faça login.', 'sucesso')
            return redirect(url_for('entrar'))
        except:
            flash('Erro: Usuário já existe.', 'perigo')
        finally:
            cur.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def entrar():
    if request.method == 'POST':
        u_f = request.form['usuario']
        s_f = request.form['senha']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario = %s", [u_f])
        u_db = cur.fetchone()
        cur.close()
        if u_db and check_password_hash(u_db['senha'], s_f):
            session['id_usr'] = u_db['id']
            session['nome_usr'] = u_db['usuario']
            return redirect(url_for('ini'))
        flash('Usuário ou senha incorretos.', 'perigo')
    return render_template('login.html')


@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('entrar'))


@app.route('/')
def ini():
    if not logado(): return redirect(url_for('entrar'))

    tp = request.args.get('tipo')
    cat_s = request.args.get('categoria')
    m = request.args.get('mes')

    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT categoria FROM transacoes WHERE id_usuario = %s", [session['id_usr']])
    cats = [r['categoria'] for r in cur.fetchall()]

    sql = "SELECT * FROM transacoes WHERE id_usuario = %s"
    par = [session['id_usr']]

    if tp:
        sql += " AND tipo = %s"
        par.append(tp)
    if cat_s:
        sql += " AND categoria = %s"
        par.append(cat_s)
    if m:
        sql += " AND DATE_FORMAT(data, '%%Y-%%m') = %s"
        par.append(m)

    sql += " ORDER BY data DESC"
    cur.execute(sql, par)
    trans = cur.fetchall()

    ent = sum(t['valor'] for t in trans if t['tipo'] == 'entrada')
    desp = sum(t['valor'] for t in trans if t['tipo'] == 'despesa')
    sld = ent - desp
    cur.close()

    return render_template('index.html', trans=trans, t_ent=ent, t_desp=desp, sld=sld, lista_cats=cats)


@app.route('/add', methods=['POST'])
def add():
    if not logado(): return redirect(url_for('entrar'))
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO transacoes (id_usuario, tipo, valor, categoria, data, descricao)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session['id_usr'], request.form['tipo'], request.form['valor'],
          request.form['categoria'], request.form['data'], request.form['descricao']))
    mysql.connection.commit()
    cur.close()
    flash('Adicionado!', 'sucesso')
    return redirect(url_for('ini'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not logado(): return redirect(url_for('entrar'))
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        cur.execute("""
            UPDATE transacoes SET tipo=%s, valor=%s, categoria=%s, data=%s, descricao=%s
            WHERE id=%s AND id_usuario=%s
        """, (request.form['tipo'], request.form['valor'], request.form['categoria'],
              request.form['data'], request.form['descricao'], id, session['id_usr']))
        mysql.connection.commit()
        cur.close()
        flash('Atualizado!', 'sucesso')
        return redirect(url_for('ini'))
    cur.execute("SELECT * FROM transacoes WHERE id = %s AND id_usuario = %s", (id, session['id_usr']))
    t = cur.fetchone()
    cur.close()
    return render_template('edit.html', t=t)


@app.route('/del/<int:id>')
def dlt(id):
    if not logado(): return redirect(url_for('entrar'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM transacoes WHERE id = %s AND id_usuario = %s", (id, session['id_usr']))
    mysql.connection.commit()
    cur.close()
    flash('Excluído!', 'sucesso')
    return redirect(url_for('ini'))


if __name__ == '__main__':
    app.run()