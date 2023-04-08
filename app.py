# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash, url_for, make_response
# from  flask_mysqldb import MySQL
import pymysql
from flask_cors import CORS
import jwt
# import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

import os
import json


UPLOAD_FOLDER = os.getenv('STORAGE_PATH_MAC')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = os.getenv('JWT_SECRET_KEY')

conn = pymysql.connect(
        host='127.0.0.1',
        user='root', 
        password = os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DB'),
        )

cur = conn.cursor()

def generate_jwt_token(content):
    encoded_content = jwt.encode(content, app.secret_key, algorithm="HS256")
    token = str(encoded_content)
    return token

def decode_user(token: str):
    """
    :param token: jwt token
    :return:
    """
    decoded_data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
    return decoded_data

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	if request.method == 'GET':
		cur.execute('SELECT * FROM accounts')
		accounts = cur.fetchall()
		accountsList = []
		for row in accounts:
			accountsList.append(json.dumps(row))
		return accountsList
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		# cursor = cur.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password))
		account = cur.fetchone()
		this_id = account[0]
		jwt_token = generate_jwt_token({"id": this_id})

		if account:
			return jsonify({"jwt_token": jwt_token})
	return make_response(
		jsonify({
			"message": "User already exists", 
			"error": "Unauthorized", 
			"data": None
		}), 401
    )

@app.route('/admin', methods =['POST'])
def admin():
	if request.method == 'POST' and 'jwt_token' in request.form:
		jwt_token = request.form['jwt_token']
		obj = decode_user(jwt_token)
		this_id = obj['id']
		cur.execute('SELECT * FROM accounts WHERE id = %s', (this_id))
		account = cur.fetchone()
		return jsonify({'user': account})
	return make_response(
		jsonify({
			"message": "User is not recognized as admin", 
			"error": "Unauthorized", 
			"data": None
		}), 401
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return make_response(
			    jsonify({
				    "message": "File doesn't exist", 
					"error": "Not Acceptable", 
					"data": None
				}), 406
            )
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return make_response(
			    jsonify({
				    "message": "No file was selected", 
					"error": "Bad Request", 
					"data": None
				}), 400
            )
        if file and allowed_file(file.filename):
          filename = secure_filename(file.filename)
          file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
          return 'Success'
    return make_response(
		jsonify({
			"message": "Unauthorized user cannot upload file", 
			"error": "Unauthorized", 
			"data": None
		}), 401
    )

if __name__ == "__main__":
	app.run(host ="localhost", port = int("5000"))
