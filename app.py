from datetime import datetime

from flask import Flask, flash, g, redirect, render_template, request, url_for, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

# configure app
app = Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'pbkdf2:sha256:600000$RCLZXo09ftX8KIA6$b0814c3175e5018c03bb7de6b0' \
                 'a6e73067f7fb673ec1f2d1803d6c23328bac57'

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

    # store words for level 1
    words = easy['word'].tolist()
    transcriptions = easy['transcription'].tolist()

    return render_template('level_1.html',
                           sound_dict_vowels=sound_dict_vowels,
                           sound_dict_consonants=sound_dict_consonants,
                           transcriptions=transcriptions,
                           words=words)


@app.route("/level_2")
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
                        user = User(username=username, password_hash=generate_password_hash(password))
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
            return render_template("my_account.html", user=user.username)
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
