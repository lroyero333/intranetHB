import datetime as dt
import os
from datetime import datetime, time, timedelta
from random import sample

import pymysql
from flask import jsonify
from pymysql import IntegrityError
from werkzeug.utils import secure_filename

from main.run import (agregar_tiempo_transcurrido, app, bcrypt, flash,
                      generarID, jsonify, mysql, redirect, render_template,
                      request, session, url_for)


@app.route('/cursos')
def cursos():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    fecha_actual = datetime.now()
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT cursos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM cursos LEFT JOIN general_users ON cursos.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosCursos = cursor.fetchall()
    # Eliminar cuando se agregue correctamente en la base de datos
    cursor.execute("SELECT * FROM cursos WHERE fecha_fin < %s",
                   (fecha_actual,))
    datos_a_eliminar = cursor.fetchall()
    for dato in datos_a_eliminar:
        cursor.execute("DELETE FROM cursos WHERE id_curso = %s", (dato[0],))
    conexion.commit()
    cursos_con_tiempo = agregar_tiempo_transcurrido(datosCursos, 5)
    return render_template('calendario/templates/cursos/Cursos.html', datosCursos=cursos_con_tiempo)


@app.route('/cursos/<string:curso_id>', methods=['GET', 'POST'])
def verCursos(curso_id):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    query = "SELECT *, DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio1, DATE_FORMAT(fecha_fin, %s) AS fecha_fin2 FROM cursos WHERE id_curso = %s;"
    cursor.execute(query, ('%d %M %Y', '%d %M %Y', curso_id))
    datosCursos = cursor.fetchone()
    query = "SELECT inscripcion_cursos.*, DATE_FORMAT(fecha_inscripcion_curso,%s ) AS fecha_inscripcion, DATE_FORMAT(fecha_inscripcion_curso, %s) AS hora_inscripcion, general_users.Nombre, general_users.segundo_nombre, general_users.Apellido, general_users.segundo_apellido, general_users.foto, general_users.usuario FROM inscripcion_cursos LEFT JOIN general_users ON inscripcion_cursos.id_usuario_fk = general_users.usuario WHERE id_curso_fk= %s;"
    cursor.execute(query, ('%d-%m-%Y', '%H:%i %p', curso_id))
    datosCursosInscritos = cursor.fetchall()
    # Buscar si el usuario actual está inscrito en el curso
    cursor.execute("SELECT * FROM inscripcion_cursos WHERE id_usuario_fk = %s AND id_curso_fk = %s",
                   (session['usuario'], curso_id))
    resultado = cursor.fetchone()
    conexion.commit()

    if request.method == 'POST':
        if resultado is not None:
            # Eliminar al usuario de la tabla de inscripción de cursos
            cursor.execute(
                "DELETE FROM inscripcion_cursos WHERE id_usuario_fk=%s AND id_curso_fk=%s", (session['usuario'], curso_id))
            conexion.commit()
            flash("Has cancelado la inscripción en este curso.", 'correcto')
        else:
            # Insertar un nuevo usuario en la tabla de inscripción de cursos
            id_usuario_fk = session['usuario']
            id_curso_fk = curso_id
            fecha_inscripcion_curso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO inscripcion_cursos (id_inscripcion_cursos,id_usuario_fk, id_curso_fk, fecha_inscripcion_curso) VALUES (%s, %s, %s, %s)"
            params = [generarID(), id_usuario_fk, id_curso_fk,
                      fecha_inscripcion_curso]

            cursor.execute(query, params)
            conexion.commit()

            flash("Te has inscrito exitosamente en este curso.", 'correcto')

        return redirect(f"/cursos/{curso_id}")

    return render_template('calendario/templates/cursos/verCurso.html', datosCursos=datosCursos, inscrito=(resultado is not None), datosCursosInscritos=datosCursosInscritos)


@app.route('/curso/crear', methods=['GET', 'POST'])
def crearCurso():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        if 'crear_curso' in request.form:
            id_usuario_fk = session["usuario"]
            nombre_curso = request.form['nombre_curso']
            fecha_inicio_curso = request.form['fecha_inicio_curso']
            Fecha_fin_curso = request.form['fecha_fin_curso']
            ubicacion = request.form['ubicacion_curso']
            descripcion = request.form['descripcion']
            descripcion_corta = request.form['descripcion_corta']
            horario = request.form['horario_curso']
            fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO cursos (id_curso,id_usuario_fk,nombre_curso, fecha_inicio, fecha_fin, fecha_publicacion, ubicacion, descripcion, descripcion_corta, horario) VALUES (%s, %s,%s,%s, %s, %s, %s, %s, %s, %s)"
            params = [generarID(), id_usuario_fk, nombre_curso, fecha_inicio_curso,
                      Fecha_fin_curso, fecha_publicacion, ubicacion, descripcion, descripcion_corta, horario]

            cursor.execute(query, params)
            conexion.commit()
            flash('Curso agregado satisfactoriamente', 'correcto')

            return redirect('/calendario')
    return render_template('calendario/templates/cursos/crearCursos.html')


@app.route('/cursos/lista/editar', methods=['GET', 'POST'])
def listaCursoEditar():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        if request.form.get('editar_curso'):
            return redirect(f"/curso/editarCurso/{curso_id}")
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()
    return render_template('calendario/templates/cursos/listaEditarCursos.html', cursos=cursos)


@app.route('/cursos/lista/eliminar', methods=['GET', 'POST'])
def listaCursoEliminar():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        if request.form.get('borrar_curso'):
            cursor.execute(
                "DELETE FROM cursos WHERE id_curso = %s;", (curso_id,))
            conexion.commit()
            flash('El curso ha sido eliminado.', 'correcto')
            return redirect('/calendario')
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()
    return render_template('calendario/templates/cursos/listaEliminarCursos.html', cursos=cursos)


@app.route('/curso/editarCurso/<string:curso_id>', methods=['GET', 'POST'])
def editCurso(curso_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cursos WHERE id_curso= %s", curso_id)
    curso = cursor.fetchone()

    if request.method == 'POST':
        # Obtener los valores de los campos del formulario
        id_usuario_fk = session["usuario"]
        nombre_curso = request.form.get('nombre_curso') or curso[2]
        fecha_inicio_curso = request.form.get(
            'fecha_inicio_curso') or curso[3]
        fecha_fin_curso = request.form.get('fecha_fin_curso') or curso[4]
        ubicacion = request.form.get('ubicacion_curso') or curso[6]
        descripcion = request.form.get('descripcion') or curso[7]
        descripcion_corta = request.form.get('descripcion_corta') or curso[8]
        horario = request.form.get('horario_curso') or curso[9]
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = "UPDATE cursos SET id_usuario_fk = %s, nombre_curso = %s, fecha_inicio = %s, fecha_fin = %s, ubicacion = %s, descripcion = %s, fecha_publicacion = %s , descripcion_corta=%s, horario=%s WHERE id_curso = %s"
        params = [id_usuario_fk, nombre_curso, fecha_inicio_curso,
                  fecha_fin_curso, ubicacion, descripcion, fecha_publicacion, descripcion_corta, horario, curso_id]

        cursor.execute(query, params)
        conexion.commit()

        flash('El curso ha sido editado correctamente.', 'correcto')
        return redirect('/calendario')

    return render_template('calendario/templates/cursos/editarCurso.html', curso=curso)
