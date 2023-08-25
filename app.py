from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

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
        # long_name = request.form['long_name']
        # add to database
        return render_template("registered.html")

@app.route("/registered", methods=['GET'])
def registered():
    return render_template("registered.html")

