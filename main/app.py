from flask import Flask
from flask import render_template, redirect, request, url_for, session
from flaskext.mysql import MySQL
import bcrypt

app=Flask(__name__, static_url_path='/static')
app.secret_key="develoteca"
mysql=MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='login'
mysql.init_app(app)

from main.routes import *

