from flask import Flask, session, request, render_template, url_for, redirect
import dataset
import requests, random, string

app = Flask(__name__)
app.secret_key = "zJ2BRqQSf2Gd2MCMULJ7LzrFbhN63xKR"
db: dataset.Database = dataset.connect("postgresql://postgres:postgres@100.65.209.33:5432/postgres")

user_table: dataset.Table = db['users']
foods_table: dataset.Table = db['foods']


@app.route('/')
def index():
    # if "user_id" not in session:
    #     return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/add')
def add():
    return render_template("add.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/api')
def api():
    return render_template("test.html")


@app.route('/login')
def login():
    state = random_strings(15)
    session['state'] = state
    url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=1660874511&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcallback&state={state}&scope=profile"
    return redirect(url)


@app.route('/callback')
def callback():
    state = request.args.get('state')
    code = request.args.get('code')
    if state != session['state']:
        return "Unauthorized"
    res = get_line_auth(code)
    session['access_token'] = res['access_token']
    res = get_current_line_user()
    session['user_id'] = res['userId']
    session['display_name'] = res['displayName']
    session['picture_url'] = res['pictureUrl']
    return redirect(url_for('index'))


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
