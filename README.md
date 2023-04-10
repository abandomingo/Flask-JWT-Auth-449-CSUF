By: Aban Domingo and Brandon Winkler  
4/5/23, CSUF 449 Backend Engineering


Make sure libraries are installed in venv<br>

pip install pymysql<br>
pip install Flask<br>
pip install PyJWT<br>
pip install python-dotenv<br>
pip install Werkzeug<br>
 or <br>
***pip install -r requirements.txt<br>***

Create a virtual env<br>

***virtualenv venv<br>***

Create an .env file (look at sample-env for more info)<br>
and set file with your own info<br>

MacOS:<br>
***touch .env<br>***

Windows: <br>
***type nul > .env<br>***


To start this file, make sure you are in this projects venv<br>

MacOS:<br>
***. venv/bin/activate<br>***

Windows:<br>
***venv/Scripts/activate <br>***


In venv, to start server<br>

***flask run<br>***

Here are some examples in post man<br>

![Alt text](example.png?raw=true "Example 1")
![Alt text](example2.png?raw=true "Example 2")
