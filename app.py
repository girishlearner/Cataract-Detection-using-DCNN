import os
import uuid
import urllib
import sqlite3
import pickle
from flask import session
from flask import Flask,request,jsonify,render_template,url_for, flash, redirect
#from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request
from tensorflow.keras.preprocessing.image import load_img, img_to_array

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model("Cataract-Model")

ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = ["cataract", "normal"]

def create_table():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phoneNumber INTEGER NOT NULL,
            fullName TEXT NOT NULL,
            Address TEXT NOT NULL
        )
    ''')

    connection.commit()
    connection.close()

create_table()

def predict(filename , model):
    img = load_img(filename , target_size = (224 , 224))
    img = img_to_array(img)
    img = img.reshape(1, 224, 224, 3)

    img = img.astype('float32')
    # img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(2):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:2]
    
    prob_result = []
    class_result = []
    for i in range(2):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result , prob_result


@app.route('/', methods=['GET'])
def root():
        return redirect(url_for('welcome'))

@app.route('/welcome', methods=['GET'])
def welcome():
    return render_template('welcome.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    return render_template('index.html')

import re

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullName = request.form.get('fullName')
        username = request.form.get('username')
        password = request.form.get('password')
        phoneNumber = request.form.get('phoneNumber')
        Address = request.form.get('Address')

        if not re.match(r'^[a-zA-Z0-9]{4,10}$', username):
            flash('Error: Username should be 4 to 10 characters without spaces or special characters.')
        else:
                if not (8 <= len(password) <= 64) or not any(char.islower() for char in password) \
                    or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password) \
                    or not any(char in '!@#$%^&*()-_=+[]{}|;:\'",.<>/?`~' for char in password):
                    flash('Error: Password should be 8 to 64 characters with a mix of lowercase, uppercase, and special characters (no spaces).')
                else:
                    connection = sqlite3.connect('users.db')
                    cursor = connection.cursor()

                
                    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        flash('Error: Username already exists.')
                    else:
                        # Create a new user
                        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                        cursor.execute('INSERT INTO users (username, password, phoneNumber, fullName, Address) VALUES (?, ?, ?, ?, ?)', (username, hashed_password, phoneNumber, fullName, Address))
                        connection.commit()

                        flash('Signup successful! You can now log in.')
                        connection.close()

                        return redirect(url_for('login'))

                    connection.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()

        connection.close()

        if user_data and check_password_hash(user_data[2], password):
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.')

    return render_template('login.html')


@app.route('/success' , methods = ['POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd() , 'Datasets/ODIR-IMAGE')
    if request.method == 'POST':
        if (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                class_result , prob_result = predict(img_path , model)

                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('index.html' , error = error)

    else:
        return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug = True)


