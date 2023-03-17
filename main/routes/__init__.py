import json
from flask import render_template, redirect, request, url_for, session
import bcrypt

from main.app import app, mysql

from main.templates.login import login

from main.templates.register import register

from main.templates.calendario import calendario


"""@app.before_request
def datosUsuario():

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, Apellido, id_cargo_fk, foto FROM general_users")
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)
"""

@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect('/')


url_inicio = '/inicio'


@app.route('/inicio')
def inicio():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/index.html')


"""
@app.route('/inicio')
def inicio():
   usuario_json = request.args.get('usuario')
    user = json.loads(usuario_json)
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/index.html',user = user)"""


@app.route('/Noticias')
def noticias():
    if not 'login' in session:
        return redirect('/')
    return render_template('sitio/Noticias.html')


@app.route('/proyectos')
def programacion():
    if not 'login' in session:
        return redirect('/')
    return render_template('sitio/proyectos.html')


@app.route('/static/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/tareas')
def tareas():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/app-taskboard.html')


@app.route('/inventario')
def inventario():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/app-taskboard.html')


@app.route('/crear-evento')
def crearEvento():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/app-taskboard.html')


@app.route('/orden-perfiles')
def ordenarPerfil():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/app-taskboard.html')


@app.route('/crear-proyecto')
def crearProyecto():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/app-taskboard.html')


@app.route('/empleados')
def listaEmpleados():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/app-taskboard.html')


@app.route('/contactos')
def listaEmpleadosContact():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, Apellido, correo, celular, foto ,profesion FROM general_users")
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)

    return render_template('templates/light/app-contact.html', datosUsuarios=datosUsuarios)


@app.route('/myProfile')
def myperfil():
    if not 'login' in session:
        return redirect('/')
    """_foto=request.files['txtFoto']
    if _foto.filename!="":
        _foto.save("static/images/"+_foto.filename)"""
    return render_template('templates/light/profile.html')
