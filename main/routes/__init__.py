from flask import render_template, redirect, request, url_for, session
import bcrypt

from main.app import app, mysql

from main.templates.login import login

from main.templates.register import register

from main.templates.calendario import calendario


@app.before_request
def datosUsuario():
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM general_users")
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)
   
@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect('/')

url_inicio='/inicio'
    
@app.route('/inicio')

def inicio():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/index.html')

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
    return render_template('templates/light/app-contact.html')


@app.route('/base')
def base():
    return render_template('templates/light/prueba.html')
