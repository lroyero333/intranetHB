from random import sample
from flask import request, redirect, send_file, send_from_directory
import os
import json
from flask import render_template, redirect, request, url_for, session, flash
import bcrypt
from werkzeug.utils import secure_filename
from main.app import app, mysql
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from main.templates.login import login
from main.templates.register import register
from main.templates.calendario import calendario
from main.templates.error import error
from main.templates.nomina_certificados import nomina_certificado
from main.templates.usersCRUD import usersCRUD

"""import pyrebase

config = {
    "apiKey": "AIzaSyDsjemDIJl28I1dkoGW4aFIojZ6pJeMZCY",
    "authDomain": "intranethb.firebaseapp.com",
    "databaseURL": "https://firebase.google.com/docs/web/setup#available-libraries",
    "projectId": "intranethb",
    "storageBucket": "intranethb.appspot.com",
    "messagingSenderId": "20219685128",
    "appId": "1:20219685128:web:3656bb076ac7222d9524bd"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

def upload_image_to_firebase_storage(file_path):
    filename = file_path.split("/")[-1]
    storage.child("images/" + filename).put(file_path)
    url = storage.child("images/" + filename).get_url(None)
    return url

"""

"""
@app.before_request
def datosUsuario():

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(
        "SELECT *  FROM general_users WHERE usuario = %s", (session["usuario"]))
    row = cursor.fetchone()
    conexion.commit()
    session["login"]=True
    session["usuario"]=row[26]
    session["nombre"]=row[1]
    session["nombre2"]=row[2]
    session["apellido"]=row[3]
    session["apellido2"]=row[4]
    session["genero"]=row[5]
    session["fecha_nacimiento"]=row[7]
    session["edad"]=row[28]
    session["correo"]=row[7]
    session["identificacion"]=row[8]
    session["direccion"]=row[9]
    session["barrio"]=row[10]
    session["ciudad"]=row[11]
    session["departamento"]=row[12]
    session["pais"]=row[13]
    session["telefono"]=row[14]
    session["celular"]=row[15]
    session["habilidades"]=row[16]
    session["profesion"]=row[17]
    session["cargo"]=row[18]
    session["institucion"]=row[19]
    session["posgrado"]=row[20]
    session["entidad_salud"]=row[21]
    session["tipo_sangre"]=row[22]
    session["foto"]=row[23]
    session["nombre_contacto"]=row[24]
    session["numero_contacto"]=row[25]
"""
def stringAleatorio():
    string_aleatorio="0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud=10
    secuencia=string_aleatorio.upper()
    resultado_aleatorio= sample(secuencia, longitud)
    string_aleatorio= "".join(resultado_aleatorio)
    return string_aleatorio

@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect('/')


url_inicio = '/inicio'


"""@app.route('/notificaciones')
def notificaciones():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Recuperar las notificaciones sin leer de la base de datos
    notificaciones = Notification.query.filter_by(
        user_id=session['user_id'], leido=False).all()

    # Marcar las notificaciones como leídas y actualizar la base de datos
    for notificacion in notificaciones:
        notificacion.leido = True
        db.session.add(notificacion)
    db.session.commit()

    # Eliminar las notificaciones leídas de la sesión del usuario
    session.pop('notificaciones', None)

    return render_template('notificaciones.html', notificaciones=notificaciones)"""


@app.route('/inicio')
def inicio():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT cursos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM cursos LEFT JOIN general_users ON cursos.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosCursos = cursor.fetchall()
    conexion.commit()
    cursos_con_tiempo = []
    for curso in datosCursos:
        fecha_insertado = curso[5]
        fecha_actual = datetime.now()
        diferencia = relativedelta(fecha_actual, fecha_insertado)
        if diferencia.years > 0:
            tiempo_transcurrido = f"hace {diferencia.years} años"
        elif diferencia.months > 0:
            tiempo_transcurrido = f"hace {diferencia.months} meses"
        elif diferencia.days > 0:
            tiempo_transcurrido = f"hace {diferencia.days} días"
        elif diferencia.hours > 0:
            tiempo_transcurrido = f"hace {diferencia.hours} horas"
        elif diferencia.minutes > 0:
            tiempo_transcurrido = f"hace {diferencia.minutes} minutos"
        else:
            tiempo_transcurrido = f"hace {diferencia.seconds} segundos"
        # convertir a lista para poder modificar
        curso_con_tiempo = list(curso)
        curso_con_tiempo.append(tiempo_transcurrido)
        cursos_con_tiempo.append(curso_con_tiempo)

    cursor.execute("SELECT noticias.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM noticias LEFT JOIN general_users ON noticias.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosNoticias = cursor.fetchall()
    conexion.commit()
    noticias_con_tiempo = []
    for noticia in datosNoticias:
        fecha_insertado = noticia[4]
        fecha_actual = datetime.now()
        diferencia = relativedelta(fecha_actual, fecha_insertado)
        if diferencia.years > 0:
            tiempo_transcurrido = f"hace {diferencia.years} años"
        elif diferencia.months > 0:
            tiempo_transcurrido = f"hace {diferencia.months} meses"
        elif diferencia.days > 0:
            tiempo_transcurrido = f"hace {diferencia.days} días"
        elif diferencia.hours > 0:
            tiempo_transcurrido = f"hace {diferencia.hours} horas"
        elif diferencia.minutes > 0:
            tiempo_transcurrido = f"hace {diferencia.minutes} minutos"
        else:
            tiempo_transcurrido = f"hace {diferencia.seconds} segundos"
        # convertir a lista para poder modificar
        # Cambiar el nombre de la variable aquí
        noticia_con_tiempo = list(noticia)
        noticia_con_tiempo.append(tiempo_transcurrido)
        noticias_con_tiempo.append(noticia_con_tiempo)  # Agregar a la lista

    return render_template('templates/light/index.html', datosCursos=cursos_con_tiempo, datosNoticias=noticias_con_tiempo)


@app.route('/Noticias')
def noticias():
    if not 'login' in session:
        return redirect('/')
    return render_template('sitio/Noticias.html')


@app.route('/static/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/contactos')
def listaEmpleadosContact():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, Apellido, correo, celular, foto ,profesion FROM general_users WHERE usuario != %s;", session["usuario"])
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)

    return render_template('templates/light/app-contact.html', datosUsuarios=datosUsuarios)

@app.route('/myProfile', methods=['GET', 'POST'])
def myperfil():
    if not 'login' in session:
        return redirect('/')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT general_users.*, cargos.nombre_cargo FROM general_users LEFT JOIN usuario_cargo ON general_users.id = usuario_cargo.id_usuario_fk LEFT JOIN cargos ON usuario_cargo.id_cargo_fk = cargos.id_cargo WHERE usuario= %s;", session['usuario'])
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)
    # Obtener la información de la sesión actual

    # Renderizar el perfil actualizado
    return render_template('templates/light/profile.html',  datosUsuarios=datosUsuarios)

@app.route('/ver_archivo/<string:filename>', methods=['GET','POST'])
def ver_archivo(filename):
    if 'ver_certificado':
        ruta_archivo = os.path.join(app.root_path, 'static', 'archivos', 'certificados', filename)
    elif 'ver_nomina':
        directorio_archivos = os.path.abspath(os.path.join(app.root_path, '..', 'static', 'archivos', 'certificados', filename))

    return send_file(ruta_archivo, as_attachment=True)
