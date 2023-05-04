import random
import string
from datetime import datetime

import dataset
import requests
from flask import Flask, session, request, render_template, url_for, redirect

app = Flask(__name__)
app.secret_key = "zJ2BRqQSf2Gd2MCMULJ7LzrFbhN63xKR"
db: dataset.Database = dataset.connect("postgresql://postgres:postgres@100.65.209.33:5432/postgres")

user_table: dataset.Table = db['users']
foods_table: dataset.Table = db['foods']


@app.route('/')
def index():
    item_list = []
    for row in foods_table.find():
        n_row = dict(row)
        expiry = datetime.strftime(row["expiry"], "%Y/%m/%d")
        user = user_table.find_one(line_id=row["owner_line_id"])
        n_row.update(dict(owner_name=user["line_name"], owner_room=user["room"], expiry=expiry))
        item_list.append(n_row)
    return render_template("index.html", item_list=item_list)


@app.route('/add')
def add():
    if "line_id" not in session:
        return redirect(url_for('login') + '?redirect_page=add')
    return render_template("add.html")


@app.route('/settings')
def settings():
    return render_template("settings.html")


@app.route('/api')
def api():
    return render_template("test.html")


@app.route('/login')
def login():
    if "redirect_page" in request.args:
        session['redirect_page'] = request.args['redirect_page']
    state = random_strings(15)
    session['state'] = state
    url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=1660874511&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcallback&state={state}&scope=profile"
    return redirect(url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/callback')
def callback():
    state = request.args.get('state')
    code = request.args.get('code')
    if state != session['state']:
        return "Unauthorized"
    res = get_line_auth(code)
    session['access_token'] = res['access_token']
    res = get_current_line_user()
    session['line_id'] = res['userId']
    session['display_name'] = res['displayName']
    session['picture_url'] = res['pictureUrl']
    redirect_page = session['redirect_page'] if "redirect_page" in session else "index"
    user_row = user_table.find_one(line_id=session['line_id'])
    session["room"] = user_row["room"] if user_row else None
    return redirect(url_for(redirect_page))


def random_strings(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def get_line_auth(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://127.0.0.1:5000/callback',
        'client_id': '1660874511',
        'client_secret': 'a3a3ec3b6288d6b03134afaf8d58a725'
    }
    response = requests.post('https://api.line.me/oauth2/v2.1/token', data=data)
    return response.json()


def get_current_line_user():
    headers = {
        'Authorization': f'Bearer {session["access_token"]}'
    }
    response = requests.get('https://api.line.me/v2/profile', headers=headers)
    return response.json()


if __name__ == '__main__':
    app.run()
