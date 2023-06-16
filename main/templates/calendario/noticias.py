import datetime as dt
import os
from datetime import datetime, time, timedelta
from random import sample

import pymysql
from flask import jsonify
from pymysql import IntegrityError
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (agregar_tiempo_transcurrido, app, bcrypt, fecha_actualCO,
                      flash, generarID, jsonify, mysql, redirect,
                      render_template, request, session, stringAleatorio,
                      url_for)

extensionesImagenes = ['.jpg', '.jpeg', '.png']
conexion = mysql.connect()
cursor = conexion.cursor()


def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud = 10
    secuencia = string_aleatorio.upper()
    resultado_aleatorio = sample(secuencia, longitud)
    string_aleatorio = "".join(resultado_aleatorio)
    return string_aleatorio


@app.route('/noticias')
def noticias():
    if not 'login' in session:
        return redirect('/')
    fecha_actual =datetime.now()
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT noticias.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM noticias LEFT JOIN general_users ON noticias.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosNoticias = cursor.fetchall()
    fecha_limite = fecha_actual - dt.timedelta(days=6 * 30)
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM noticias WHERE fecha_publicacion < %s", (fecha_limite,))

    conexion.commit()
    noticias_con_tiempo = agregar_tiempo_transcurrido(datosNoticias, 4)
    return render_template('calendario/templates/noticias/Noticias.html',  datosNoticias=noticias_con_tiempo)


@app.route('/noticia/editarNoticia/<string:noticia_id>', methods=['GET', 'POST'])
def editNoticia(noticia_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and  session['cargo'] != 0:
        return redirect('/inicio')
    cursor.execute("SELECT * FROM noticias WHERE id_noticia= %s", noticia_id)
    noticia = cursor.fetchone()

    if request.method == 'POST':
        # Obtener los valores de los campos del formulario

        usuarioPublica = session["usuario"]
        titulo_noticia = request.form.get('titulo_noticia') or noticia[1]

        descripcion_noticia = request.form.get(
            'descripcion_noticia') or noticia[3]
        fecha_publicacion =datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if request.files['imagen_noticia'].filename != '':
            imagen_noticia = request.files['imagen_noticia']
            filename, file_extension = os.path.splitext(
                imagen_noticia.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash(
                    'La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.', 'error')
            else:
                flash('La noticia se ha actualizado satisfactoriamente', 'correcto')
            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_noticia.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, app.root_path, 'static', 'images', 'Noticias', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_noticia.save(upload_path)

        # Resto del código para procesar y guardar la imagen
        else:
            nuevoNombreImagen = noticia[2]

        query = "UPDATE noticias SET id_usuario_fk = %s, titulo_noticia = %s, imagen_noticia = %s, descripcion_noticia = %s,fecha_publicacion = %s WHERE id_noticia = %s"
        params = [usuarioPublica, titulo_noticia, nuevoNombreImagen,
                  descripcion_noticia, fecha_publicacion, noticia_id]
        cursor.execute(query, params)
        conexion.commit()
        flash('El curso ha sido editado.', 'success')
        return redirect('/calendario')

    return render_template('calendario/templates/noticias/editarNoticia.html', noticia=noticia)


@app.route('/noticias/crear', methods=['GET', 'POST'])
def crearNoticia():
    if request.method == 'POST':
        if 'crear_noticia' in request.form:
            usuarioPublica = session["usuario"]
            titulo_noticia = request.form['titulo_noticia']
            imagen_noticia = request.files['imagen_noticia']
            descripcion_noticia = request.form['descripcion_noticia']
            fecha_publicacion =datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            filename, file_extension = os.path.splitext(
                imagen_noticia.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash(
                    'La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.', 'error')
                return redirect('/calendario')
            else:
                flash('La noticia se ha agregado satisfactoriamente', 'correcto')
            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_noticia.filename)
            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension
            upload_path = os.path.join(
                basepath, '..', '..', 'static', 'images', 'Noticias', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_noticia.save(upload_path)
            query = "INSERT INTO noticias (id_noticia, titulo_noticia, imagen_noticia, descripcion_noticia, fecha_publicacion,id_usuario_fk) VALUES (%s, %s,%s, %s, %s,%s)"
            params = [generarID(), titulo_noticia, nuevoNombreImagen,
                      descripcion_noticia, fecha_publicacion, usuarioPublica]

            cursor.execute(query, params)
            conexion.commit()

            return redirect('/calendario')

    return render_template('calendario/templates/noticias/crearNoticias.html')


@app.route('/noticias/lista/editar', methods=['GET', 'POST'])
def listaNoticiaEditar():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        noticia_id = request.form.get('noticia_id')
        if request.form.get('editar_noticia'):
            return redirect(f"/noticia/editarNoticia/{noticia_id}")
    cursor.execute("SELECT * FROM noticias")
    noticias = cursor.fetchall()
    conexion.close()
    return render_template('calendario/templates/noticias/listaEditarNoticias.html', noticias=noticias)


@app.route('/noticia/lista/eliminar', methods=['GET', 'POST'])
def listaNoticiaEliminar():
    if request.method == 'POST':
        noticia_id = request.form.get('noticia_id')
        if request.form.get('borrar_noticia'):
            cursor.execute(
                "SELECT imagen_noticia FROM noticias WHERE id_noticia = %s;", (noticia_id,))
            nombre_archivo = cursor.fetchone()
            print('NOMBREARCHIVO', nombre_archivo[0])
            ruta_archivo = os.path.join(
                app.root_path, 'static', 'images', 'Noticias', nombre_archivo[0])
            cursor.execute(
                "DELETE FROM noticias WHERE id_noticia = %s;", (noticia_id,))
            conexion.commit()
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            flash('La noticia ha sido eliminada correctamente', 'correcto')
            return redirect('/calendario')
    cursor.execute("SELECT * FROM noticias")
    noticias = cursor.fetchall()
    return render_template('calendario/templates/noticias/listaEliminarNoticias.html', noticias=noticias)


@app.route('/noticia/<string:noticia_id>', methods=['GET', 'POST'])
def verNoticia(noticia_id):
    if not 'login' in session:
        return redirect('/')
    cursor.execute("SELECT * FROM noticias WHERE id_noticia= %s;", noticia_id)
    datosNoticias = cursor.fetchone()
    conexion.commit()

    return render_template('calendario/templates/noticias/verNoticia.html', datosNoticias=datosNoticias)
