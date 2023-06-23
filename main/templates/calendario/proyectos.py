import datetime as dt
import os
from datetime import datetime, time, timedelta
from random import sample

import pymysql
from flask import jsonify
from pymysql import IntegrityError
from werkzeug.utils import secure_filename

from main.run import (app, bcrypt, fecha_actualCO, flash, generarID, jsonify,
                      mysql, redirect, render_template, request, session,
                      stringAleatorio, url_for)

extensionesImagenes = ['.jpg', '.jpeg', '.png']


@app.route('/proyectos/usuarios/<string:project_id>', methods=['GET', 'POST'])
def userProyecto(project_id):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, segundo_nombre, Apellido, segundo_apellido, usuario FROM general_users")
    integrante = cursor.fetchall()
    query = "SELECT proyecto_users.*,proyectos.*, DATE_FORMAT(fecha_inicio_user, %s)as inicio_user, DATE_FORMAT(fecha_fin_user, %s)as fecha_fin_user, general_users.Nombre, general_users.segundo_nombre, general_users.Apellido, general_users.segundo_apellido, general_users.foto FROM proyecto_users JOIN proyectos ON proyecto_users.id_proyecto= proyectos.id_proyecto JOIN general_users ON proyecto_users.id_usuario= general_users.usuario;"
    cursor.execute(query, ('%d-%m-%Y', '%d-%m-%Y'))
    project_user = cursor.fetchall()
    cursor.execute(
        'SELECT nombre_proyecto FROM proyectos WHERE id_proyecto=%s;', project_id)
    proyecto_nombre = cursor.fetchone()
    conexion.commit()
    fecha_user =datetime.now()
    if request.method == 'POST':
        if 'desactivar_usuario_proyecto' in request.form:
            id_usuario = request.form['desactivar_usuario_proyecto']
            estado_usuario = 'Inactivo'
            query = "UPDATE proyecto_users SET estado_usuario = %s, fecha_fin_user = %s WHERE id_usuario = %s"
            params = [estado_usuario, fecha_user, id_usuario]
            cursor.execute(query, params)
            conexion.commit()
            flash('Usuario desactivado satisfactoriamente', 'correcto')
            return redirect(request.url)

        elif 'activar_usuario_proyecto' in request.form:
            id_usuario = request.form['activar_usuario_proyecto']
            estado_usuario = 'Activo'
            query = "UPDATE proyecto_users SET estado_usuario = %s WHERE id_usuario = %s"
            params = [estado_usuario, id_usuario]
            cursor.execute(query, params)
            conexion.commit()
            flash('Usuario activado satisfactoriamente', 'correcto')
            return redirect(request.url)
        elif 'asignar_usuario_proyecto' in request.form:
            id_usuario = request.form['integrante_id']
            observaciones_user_proyecto = request.form['observaciones_user_proyecto']
            cursor.execute(
                "SELECT * FROM proyecto_users WHERE id_proyecto=%s AND id_usuario=%s", (project_id, id_usuario))
            usuario_proyecto = cursor.fetchone()
            if usuario_proyecto is not None:
                flash('El usuario ya pertenece a este proyecto', 'error')
                return render_template('calendario/templates/proyectos/usersProjects.html', integrante=integrante, project_user=project_user, proyecto_nombre=proyecto_nombre)
            else:
                query = "INSERT INTO proyecto_users (id_proyecto_usuario,id_proyecto, id_usuario, fecha_inicio_user,observaciones) VALUES (%s,%s, %s, %s,%s)"
                params = [generarID(), project_id, id_usuario,
                          fecha_user, observaciones_user_proyecto]
                cursor.execute(query, params)
                conexion.commit()
                flash('Usuario agregado satisfactoriamente', 'correcto')
                return redirect(request.url)
        elif 'editar_usuario_proyecto' in request.form:
            id_participante = request.form['editar_usuario_proyecto']
            return redirect(f'/proyectos/editarUsuarios/{id_participante}')
        elif 'eliminar_usuario_proyecto' in request.form:
            integrante_id = request.form['integrante_id']
            cursor.execute(
                "DELETE FROM proyecto_users WHERE id_proyecto_usuario = %s", integrante_id)
            conexion.commit()
            return redirect(request.url)
    return render_template('calendario/templates/proyectos/usersProjects.html', integrante=integrante, project_user=project_user, proyecto_nombre=proyecto_nombre)


@app.route('/proyectos/editarUsuarios/<string:project_id>', methods=['GET', 'POST'])
def editarUserProyecto(project_id):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute('SELECT proyecto_users.*, general_users.Nombre, general_users.segundo_nombre, general_users.Apellido, general_users.segundo_apellido FROM proyecto_users JOIN general_users ON proyecto_users.id_usuario= general_users.usuario WHERE id_proyecto_usuario=%s;', project_id)
    project_user = cursor.fetchone()

    if 'editar_usuario_proyecto' in request.form:
        proyecto_usuario = request.form['proyecto_usuario']
        observaciones_user_proyecto = request.form.get(
            'observaciones_user_proyecto') or project_user[6]
        fecha_inicio = request.form.get('fecha_inicio') or project_user[4]
        fecha_final = request.form.get('fecha_final') or project_user[5]
        query = "UPDATE proyecto_users SET fecha_inicio_user = %s, fecha_fin_user = %s, observaciones = %s  WHERE id_proyecto_usuario = %s"
        params = [fecha_inicio, fecha_final,
                  observaciones_user_proyecto, project_id]
        cursor.execute(query, params)
        conexion.commit()
        flash('Datos del participante actualizados correctamente.', 'correcto')

        return redirect(f'/proyectos/usuarios/{proyecto_usuario}')
    return render_template('calendario/templates/proyectos/editarUsuariosProyectos.html', project_user=project_user)


