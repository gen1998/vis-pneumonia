from flask import Flask
from flask import render_template

app = Flask(__name__)

bull = ["hi","hello", "hey"]

@app.route("/")
def index():
    return render_template("index.html", bull=bull)
