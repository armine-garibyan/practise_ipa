from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, url_for, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# configure app
app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)

# Configure session extension
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'practise_ipa'

# Initialize the session extension
Session(app)

# login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access your account."
login_manager.login_message_category = "danger"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), unique=True, nullable=False)
    joined_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    correct_1 = db.Column(db.Integer, nullable=False)
    incorrect_1 = db.Column(db.Integer, nullable=False)
    correct_2 = db.Column(db.Integer, nullable=False)
    incorrect_2 = db.Column(db.Integer, nullable=False)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template('index.html')


@app.route("/levels")
def levels():
    return render_template("levels.html")

@app.route('/about')
def about():
    return render_template("about.html")

# split words by level of difficulty
phon_br = pd.read_csv("phon_br.csv", names=['word', 'transcription'], sep=";")
def char_count(text):
    length = 0
    if ',' in str(text):
        for char in text.split(",")[0]:
            if char != "ˈ" and char != "ˌ" and char != ":":
                length += 1
        return length
    else:
        for char in text.split(",")[0]:
            if char != "ˈ" and char != "ˌ" and char != ":":
                length += 1
        return length
phon_br['numLetters'] = phon_br['word'].apply(char_count)
phon_br['numPhonemes'] = phon_br['transcription'].apply(char_count)
phon_br['difference'] = phon_br['numLetters'] - phon_br['numPhonemes']
phon_br.to_csv('phon_br_with_charcount.csv', index=False)

easy = phon_br[phon_br['difference'] == 0]
hard = phon_br[(phon_br['difference'] < 0) | (phon_br['difference'] > 0)]


@app.route("/level_1", methods=['GET', 'POST'])
def level_1():
    sounds = pd.read_csv("sounds.csv", names=['sounds', 'words', 'type'], sep=";")
    phonemes = sounds['sounds'].tolist()
    examples = sounds['words'].tolist()
    types = sounds['type'].tolist()
    sound_dict_vowels = {phoneme: example for phoneme, example, type in zip(phonemes, examples, types)
                        if type == 'v'}
    sound_dict_consonants = {phoneme: example for phoneme, example, type in zip(phonemes, examples, types)
                        if type == 'c'}

    # store words for level 1
    words = easy['word'].tolist()
    transcriptions = easy['transcription'].tolist()

    if "user_id" in session:
        user = User.query.get(session["user_id"])
    else:
        user = None

    if request.method == 'POST':
        correct = int(request.form.get('correct_point', 0))
        incorrect = int(request.form.get('incorrect_point', 0))

        if user:
            user.correct_1 += int(correct)
            user.incorrect_1 += int(incorrect)
            db.session.commit()



    return render_template('level_1.html',
                           sound_dict_vowels=sound_dict_vowels,
                           sound_dict_consonants=sound_dict_consonants,
                           transcriptions=transcriptions,
                           user=user,
                           words=words)


@app.route("/level_2", methods=['GET', 'POST'])
def level_2():
    sounds = pd.read_csv("sounds.csv", names=['sounds', 'words', 'type'], sep=";")
    phonemes = sounds['sounds'].tolist()
    examples = sounds['words'].tolist()
    types = sounds['type'].tolist()
    sound_dict_vowels = {phoneme: example for phoneme, example, type in zip(phonemes, examples, types)
                        if type == 'v'}
    sound_dict_consonants = {phoneme: example for phoneme, example, type in zip(phonemes, examples, types)
                        if type == 'c'}

    # store words for level 1
    words = hard['word'].tolist()
    transcriptions = hard['transcription'].tolist()

    if "user_id" in session:
        user = User.query.get(session["user_id"])
    else:
        user = None

    if request.method == 'POST':
        correct = int(request.form.get('correct_point', 0))
        incorrect = int(request.form.get('incorrect_point', 0))

        if user:
            user.correct_2 += int(correct)
            user.incorrect_2 += int(incorrect)
            db.session.commit()

    return render_template('level_2.html',
                           sound_dict_vowels=sound_dict_vowels,
                           sound_dict_consonants=sound_dict_consonants,
                           transcriptions=transcriptions,
                           words=words)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('userPassword')
        repeat_password = request.form.get('repeatPassword')
        # check if 2 passwords are equal; use generate_password_hash(password)
        if username:
            if password == repeat_password:
                # check if username already exists
                with app.app_context():
                    if User.query.filter(User.username == username).first():
                        flash('Choose a different username!', 'error')
                        return redirect(url_for("register"))
                    else:
                        user = User(username=username,
                                    password_hash=generate_password_hash(password),
                                    correct_1=0,
                                    incorrect_1=0,
                                    correct_2=0,
                                    incorrect_2=0)
                        db.session.add(user)
                        db.session.commit()
                        return render_template('registered.html')
            else:
                flash("Passwords don't match!", "error")
                return redirect(url_for("register"))
        else:
            flash("Please provide a username!", "error")
            return redirect(url_for("register"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['userPassword']
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            login_user(user, remember=remember)
            return redirect(url_for('my_account'))
        elif user:
            flash("Invalid password.", "danger")
            return redirect(url_for("login"))
        else:
            flash("User does not exist.", "danger")
            return redirect(url_for("register"))


@app.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    if request.method == "GET":
        if "user_id" in session:
            # fetch user's data from db
            user = User.query.get(session["user_id"])
            correct_1 = user.correct_1
            incorrect_1 = user.incorrect_1
            correct_2 = user.correct_2
            incorrect_2 = user.incorrect_2
            return render_template("my_account.html",
                                   user=user.username,
                                   correct_1=correct_1,
                                   incorrect_1=incorrect_1,
                                   correct_2=correct_2,
                                   incorrect_2=incorrect_2
                                   )
        else:
            flash("Please log in to access your account.")
            return redirect(url_for("login"))
    elif request.method == "POST":
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
