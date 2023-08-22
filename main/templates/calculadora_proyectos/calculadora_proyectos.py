import datetime
import json
import os
from random import sample

from flask import send_file
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (app, bcrypt, flash, jsonify, mysql, redirect,
                      render_template, request, session, url_for)

extensionesImagenes = ['.jpg', '.jpeg', '.png']

@app.route('/calculadoraProyectos', methods=['POST', 'GET'])
def calculadoraProyectos():
    if not 'login' in session:
        return redirect('/')
    if request.method == 'POST':
        print("Test")
        print(request.form.keys())
        print("Exit")
    else:
        print("Método no permitido: " + request.method)
    # conexion = mysql.connect()
    # cursor = conexion.cursor()
    # cursor.execute(
    #     "SELECT Nombre, Apellido, correo, celular, foto ,profesion ,usuario FROM general_users WHERE estado_usuario='Aceptado';")
    # datosUsuarios = cursor.fetchall()
    # conexion.commit()
    return render_template('calculadora_proyectos/templates/estimacionCostos.html')

@app.route('/registroCostos', methods=['POST', 'GET'])
def registroCostos():
    if not 'login' in session:
        return redirect('/')
    if request.method == 'POST':
        print("Test")
        print(request.form.keys())
        print("Exit")
    else:
        print("Método no permitido: " + request.method)
    # conexion = mysql.connect()
    # cursor = conexion.cursor()
    # cursor.execute(
    #     "SELECT Nombre, Apellido, correo, celular, foto ,profesion ,usuario FROM general_users WHERE estado_usuario='Aceptado';")
    # datosUsuarios = cursor.fetchall()
    # conexion.commit()
    return render_template('calculadora_proyectos/templates/registroCostos.html')