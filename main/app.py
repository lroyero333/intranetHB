from flask import Flask
from flaskext.mysql import MySQL
import bcrypt
from flask import Flask, render_template, request, redirect, url_for,session
import os
from werkzeug.utils import secure_filename



app=Flask(__name__, static_url_path='/static')
app.config['CARPETA_IMAGENES'] = '..\\static\\images'
app.config['DEBUG'] = True
app.secret_key="develoteca"
mysql=MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='login'
mysql.init_app(app)


from main.routes import *

