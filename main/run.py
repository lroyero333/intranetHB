from flask import Flask
from flaskext.mysql import MySQL
import bcrypt
from flask import Flask, render_template, request, redirect, url_for,session,jsonify, flash
import os
from werkzeug.utils import secure_filename



app=Flask(__name__, static_url_path='/static')
app.config['DEBUG'] = True
app.secret_key="18*=70Y3DugTJ;-~&Jnr"
mysql=MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='login'

"""app.config['MYSQL_DATABASE_HOST']='srv652.hstgr.io'
app.config['MYSQL_DATABASE_USER']='u122395259_HumanBionics'
app.config['MYSQL_DATABASE_PASSWORD']='Human100.'
app.config['MYSQL_DATABASE_DB']='u122395259_intranerHB'
"""
mysql.init_app(app)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
from main.routes import *
