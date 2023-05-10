import datetime
import os
from random import sample
from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for
from main.run import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash

@app.route('/miTrabajo')
def miTrabajo():
    
    return render_template('miTrabajo/templates/miTrabajo.html')
