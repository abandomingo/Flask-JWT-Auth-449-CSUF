# import required modules
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_cors import CORS
import jwt
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import pymysql

# load environment variables from .env file
load_dotenv()

import os
import json



UPLOAD_FOLDER = os.getenv('STORAGE_PATH')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

# CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


# set the secret key for generating and decoding JWT tokens
app.secret_key = os.getenv('JWT_SECRET_KEY')

# set the upload folder and maximum content length
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1000 * 1000 #8 megabytes max

# connect to the MySQL database CHANGE THIS TO YOUR DB SETTINGS
conn = pymysql.connect(
        host='127.0.0.1',
        user='root', 
        password = os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DB'),
        )

cur = conn.cursor()

# function to generate JWT tokens
def generate_jwt_token(content):
    encoded_content = jwt.encode(content, app.secret_key, algorithm="HS256")
    token = str(encoded_content)
    return token

def decode_user(token: str):
    decoded_data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
    return decoded_data

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
  if request.method == 'GET':
    # if a GET request is received, fetch all accounts from the database and return them as a list of JSON strings
    cur.execute('SELECT * FROM accounts')
    accounts = cur.fetchall()
    accountsList = []
    for row in accounts:
      accountsList.append(json.dumps(row))
    return accountsList
  if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    # if a POST request is received and the username and password fields are present, check if the user exists and if the password is correct
    username = request.form['username']
    password = request.form['password']
    cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password))
    account = cur.fetchone()
    # if the account is not found, return a 401 Unauthorized error with a JSON message
    if account == None:
      return make_response(
    jsonify({
      "message": "User does not exists", 
      "error": "Unauthorized", 
      "data": None
    }), 401
    )
    this_id = account[0]
    jwt_token = generate_jwt_token({"id": this_id})
  # if the account is found, generate a JWT token for the user and return it as a JSON message
  if account:
    return jsonify({"jwt_token": jwt_token})
  # if something went wrong, return a 401 Unauthorized error with a JSON message
  return make_response(
  jsonify({
    "message": "User does not exists", 
    "error": "Unauthorized", 
    "data": None
  }), 401
  )

@app.route('/admin', methods =['POST'])
def admin():
    if request.method == 'POST' and 'jwt_token' in request.form:
         # if a POST request is received and jwt_token field is present, check take the jwt_token
        jwt_token = request.form['jwt_token']
        try:
            obj = decode_user(jwt_token)
        except jwt.exceptions.DecodeError:
            # if decoded content is not available or jwt_token is wrong, return a 401 Unauthorized error with a JSON message
            return make_response(
                jsonify({
                    "message": "Invalid token",
                    "error": "Unauthorized",
                    "data": None
                }), 401
            )
        this_id = obj['id']
        cur.execute('SELECT * FROM accounts WHERE id = %s', (this_id))
        account = cur.fetchone()
        #once the id taken from the decoded content, find in database and return user account info
        return jsonify({'user': account})
    # if there is no POST Request or no jwt_token in request
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
        
@app.route('/upload', methods=['POST'])
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
        #if the extension is not in the selected approved file types return error
        if not allowed_file(file.filename):
          return make_response(
            jsonify({
              "message": "This File Type is not allowed", 
              "error": "Not", 
              "data": file.filename
            }), 406
            )
        #if it is present and it is valid, upload filename to filepath set before
        if file and allowed_file(file.filename):
          filename = secure_filename(file.filename)
          file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
          return 'Success'
    #if the request is not a post request, give error
    return make_response(
		jsonify({
			"message": "Must be a POST request", 
			"error": "Method Not Allowed", 
			"data": None
		}), 405
    )

#start app on localhost port 5000
if __name__ == "__main__":
	app.run(host ="localhost", port = int("5000"))
