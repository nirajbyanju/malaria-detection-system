from __future__ import division, print_function

import sys
import os
import glob
import re
import numpy as np

# Keras
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Model saved with Keras model.save()
MODEL_PATH = "malariagit97_final.h5"

# Load your trained model
model = load_model(MODEL_PATH)

def get_database_cursor():
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='', database='malaria')
        cursor = conn.cursor()
        return conn, cursor
    except mysql.connector.Error as e:
        print("Error connecting to MySQL database:", e)
        return None, None

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    conn, cursor = get_database_cursor()
    if conn and cursor:
        cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
        users = cursor.fetchall()

        if len(users) > 0:
            session['user_id'] = users[0][0]
            conn.close()  # Close the connection after using it
            return redirect('/index')
        else:
            conn.close()  # Close the connection after using it
            return redirect('/')
    else:
        return "Database connection error"

@app.route('/index')
def indexr():
    if 'user_id' in session:
        return render_template('index.html')
    else:
        return redirect('/')

@app.route('/add-user', methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    conn, cursor = get_database_cursor()
    if conn and cursor:
        cursor.execute("""INSERT INTO user (user_id, name, email, password) VALUES
                   (NULL, '{}', '{}', '{}')""".format(name, email, password))
        conn.commit()
        conn.close()  # Close the connection after using it
        return "successful"
    else:
        return "Database connection error"

@app.route('/run', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

def model_predict(img_path, model):
    test_image = image.load_img(img_path, target_size=(64, 64))
    test_image = np.array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
   
    result = model.predict(test_image)

    if result[0][0] == 0:
        preds = 'The Person is Infected With Malaria'
        label = 'infected'
    else:
        preds = 'The Person is not Infected With Malaria'
        label = 'notinfected'

    return preds, label

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Make prediction
        preds, label = model_predict(f, model)

        result = preds
        return result

    return None

if __name__ == '__main__':
    app.run(debug=True)
