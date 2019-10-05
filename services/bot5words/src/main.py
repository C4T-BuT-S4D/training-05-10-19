# coding=utf-8
from gevent import monkey; monkey.patch_all()

import session
import crawler

from bottle import default_app, request, response, redirect, abort
from bottle import jinja2_template as template
from bottle import jinja2_view as view
from bottle.ext import sqlite
from enum import Enum

from auth import logged_in, get_data_from_session

app = default_app()
plugin = sqlite.Plugin(dbfile='test.db')
app.install(plugin)


class UserType(Enum):
    GhostWriter = 1
    MC = 2


def encrypt_link(t_id):
    bin_string = bin(t_id)[2:]
    bin_string = bin_string.replace('0', 'x')
    bin_string = bin_string.replace('1', 'y')
    return bin_string


def decrypt_link(link):
    try:
        link = link.replace('x', '0')
        link = link.replace('y', '1')
        t_id = int(link, 2)
        return t_id
    except ValueError:
        return -1


@app.route('/')
@view('index')
def index():
    data = get_data_from_session()
    if 'id' in data.keys():
        return redirect('/page')
    else:
        return {}


@app.route('/register')
@view('register')
def register():
    return {}


@app.route('/register', method='POST')
def register(db):
    login = request.forms.login
    password = request.forms.password
    user_type = request.forms.get('type', None)
    if login and password and user_type:
        try:
            db.execute("INSERT INTO users (login,password,user_type) VALUES (?,?,%s)" % user_type,
                       (login, password))
        except Exception as e:
            print(e)
            return "Login already exist"
        else:
            return redirect('/login')
    else:
        return "All fields are required"


@app.route('/login')
@view('login')
def login_get():
    return {}


@app.route('/login', method='POST')
def login_post(db):
    login = request.forms.login
    password = request.forms.password
    if login and password:
        row = db.execute("SELECT * FROM users WHERE login = ? and password = ?", (login, password)).fetchone()
        if row:
            sess = session.session.new_session()
            sess.set({'id': row[0], 'user_type': row[1], 'login': row[2]})
            response.set_cookie('SESSION', sess.key)
            return redirect('/page')
        return "User not found"
    else:
        return "All field are required"


@app.route("/page")
@logged_in
def user_page(db):
    data = get_data_from_session()
    user = data['login']
    if data['user_type'] == UserType.GhostWriter.value:
        return template('gost', user=user)
    else:
        return template('mc', user=user)



@app.route('/create', method='POST')
@logged_in
def create_text(db):
    data = get_data_from_session()
    if data['user_type'] != UserType.GhostWriter.value:
        return "Sorry. Only for ghost-writers"
    else:
        name = request.forms.name
        text = request.forms.text
        print(text, name)
        if name and text:
            db.execute('INSERT INTO texts (author_id,name,text) VALUES(?,?,?)', (data['id'], name, text))
            return redirect('/list')
        else:
            return "All field are required"


@app.route('/create')
@logged_in
def create(db):
    data = get_data_from_session()
    if data['user_type'] != UserType.GhostWriter.value:
        return "Sorry. Only for ghost-writers"
    else:
        return template('create')


@app.route('/create_url', method="POST")
@logged_in
def create_text_from_url(db):
    data = get_data_from_session()
    if data['user_type'] != UserType.GhostWriter.value:
        return "Sorry. Only for ghost-writers"
    else:
        name = request.forms.name
        url = request.forms.url
        if url and name:
            text = crawler.get_text_from_url(url)
            db.execute('INSERT INTO texts (author_id,name,text) VALUES(?,?,?)', (data['id'], name, text))
            return redirect('/list')
        else:
            return "All field are required"


@app.route('/list')
@logged_in
def text_page(db):
    data = get_data_from_session()
    if data['user_type'] == UserType.GhostWriter.value:
        texts = db.execute('SELECT * FROM texts where author_id = ?', [int(data['id'])]).fetchall()
        texts = [list(x) for x in texts]
        return template('list', texts=texts)
    else:
        return "Sorry. Only for ghost-writers"


@app.route('/find')
@logged_in
def find(db):
    data = get_data_from_session()
    item = request.query.get('item', None)
    if not item:
        return "Item not found"
    t_id = decrypt_link(item)
    data = db.execute('SELECT * FROM texts INNER JOIN users ON users.id = texts.author_id and texts.id = ?',
                      [t_id]).fetchone()
    if not data:
        return "Item not found"
    text_name = data[2]
    text = data[3]
    author = data[6]
    return template('text_page', text=text, text_name=text_name, author=author, key=item)
    # name = text[]
    # return dict(text=text)


@app.route('/text/<text_id>')
@logged_in
def text_page_detail(db, text_id):
    data = get_data_from_session()
    if data['user_type'] == UserType.GhostWriter.value:
        text_object = db.execute('SELECT * FROM texts INNER JOIN users ON users.id = texts.author_id and texts.id = ?',
                                 (text_id,)).fetchone()
        text_id = int(text_id)
        if not text_object:
            abort(404, text="Not found")
            return

        u_id = int(data['id'])
        text_author_id = int(text_object[1])
        assert text_author_id == u_id
        text_name = text_object[2]
        text = text_object[3]
        author = text_object[6]
        return template('text_page', text=text, text_name=text_name, author=author, key=encrypt_link(text_id))
    else:
        return "Sorry. Only for ghost-writers"


@app.route('/logout')
def logout():
    sess = session.session.get_session(request.cookies.get('SESSION', ''))
    sess.delete()
    response.delete_cookie('SESSION')
    return redirect('/')


if __name__ == '__main__':
    app.config.load_config('config.ini')
    session.session = session.FileSessionFabric(app.config['sessions.seed'], 12)
    import sqlite3

    conn = sqlite3.connect('test.db')
    db = conn.cursor()
    init_query = 'CREATE TABLE IF NOT EXISTS users(id  integer NOT NULL PRIMARY KEY AUTOINCREMENT,user_type integer,login text UNIQUE ,password text)'
    db.execute(init_query)
    init_query = 'CREATE TABLE IF NOT EXISTS texts(id  integer NOT NULL PRIMARY KEY AUTOINCREMENT,author_id integer,name text,text text)'
    db.execute(init_query)
    app.run(host='0.0.0.0', port=5005, server='gevent')

# app.run(server='paste')