@app.route('/misProyectos', methods=['GET', 'POST'])
def misProyectos():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT proyectos.*  FROM proyecto_users LEFT JOIN proyectos ON  proyecto_users.id_proyecto=proyectos.id_proyecto WHERE id_usuario=%s;", session['usuario'])
    datosProyectos = cursor.fetchall()

    conexion.commit()
    return render_template('calendario/templates/proyectos/projects.html', datosProyectos=datosProyectos)


@app.route('/proyectos', methods=['GET', 'POST'])
def verProyectos():
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 4:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT *  FROM proyectos ;")
    datosProyectos = cursor.fetchall()
    conexion.commit()
    return render_template('calendario/templates/proyectos/projects.html', datosProyectos=datosProyectos)


@app.route('/proyectos/lista/editar', methods=['GET', 'POST'])
def verProyectoEditar():
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 4:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        proyecto_id = request.form.get('proyecto_id')
        if request.form.get('editar_proyecto'):
            return redirect(f"/proyectos/editarProyecto/{proyecto_id}")
    cursor.execute(
        "SELECT * FROM proyectos;")
    datosProyectos = cursor.fetchall()
    conexion.commit()

    return render_template('calendario/templates/proyectos/listaEditarProyecto.html', datosProyectos=datosProyectos)


@app.route('/proyectos/lista/eliminar', methods=['GET', 'POST'])
def verProyectoEliminar():
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 4:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        proyecto_id = request.form.get('proyecto_id')
        if request.form.get('borrar_proyecto'):
            cursor.execute(
                "SELECT imagen_proyecto FROM proyectos WHERE id_proyecto = %s;", (proyecto_id,))
            nombre_archivo = cursor.fetchone()
            ruta_archivo = os.path.join(
                app.root_path, 'static', 'images', 'proyectos', nombre_archivo[0])
            cursor.execute(
                "DELETE FROM proyectos WHERE id_proyecto = %s;", (proyecto_id,))
            conexion.commit()
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            flash('El proyecto ha sido eliminado.', 'correcto')
            return redirect('/proyectos')
    cursor.execute(
        "SELECT * FROM proyectos;")
    datosProyectos = cursor.fetchall()
    conexion.commit()
    return render_template('calendario/templates/proyectos/listaEliminarProyecto.html', datosProyectos=datosProyectos)


@app.route('/proyectos/crear', methods=['GET', 'POST'])
def crearProyecto():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST' and 'crear_proyecto' in request.form:

        nombre_proyecto = request.form['nombre_proyecto']
        imagen_proyecto = request.files['imagen_proyecto']
        descripcion_proyecto = request.form['descripcion_proyecto']
        filename, file_extension = os.path.splitext(imagen_proyecto.filename)
        if file_extension.lower() not in extensionesImagenes:
            flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.', 'error')
            return redirect('/proyectos')
        else:
            flash('El proyecto se ha agregado satisfactoriamente', 'correcto')

        basepath = os.path.dirname(__file__)
        filename = secure_filename(imagen_proyecto.filename)

        extension = os.path.splitext(filename)[1]
        nuevoNombreImagen = stringAleatorio()+extension

        upload_path = os.path.join(
            basepath, '..', '..',  'static', 'images', 'proyectos', nuevoNombreImagen)
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        imagen_proyecto.save(upload_path)

        query = "INSERT INTO proyectos (id_proyecto, nombre_proyecto, imagen_proyecto, descripcion_proyecto) VALUES (%s,%s,%s, %s)"
        params = [generarID(), nombre_proyecto, nuevoNombreImagen,
                  descripcion_proyecto]

        cursor.execute(query, params)
        conexion.commit()
        return redirect('/proyectos')

    return render_template('calendario/templates/proyectos/crearProyectos.html')


@app.route('/proyectos/editarProyecto/<string:proyecto_id>', methods=['GET', 'POST'])
def editProyecto(proyecto_id):

    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 4:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM proyectos WHERE id_proyecto= %s", proyecto_id)
    proyecto = cursor.fetchone()

    if request.method == 'POST':
        # Obtener los valores de los campos del formulario
        titulo_noticia = request.form.get('titulo_proyecto') or proyecto[1]
        descripcion_proyecto = request.form.get(
            'descripcion_proyecto') or proyecto[3]

        if request.files['imagen_proyecto'].filename != '':
            imagen_proyecto = request.files['imagen_proyecto']
            filename, file_extension = os.path.splitext(
                imagen_proyecto.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash(
                    'La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.', 'error')
                return redirect('/proyectos')
            else:
                flash('El proyecto se ha editado satisfactoriamente', 'correcto')
            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_proyecto.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, app.root_path, 'static', 'images', 'proyectos', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))
            imagen_proyecto.save(upload_path)
        # Resto del código para procesar y guardar la imagen
        else:
            nuevoNombreImagen = proyecto[2]

        query = "UPDATE proyectos SET nombre_proyecto = %s, imagen_proyecto = %s, descripcion_proyecto = %s  WHERE id_proyecto = %s"
        params = [titulo_noticia, nuevoNombreImagen,
                  descripcion_proyecto, proyecto_id]
        cursor.execute(query, params)
        conexion.commit()
        flash('El proyecto ha sido editado.', 'correcto')
        return redirect('/proyectos')

    return render_template('calendario/templates/proyectos/editarProyecto.html', proyecto=proyecto)
