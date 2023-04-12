from flask import Flask, session, request, render_template, url_for
import dataset

app = Flask(__name__)
db: dataset.Database = dataset.connect("postgresql://postgres:postgres@100.65.209.33:5432/postgres")

user_table: dataset.Table = db['users']
foods_table: dataset.Table = db['foods']


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/add')
def add():
    return render_template("add.html")

@app.route('/api')
def api():
    pass


if __name__ == '__main__':
    app.run()
