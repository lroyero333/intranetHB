import datetime as dt
import os
from datetime import datetime, time, timedelta
from random import sample

import pymysql
from flask import jsonify
from pymysql import IntegrityError
from werkzeug.utils import secure_filename

from main.run import (app, bcrypt, flash, jsonify, mysql, redirect,
                      render_template, request, session, stringAleatorio,
                      url_for)

extensionesImagenes=['.jpg', '.jpeg', '.png']
conexion = mysql.connect()
cursor = conexion.cursor()

@app.route('/proyectos/usuarios/<string:project_id>', methods=['GET', 'POST'])
def userProyecto(project_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 4:
        return redirect('/inicio')
    cursor.execute("SELECT Nombre, segundo_nombre, Apellido, segundo_apellido, usuario FROM general_users")
    integrante = cursor.fetchall()
    cursor.execute("SELECT proyecto_users.*,proyectos.*, DATE_FORMAT(fecha_inicio_user, '%d-%m-%Y')as inicio_user, DATE_FORMAT(fecha_fin_user, '%d-%m-%Y')as fecha_fin_user, general_users.Nombre, general_users.segundo_nombre, general_users.Apellido, general_users.segundo_apellido, general_users.foto FROM proyecto_users JOIN proyectos ON proyecto_users.id_proyecto= proyectos.id_proyecto JOIN general_users ON proyecto_users.id_usuario= general_users.usuario;")
    project_user = cursor.fetchall()
    cursor.execute('SELECT nombre_proyecto FROM proyectos WHERE id_proyecto=%s;', project_id)
    proyecto_nombre=cursor.fetchone()
    conexion.commit()
    fecha_user = datetime.now()
    if request.method == 'POST':
        if 'desactivar_usuario_proyecto' in request.form:
            id_usuario=request.form['desactivar_usuario_proyecto']
            estado_usuario='Inactivo'
            query = "UPDATE proyecto_users SET estado_usuario = %s, fecha_fin_user = %s WHERE id_usuario = %s"
            params = [estado_usuario, fecha_user, id_usuario]
            cursor.execute(query, params)
            conexion.commit()
            flash('Usuario desactivado satisfactoriamente','correcto')

        elif 'activar_usuario_proyecto' in request.form:
            id_usuario=request.form['activar_usuario_proyecto']
            estado_usuario='Activo'
            query = "UPDATE proyecto_users SET estado_usuario = %s, fecha_inicio_user = %s WHERE id_usuario = %s"
            params = [estado_usuario, fecha_user, id_usuario]
            cursor.execute(query, params)
            conexion.commit()
            flash('Usuario activado satisfactoriamente','correcto')
        elif 'asignar_usuario_proyecto' in request.form:
            id_usuario = request.form['integrante_id']
            observaciones_user_proyecto = request.form['observaciones_user_proyecto']
            cursor.execute("SELECT * FROM proyecto_users WHERE id_proyecto=%s AND id_usuario=%s", (project_id, id_usuario))
            usuario_proyecto = cursor.fetchone()
            if usuario_proyecto is not None:
                
                cursor.close()
                flash('El usuario ya pertenece a este proyecto','error')
                return render_template('calendario/templates/proyectos/usersProjects.html', integrante=integrante, project_user=project_user,proyecto_nombre=proyecto_nombre)
            else:
                query = "INSERT INTO proyecto_users (id_proyecto, id_usuario, fecha_inicio_user,observaciones) VALUES (%s, %s, %s,%s)"
                params = [project_id, id_usuario, fecha_user, observaciones_user_proyecto]
                cursor.execute(query, params)
                conexion.commit()
                flash('Usuario agregado satisfactoriamente','correcto')
    cursor.close()
    return render_template('calendario/templates/proyectos/usersProjects.html', integrante=integrante, project_user=project_user,proyecto_nombre=proyecto_nombre) 

@app.route('/proyectos', methods=['GET', 'POST'])
def verProyecto():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM proyectos;")
    datosProyectos = cursor.fetchall()
    conexion.commit()
    conexion.close()
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
    conexion.close()
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
                "DELETE FROM proyectos WHERE id_proyecto = %s;", (proyecto_id,))
            conexion.commit()
            flash('El proyecto ha sido eliminado.', 'correcto')
            return redirect('/proyectos')
    cursor.execute(
        "SELECT * FROM proyectos;")
    datosProyectos = cursor.fetchall()
    conexion.commit()
    conexion.close()
    return render_template('calendario/templates/proyectos/listaEliminarProyecto.html', datosProyectos=datosProyectos)


@app.route('/proyectos/crear', methods=['GET', 'POST'])
def crearProyecto():
    if not 'login' in session:
        return redirect('/')
    if request.method == 'POST' and 'crear_proyecto' in request.form:

        nombre_proyecto = request.form['nombre_proyecto']
        imagen_proyecto = request.files['imagen_proyecto']
        descripcion_proyecto = request.form['descripcion_proyecto']
        filename, file_extension = os.path.splitext(imagen_proyecto.filename)
        if file_extension.lower() not in extensionesImagenes:
            flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
            return redirect('/proyectos')
        else:
            flash('El proyecto se ha agregado satisfactoriamente','correcto')

        basepath = os.path.dirname(__file__)
        filename = secure_filename(imagen_proyecto.filename)

        extension = os.path.splitext(filename)[1]
        nuevoNombreImagen = stringAleatorio()+extension

        upload_path = os.path.join(basepath, '..','..',  'static', 'images','proyectos', nuevoNombreImagen)
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        imagen_proyecto.save(upload_path)


        query = "INSERT INTO proyectos (nombre_proyecto, imagen_proyecto, descripcion_proyecto) VALUES (%s,%s, %s)"
        params = [nombre_proyecto, nuevoNombreImagen, descripcion_proyecto]

        cursor.execute(query, params)
        conexion.commit()
        conexion.close()
        return redirect('/proyectos')        
    
    return render_template('calendario/templates/proyectos/crearProyectos.html')

@app.route('/proyectos/editarProyecto/<string:proyecto_id>', methods=['GET', 'POST'])
def editProyecto(proyecto_id):

    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 4:
        return redirect('/inicio')
    cursor.execute("SELECT * FROM proyectos WHERE id_proyecto= %s", proyecto_id)
    proyecto = cursor.fetchone()
    
    if request.method == 'POST':
        # Obtener los valores de los campos del formulario
        titulo_noticia = request.form.get('titulo_proyecto') or proyecto[1]   
        descripcion_proyecto = request.form.get('descripcion_proyecto') or proyecto[3]

        if request.files['imagen_proyecto'].filename != '':
            imagen_proyecto = request.files['imagen_proyecto']
            filename, file_extension = os.path.splitext(imagen_proyecto.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
                return redirect('/proyectos')
            else:
                flash('El proyecto se ha editado satisfactoriamente','correcto')
            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_proyecto.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension

            upload_path = os.path.join( basepath, '..', '..', 'static', 'images', 'proyectos', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))
            imagen_proyecto.save(upload_path)
        # Resto del código para procesar y guardar la imagen
        else:
            nuevoNombreImagen = proyecto[2]

        query = "UPDATE proyectos SET nombre_proyecto = %s, imagen_proyecto = %s, descripcion_proyecto = %s  WHERE id_proyecto = %s"
        params = [ titulo_noticia, nuevoNombreImagen, descripcion_proyecto, proyecto_id]

        cursor.execute(query, params)
        conexion.commit()

        flash('El proyecto ha sido editado.', 'correcto')
        return redirect('/proyectos')
    
    return render_template('calendario/templates/proyectos/editarProyecto.html', proyecto=proyecto)
