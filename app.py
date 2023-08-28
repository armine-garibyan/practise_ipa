from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'pbkdf2:sha256:600000$RCLZXo09ftX8KIA6$b0814c3175e5018c03bb7de6b0a6e73067f7fb673ec1f2d1803d6c23328bac57'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), unique=True, nullable=False)

db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/levels")
def levels():
    return render_template("levels.html")

@app.route("/level_1")
def level_1():
    sounds = pd.read_csv("sounds.csv", names=['sounds', 'words', 'type'], sep=";")
    phonemes = sounds['sounds'].tolist()
    examples = sounds['words'].tolist()
    types = sounds['type'].tolist()
    sound_dict_vowels = {phoneme: example for phoneme, example, type in zip(phonemes, examples, types)
                         if type == 'v'}
    sound_dict_consonants = {phoneme: example for phoneme, example, type in zip(phonemes, examples, types)
                         if type == 'c'}

    # store words of level 1
    phon_br = pd.read_csv("phon_br.csv", names=['word', 'transcription', 'graphemes', 'phonemes', 'level'], sep=";")
    words = phon_br['word'].tolist()
    transcriptions = phon_br['transcription'].tolist()


    return render_template("level_1.html",
                           sound_dict_vowels=sound_dict_vowels,
                           sound_dict_consonants=sound_dict_consonants,
                           transcriptions=transcriptions,
                           words=words)

@app.route("/level_2")
def level_2():
    return render_template("level_2.html")

@app.route("/level_3")
def level_3():
    return render_template("level_3.html")

@app.route("/sign_register", methods=['GET', 'POST'])
def sign_register():
    if request.method == 'GET':
        return render_template("sign_register.html")
    elif request.method =='POST':
        username = request.form.get('username')
        password = request.form.get('userPassword')
        repeat_password = request.form.get('repeatPassword')
        # check if 2 passwords are equal; use generate_password_hash(password)
        if username:
            if password == repeat_password:
                # check if username already exists
                if User.query.filter(User.username == username).first():
                    flash('Choose a different username!', 'error')
                    return redirect(url_for("sign_register"))
                else:
                    user = User(username=username, password_hash=generate_password_hash(password))
                    db.session.add(user)
                    db.session.commit()
                    flash("You've registered successfully!", "info")
                    return render_template("registered.html")
            else:
                flash("Passwords don't match!", "error")
                return redirect(url_for("sign_register"))
        else:
            flash("Please provide a username!", "error")
            return redirect(url_for("sign_register"))

@app.route("/registered", methods=['GET'])
def registered():
    return render_template("registered.html")

