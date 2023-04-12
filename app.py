from flask import Flask, session, request, render_template, url_for

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")

@app.route('/add')
def add():
    return render_template("add.html")

@app.route('/api')
def api():
    pass


if __name__ == '__main__':
    app.run()
