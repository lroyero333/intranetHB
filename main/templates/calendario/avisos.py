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

conexion = mysql.connect()
cursor = conexion.cursor()

@app.route('/avisos')
def avisos():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT avisos.*,DATE_FORMAT(fecha_publicacion, '%d-%m-%Y') AS fecha_publicacion, general_users.Nombre, general_users.Apellido, general_users.foto FROM avisos LEFT JOIN general_users ON avisos.usuario_publica = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosAvisos = cursor.fetchall()
    conexion.commit()
    avisos_con_tiempo = agregar_tiempo_transcurrido(datosAvisos, 3)
    return render_template('calendario/templates/avisos/Avisos.html', datosAvisos=avisos_con_tiempo, nav='Avisos')

@app.route('/aviso/crear', methods=['GET', 'POST'])
def crearAviso():
    if request.method == 'POST':
        if 'crear_aviso' in request.form:
            id_usuario_fk = session["usuario"]
            nombre_aviso = request.form['nombre_aviso']
            descripcion = request.form['descripcion']
            fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO avisos (id_aviso,titulo_aviso, usuario_publica, fecha_publicacion, descripcion) VALUES (%s,%s,%s,%s, %s)"
            params = [generarID(),nombre_aviso, id_usuario_fk, fecha_publicacion, descripcion]

            cursor.execute(query, params)
            conexion.commit()
            flash('aviso agregado satisfactoriamente','correcto')

            return redirect('/calendario')
    return render_template('calendario/templates/avisos/crearAviso.html')


@app.route('/avisos/lista/editar', methods=['GET', 'POST'])
def listaavisoEditar():
    if request.method == 'POST':
        aviso_id = request.form.get('aviso_id')
        if request.form.get('editar_aviso'):
            return redirect(f"/aviso/editarAviso/{aviso_id}")
    cursor.execute("SELECT * FROM avisos")
    avisos = cursor.fetchall()
    return render_template('calendario/templates/avisos/listaEditarAvisos.html',avisos=avisos)


@app.route('/avisos/lista/eliminar', methods=['GET', 'POST'])
def listaavisoEliminar():
    if request.method == 'POST':
        aviso_id = request.form.get('aviso_id')
        if request.form.get('borrar_aviso'):
            cursor.execute(
                "DELETE FROM avisos WHERE id_aviso = %s;", (aviso_id,))
            conexion.commit()
            flash('El aviso ha sido eliminado.', 'correcto')
            return redirect('/calendario')
    cursor.execute("SELECT * FROM avisos")
    avisos = cursor.fetchall()
    return render_template('calendario/templates/avisos/listaEliminarAvisos.html',avisos=avisos)

@app.route('/aviso/editarAviso/<string:aviso_id>', methods=['GET', 'POST'])
def editaviso(aviso_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1:
        return redirect('/inicio')
    
    cursor.execute("SELECT * FROM avisos WHERE id_aviso= %s", aviso_id)
    aviso = cursor.fetchone()
    
    if request.method == 'POST':
        # Obtener los valores de los campos del formulario
        id_usuario_fk = session["usuario"]
        nombre_aviso = request.form.get('nombre_aviso') or aviso[1]
        descripcion = request.form.get('descripcion') or aviso[4]
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = "UPDATE avisos SET usuario_publica = %s, titulo_aviso = %s , descripcion = %s, fecha_publicacion = %s WHERE id_aviso = %s"
        params = [id_usuario_fk, nombre_aviso, descripcion, fecha_publicacion, aviso_id]

        cursor.execute(query, params)
        conexion.commit()

        flash('El aviso ha sido editado correctamente.', 'correcto')
        return redirect('/calendario')
    
    return render_template('calendario/templates/avisos/editarAviso.html', aviso=aviso)
