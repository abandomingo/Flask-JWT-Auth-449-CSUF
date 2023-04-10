By: Aban Domingo and Brandon Winkler  
4/5/23, CSUF 449 Backend Engineering


Make sure libraries are installed in venv

pip install pymysql
pip install Flask
pip install PyJWT
pip install python-dotenv
pip install Werkzeug
 or 
pip install -r requirements.txt

Create a virtual env

virtualenv venv

Create an .env file (look at sample-env for more info)
and set file with your own info

MacOS:
touch .env

Windows: 
type nul > .env


To start this file, make sure you are in this projects venv

MacOS:
. venv/bin/activate

Windows:
venv/Scripts/activate 


In venv, to start server

flask run

~Here are some examples in post man~

![Alt text](example.png?raw=true "Example 1")
![Alt text](example2.png?raw=true "Example 2")