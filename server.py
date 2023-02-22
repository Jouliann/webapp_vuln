import sys
import subprocess

subprocess.check_call([sys.executable,'-m', 'pip', 'install', 'Flask'])

from flask import Flask, render_template, request, redirect, send_file
from datetime import datetime
import sqlite3, os

now = datetime.now()

SAFE_FOLDER = ''
app = Flask(__name__)

#Base de dados
TABLE_USERS = '''
CREATE TABLE "UTILIZADORES" ("name" TEXT, "email" TEXT, "age" INTEGER, "morada" TEXT)
'''
TABLE_PEDIDOS = '''
CREATE TABLE "PEDIDOS" ("pedidos" TEXT, "date" TEXT)
'''
TABLE_PEDIDOSNONVUL = '''
CREATE TABLE "PEDIDOSNONVUL" ("pedidos" TEXT, "date" TEXT)
'''
UTILIZADORES = '''INSERT INTO "UTILIZADORES" VALUES 
("Rafael", "testee@hotmail.com", "20", "Nogueira"),
("Diogo", "jaasd@sapo.pt", "30", "Braga"),
("Maria", "dfsdffsd@gmail.com", "25", "Barcelos"),
("Pedro", "sadasfsd@outlook.com", "40", "Porto"),
("Joana", "asdasda@ipb.pt", "36", "Bragança") '''

try:
    conn = sqlite3.connect('av.sqlite')
    conn.execute(TABLE_USERS)
    conn.execute(TABLE_PEDIDOS)
    conn.execute(TABLE_PEDIDOSNONVUL)
    conn.execute(UTILIZADORES)
    conn.commit()
except sqlite3.OperationalError:
    pass

@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/xss_stored', methods=['GET'])
def xss_stored():

    conn = sqlite3.connect('av.sqlite')
    cursor = conn.cursor()
    read = ''' SELECT * FROM PEDIDOS '''
    data = list(cursor.execute(read))

    return render_template('xss_stored.html', data=data )


@app.route('/xss_stored/vulnerable', methods=['GET', 'POST'])
def xss_stored_vul():

    date = now.strftime("%d/%m/%Y %H:%M:%S")
    conn = sqlite3.connect('av.sqlite')
    cursor = conn.cursor()
    
    if request.method == 'POST':

        pedidos = request.form['pedidos']
        INSERT = f'''
                INSERT INTO "PEDIDOS" 
                VALUES("{pedidos}", "{date}")
                '''
        cursor.execute(INSERT)
        conn.commit()

    read = ''' SELECT * FROM PEDIDOS '''
    data = list(cursor.execute(read))

    return render_template('xss_stored.html', data=data)


@app.route('/xss_stored/nonvulnerable', methods=['GET', 'POST'])
def xss_stored_nonvul():

    date = now.strftime("%d/%m/%Y %H:%M:%S")
    conn = sqlite3.connect('av.sqlite')
    cursor = conn.cursor()
    
    if request.method == 'POST':

        pedidos = request.form['pedidos2']
        INSERT = f'''
                INSERT INTO "PEDIDOSNONVUL" 
                VALUES("{pedidos}", "{date}")
                '''
        cursor.execute(INSERT)
        conn.commit()

    read = ''' SELECT * FROM PEDIDOSNONVUL '''
    data2 = list(cursor.execute(read))

    return render_template('xss_stored.html', data2=data2)


@app.route('/xss_reflected', methods=['GET'])
def xss_reflected():
    return render_template('xss_reflected.html')

@app.route('/xss_reflected/vulnerable', methods=['GET'])
def xss_reflected_vul():

    query = None

    if request.method == 'GET':
        query = request.args.get('query')

    return render_template('xss_reflected.html', query=query)


@app.route('/xss_reflected/nonvulnerable', methods=['GET', 'POST'])
def xss_reflected_nonvul():

    query2 = None

    if request.method == 'POST':
        query2 = request.form['query2']
    
    return render_template('xss_reflected.html', query2=query2)

@app.route('/sqli', methods=['GET', 'POST'])
def sqli():

    return render_template('sqli.html')


@app.route('/sqli/vulnerable', methods=['GET', 'POST'])
def sqli_vul(): 
    result = None

    if request.method == 'POST':
        conn = sqlite3.connect('av.sqlite')
        cursor = conn.cursor()
        name = request.form['name']
        query = f''' SELECT email FROM UTILIZADORES WHERE name LIKE "{name}" '''
        result = list(cursor.execute(query))

    return render_template('sqli.html', result=result, name=name)


@app.route('/sqli/nonvulnerable', methods=['GET', 'POST'])
def sqli_nonvul():
    result = None

    if request.method == 'POST':
        conn = sqlite3.connect('av.sqlite')
        cursor = conn.cursor()
        name = request.form['name']
        result = list(cursor.execute("SELECT email FROM UTILIZADORES WHERE name LIKE ?", (name,)))
        return render_template('sqli.html', result = result)

@app.route("/solucoes", methods=['GET'])
def solucao():
    return render_template('solucoes.html')

if __name__ == "__main__":
    app.run(debug=True)