import datetime as dt
import json
import os
from datetime import datetime, time, timedelta
from random import sample

from flask import send_file
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (app, bcrypt, fecha_actualCO, flash, generarID, jsonify,
                      mysql, redirect, render_template, request, session,
                      stringAleatorio, url_for)

extensionesImagenes = ['.jpg', '.jpeg', '.png']
conexion = mysql.connect()
cursor = conexion.cursor()


@app.route('/verInventario',  methods=['GET', 'POST'])
def verInventario():
    if not 'login' in session:
        return redirect('/')
    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()

    query = "SELECT elementos_entregados.*, DATE_FORMAT(fecha_entrega, '%d-%m-%Y') AS fecha_entrega, inventario.* FROM elementos_entregados LEFT JOIN inventario ON elementos_entregados.elemento_id = inventario.id_elemento;"
    cursor.execute(query)
    inventario_cargo = cursor.fetchall()

    query = "SELECT  * FROM inventario;"
    cursor.execute(query)
    inventario = cursor.fetchall()

    query = "SELECT movimientos.*, inventario.* FROM movimientos LEFT JOIN inventario ON movimientos.id_elemento = inventario.id_elemento WHERE estado_solicitud='Aceptado' and responsable=%s;"
    cursor.execute(query, (session['usuario'],))
    prestados = cursor.fetchall()

    fecha_actual =fecha_actualCO()

    return render_template('inventario/templates/verInventario.html', inventario_cargo=inventario_cargo, inventario=inventario, prestados=prestados)


@app.route('/inventario/listaEntregarInventario', methods=['GET', 'POST'])
def listaEntregarInventario():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT movimientos.id_movimiento,movimientos.tipo_movimiento, general_users.Nombre, general_users.Apellido, inventario.nombre_elemento FROM movimientos LEFT JOIN general_users ON movimientos.responsable = general_users.usuario LEFT JOIN inventario ON movimientos.id_elemento=inventario.id_elemento WHERE tipo_movimiento='Salida' and estado_solicitud='Aceptado';")
    materiales_prestados = cursor.fetchall()
    if request.method == 'POST':

        if 'entregar_inventario' in request.form:
            fecha_actual =fecha_actualCO()
            id_inventario = request.form['inventario_id']
            tipo_movimiento = 'Entrada'
            cantidad = request.form['cantidad_elemento']
            observaciones = request.form['observaciones']
            tipo_notificacion = 'Inventario'
            mensaje = 'Ha entregado exitosamente su elemento prestado de Inventario'
            query = "UPDATE movimientos SET tipo_movimiento = %s, cantidad = %s, fecha_movimiento = %s, observaciones = %s WHERE id_movimiento = %s"
            params = [tipo_movimiento, cantidad,
                      fecha_actual, observaciones, id_inventario]
            cursor.execute(
                "SELECT responsable FROM movimientos  WHERE id_movimiento = %s;", id_inventario)
            usuariosRH = cursor.fetchall()
            cursor.execute(query, params)
            conexion.commit()

            for usuariosRH in usuariosRH:
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, usuariosRH[0],
                          id_inventario, session['usuario'], mensaje, fecha_actual]
                cursor.execute(query, params)
                conexion.commit()
            flash('El elemento ha sido entregada.', 'correcto')

            return redirect('/verInventario')
        else:
            print('no agrego ')
    else:
        print('No es POST')
    conexion.close()
    return render_template('inventario/templates/listaEntregarInventario.html', materiales_prestados=materiales_prestados)


@app.route('/crearInventario',  methods=['GET', 'POST'])
def crearInventario():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    basepath = os.path.dirname(__file__)

    if 'agregar_elemento' in request.form:
        imagen_elemento = request.files['imagen_elemento']
        nombre_elemento = request.form['nombre_elemento']
        categoria_elemento = request.form['categoria']
        cantidad = request.form['cantidad_elemento']
        tipo_elemento = request.form['tipo_elemento']
        ubicacion = request.form['ubicacion_elemento']
        descripcion = request.form['descripcion_elemento']

        filename, file_extension = os.path.splitext(imagen_elemento.filename)
        if file_extension.lower() not in extensionesImagenes:
            flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.', 'error')
            return redirect(request.url)
        else:
            flash('Se ha agregado satisfactoriamente', 'correcto')

        filename = secure_filename(imagen_elemento.filename)
        extension = os.path.splitext(filename)[1]
        nuevoNombreElemento = stringAleatorio() + extension
        upload_path = os.path.join(
            basepath, app.root_path, 'static', 'images', 'inventario', nuevoNombreElemento)
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        imagen_elemento.save(upload_path)

        query = "INSERT INTO inventario (id_elemento, nombre_elemento, descripcion, cantidad, ubicacion,tipo_elemento,imagen,categoria) VALUES (%s,%s,%s,%s, %s,%s,%s,%s)"
        params = [generarID(), nombre_elemento, descripcion,  cantidad,
                  ubicacion, tipo_elemento, nuevoNombreElemento, categoria_elemento]

        cursor.execute(query, params)
        conexion.commit()

        return redirect('/verInventario')

    return render_template('inventario/templates/crearInventario.html')


@app.route('/inventario/listaInventario', methods=['GET', 'POST'])
def listaInventario():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM inventario")
    inventario = cursor.fetchall()
    if request.method == 'POST':
        inventario_id = request.form.get('inventario_id')
        if request.form.get('editar_inventario'):
            return redirect(f"/inventario/editarInventario/{inventario_id}")
        if request.form.get('borrar_inventario'):
            cursor.execute(
                "SELECT imagen FROM inventario WHERE id_elemento=%s", inventario_id)
            imagen_inventario = cursor.fetchone()
            ruta_archivo = os.path.join(
                app.root_path, 'static', 'images', 'inventario', imagen_inventario[0])
            cursor.execute(
                "DELETE FROM inventario WHERE id_elemento = %s;", (inventario_id,))
            conexion.commit()
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            flash('EL elemento ha sido eliminado correctamente', 'correcto')
            return redirect('/verInventario')

    conexion.close()
    return render_template('inventario/templates/listaInventario.html', inventario=inventario)


@app.route('/inventario/editarInventario/<string:inventario_id>', methods=['GET', 'POST'])
def editInventario(inventario_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and  session['cargo'] != 0:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM inventario WHERE id_elemento= %s", inventario_id)
    inventario = cursor.fetchone()

    if request.method == 'POST':
        # Obtener los valores de los campos del formulario

        nombre_elemento = request.form.get('nombre_elemento') or inventario[1]
        categoria_elemento = request.form.get('categoria') or inventario[7]
        cantidad = request.form.get('cantidad_elemento') or inventario[3]
        tipo_elemento = request.form.get('tipo_elemento') or inventario[5]
        ubicacion = request.form.get('ubicacion_elemento') or inventario[4]
        descripcion = request.form.get('descripcion_elemento') or inventario[2]

        if request.files['imagen_elemento'].filename != '':
            imagen_elemento = request.files['imagen_elemento']
            filename, file_extension = os.path.splitext(
                imagen_elemento.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash(
                    'La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.', 'error')
            else:
                flash('La noticia se ha actualizado satisfactoriamente', 'correcto')
            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_elemento.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, app.root_path, 'static', 'images', 'inventario', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_elemento.save(upload_path)

        # Resto del código para procesar y guardar la imagen
        else:
            nuevoNombreImagen = inventario[6]

        query = "UPDATE inventario SET nombre_elemento = %s, categoria = %s, cantidad = %s, tipo_elemento = %s,ubicacion = %s,descripcion = %s, imagen=%s WHERE id_elemento = %s"
        params = [nombre_elemento, categoria_elemento, cantidad, tipo_elemento,
                  ubicacion, descripcion, nuevoNombreImagen, inventario_id]
        cursor.execute(query, params)
        conexion.commit()
        flash('Ha sido actualizado correctamiente.', 'success')
        return redirect('/verInventario')

    return render_template('inventario/templates/editarInventario.html', inventario=inventario)


@app.route('/inventario/asignarInventario', methods=['GET', 'POST'])
def asignarInventario():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT usuario, Nombre, segundo_nombre, Apellido, segundo_apellido FROM general_users")
    usuario = cursor.fetchall()
    cursor.execute("SELECT id_elemento, nombre_elemento FROM inventario")
    inventario = cursor.fetchall()
    if request.method == 'POST':
        if 'asignar_elemento' in request.form:
            elemento = request.form['elemento']
            usuario_elemento = request.form['usuario_elemento']
            cantidad_elemento = request.form['cantidad_elemento']
            descripcion_elemento = request.form['descripcion_elemento']
            fecha_actual =fecha_actualCO()
            query = "INSERT INTO elementos_entregados (id_entregados, empleado_id, elemento_id, cantidad, fecha_entrega, observaciones) VALUES (%s, %s,%s,%s, %s,%s)"
            params = [generarID(), usuario_elemento, elemento,
                      cantidad_elemento, fecha_actual, descripcion_elemento]
            cursor.execute(query, params)
            conexion.commit()
            flash('Elemento asignado correctamente', 'correcto')
            return redirect(request.url)
    conexion.close()
    return render_template('inventario/templates/asignarInventario.html', inventario=inventario, usuario=usuario)


@app.route('/inventario/solicitarElemento/<id_inventario>',  methods=['GET', 'POST'])
def solicitarInventario(id_inventario):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    responsable = session['usuario']
    feha_actual =fecha_actualCO()
    cursor.execute('SELECT usuario FROM general_users WHERE id_cargo_fk = 3')
    usuariosRH = cursor.fetchall()
    if request.method == 'POST':
        if 'solicitar_elemento' in request.form:
            tipo_movimiento = 'Salida'
            cantidad = request.form['cantidad_elemento']
            motivo = request.form['motivo_elemento']
            tipo_notificacion = 'Inventario'
            id_movimiento = generarID()
            mensaje = 'Ha solicitado una nueva petición de Inventario'

            query = "INSERT INTO movimientos (id_movimiento,id_elemento,tipo_movimiento, cantidad, responsable, fecha_solicitud, motivo) VALUES (%s,%s,%s,%s, %s,%s, %s)"
            params = [id_movimiento, id_inventario, tipo_movimiento,
                      cantidad,  responsable, feha_actual, motivo]
            cursor.execute(query, params)

            for usuariosRH in usuariosRH:
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, usuariosRH[0],
                          id_movimiento, responsable, mensaje, feha_actual]
                cursor.execute(query, params)
                conexion.commit()
            conexion.commit()
            flash('Solicitud realizada', 'correcto')
            return redirect('/verInventario')
        else:
            print('no agrego ')
    else:
        print('No es POST')
    return render_template('inventario/templates/solicitudInventario.html')


@app.route('/inventario/listaReportarInventario',  methods=['GET', 'POST'])
def listaReportarInventario():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM inventario')
    inventario = cursor.fetchall()
    if request.method == 'POST':
        if 'reportarElemento' in request.form:
            elemento_id = request.form['reportarElemento']
            return redirect(f'/inventario/reportarInventario/{elemento_id}')
        else:
            print('no agrego ')
    else:
        print('No es POST')
    return render_template('inventario/templates/listaReportarInventario.html', inventario=inventario)


@app.route('/inventario/reportarInventario/<id_inventario>',  methods=['GET', 'POST'])
def reportarInventario(id_inventario):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        'SELECT * FROM inventario WHERE id_elemento =%s', id_inventario)
    inventario = cursor.fetchone()
    feha_actual =fecha_actualCO()
    responsable = session['usuario']
    if request.method == 'POST':
        if 'reportarElemento' in request.form:
            if session['cargo'] == 3 or session['cargo'] == 1:
                cursor.execute(
                    'SELECT usuario FROM general_users WHERE id_cargo_fk = 1')
                usuariosRH = cursor.fetchall()
            else:
                cursor.execute(
                    'SELECT usuario FROM general_users WHERE id_cargo_fk = 3')
                usuariosRH = cursor.fetchall()
            descripcion = request.form['descripcion']
            tipo_notificacion = 'Reporte'
            id_reporte = generarID()
            mensaje = 'Ha reportado un elemento del Inventario'

            query = "INSERT INTO reportes_inventario (id_reporte,elemento_entregado,fecha_reporte, descripcion, reportado_por) VALUES (%s,%s,%s,%s,%s)"
            params = [id_reporte, id_inventario,
                      feha_actual, descripcion, responsable]
            cursor.execute(query, params)

            for usuariosRH in usuariosRH:
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, usuariosRH[0],
                          id_inventario, responsable, mensaje, feha_actual]
                cursor.execute(query, params)
                conexion.commit()
            conexion.commit()
            flash('Elemento reportado con exito', 'correcto')
            if session['cargo'] == 1:
                return redirect('/inventario/listaReportarInventario')
            else:
                return redirect('/verInventario')
        else:
            print('no agrego ')
            flash('Elemento no ha sido reportado con exito', 'error')

    else:
        print('No es POST')
    return render_template('inventario/templates/reportarElemento.html', inventario=inventario)
