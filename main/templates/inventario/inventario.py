import datetime as dt
import json
import os
from datetime import datetime, time, timedelta
from random import sample

from flask import send_file
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (app, bcrypt, flash, jsonify, mysql, redirect,
                      render_template, request, session, stringAleatorio,
                      url_for)

extensionesImagenes=['.jpg', '.jpeg', '.png']
conexion = mysql.connect()
cursor = conexion.cursor()
@app.route('/verInventario',  methods=['GET','POST'])
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

    cursor.execute("SELECT movimientos_materiales.*, general_users.Nombre, general_users.Apellido, general_users.foto , materiales.* FROM movimientos_materiales LEFT JOIN general_users ON movimientos_materiales.responsable = general_users.usuario LEFT JOIN materiales ON movimientos_materiales.id_material=materiales.id_material WHERE tipo_movimiento='Salida' and estado_solicitud='Aceptado' ORDER BY fecha_solicitud DESC;")
    materiales_prestados = cursor.fetchall()
    fecha_actual=datetime.now()
    if request.method == 'POST':
        
        if 'eliminar_tool' in request.form:
            
            imagen_tool = request.form['imagen_herramienta']
            print('herramienta',imagen_tool)
            ruta_archivo = os.path.join(app.root_path, 'static', 'images', 'inventario','herramientas', imagen_tool)

            cursor.execute("DELETE FROM herramientas WHERE imagen_herramienta=%s;", imagen_tool)
            conexion.commit()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            flash('La herramienta ha sido eliminada.', 'correcto')
            
            return redirect('/verInventario')
                
        if 'entregar_tool' in request.form:
            id_inventario=request.form['herramienta_prestada']
            tipo_movimiento='Entrada'
            cantidad = request.form['cantidad_herramienta']
            observaciones = request.form['observaciones_tool']
            query = "UPDATE movimientos_herramientas SET tipo_movimiento = %s, cantidad = %s, fecha_movimiento = %s, observaciones = %s WHERE id_movimiento = %s"
            params = [tipo_movimiento, cantidad,  fecha_actual, observaciones, id_inventario]

            query = "INSERT INTO notificaciones_respuesta (tipo_notificacion, destinatario, remitente, fecha_notificacion) VALUES (%s,%s,%s, %s)"
            params = [nombre_herramienta, cantidad,  ubicacion,  descripcion, nuevoNombreTool]

            cursor.execute(query, params)
            conexion.commit()

            flash('La herramienta ha sido entregada.', 'correcto')

            return redirect('/verInventario')
        if 'entregar_material' in request.form:
            id_inventario=request.form['material_prestado']
            tipo_movimiento='Entrada'
            cantidad = request.form['cantidad_material']
            observaciones = request.form['observaciones_material']
            query = "UPDATE movimientos_materiales SET tipo_movimiento = %s, cantidad = %s, fecha_movimiento = %s, observaciones = %s WHERE id_movimiento = %s"
            params = [tipo_movimiento, cantidad,  fecha_actual, observaciones, id_inventario]

            cursor.execute(query, params)
            conexion.commit()

            flash('El material ha sido entregado.', 'correcto')

            return redirect('/verInventario')
        else:
            print('no agrego ')
    else:
         print('No es POST')
    return render_template('inventario/templates/verInventario.html', inventario_cargo=inventario_cargo, inventario=inventario, prestados=prestados)

@app.route('/crearInventario',  methods=['GET','POST'])
def crearInventario():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    basepath = os.path.dirname(__file__)
    
    if 'agregar_elemento' in request.form:
        imagen_elemento=request.files['imagen_elemento']
        nombre_elemento = request.form['nombre_elemento']
        categoria_elemento=request.form['categoria']
        cantidad = request.form['cantidad_elemento']
        tipo_elemento=request.form['tipo_elemento']
        ubicacion = request.form['ubicacion_elemento']
        descripcion = request.form['descripcion_elemento']

        filename, file_extension = os.path.splitext(imagen_elemento.filename)
        if file_extension.lower() not in extensionesImagenes:
            flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
            return redirect(request.url)
        else:
            flash('Se ha agregado satisfactoriamente','correcto')
            
        filename = secure_filename(imagen_elemento.filename)
        extension = os.path.splitext(filename)[1]
        nuevoNombreElemento = stringAleatorio() + extension
        upload_path = os.path.join(basepath, app.root_path, 'static', 'images', 'inventario', nuevoNombreElemento)
        if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

        imagen_elemento.save(upload_path)

        query = "INSERT INTO inventario (nombre_elemento, descripcion, cantidad, ubicacion,tipo_elemento,imagen,categoria) VALUES (%s,%s,%s, %s,%s,%s,%s)"
        params = [nombre_elemento, descripcion,  cantidad,  ubicacion, tipo_elemento,nuevoNombreElemento,categoria_elemento]

        cursor.execute(query, params)
        conexion.commit()

        return redirect('/verInventario')
    
    return render_template('inventario/templates/crearInventario.html')

@app.route('/inventario/listaInventario', methods=['GET', 'POST'])
def listaInventario():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':  
        inventario_id = request.form.get('inventario_id')
        if request.form.get('editar_inventario'):
            return redirect(f"/inventario/editarInventario/{inventario_id}")
        if request.form.get('borrar_inventario'):
            cursor.execute(
                "DELETE FROM inventario WHERE id_elemento = %s;", (inventario_id,))
            conexion.commit()
            flash('La inventario ha sido eliminada correctamente','correcto')
            return redirect('/verInventario')
    cursor.execute("SELECT * FROM inventario")
    inventario = cursor.fetchall()
    conexion.close()
    return render_template('inventario/templates/listaInventario.html',inventario=inventario)

@app.route('/inventario/editarInventario/<string:inventario_id>', methods=['GET', 'POST'])
def editInventario(inventario_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1:
        return redirect('/inicio')
    cursor.execute("SELECT * FROM inventario WHERE id_elemento= %s", inventario_id)
    inventario = cursor.fetchone()
    
    if request.method == 'POST':
        # Obtener los valores de los campos del formulario

        nombre_elemento = request.form.get('nombre_elemento') or inventario[1]
        categoria_elemento=request.form.get('categoria') or inventario[7]
        cantidad = request.form.get('cantidad_elemento') or inventario[3]
        tipo_elemento=request.form.get('tipo_elemento') or inventario[5]
        ubicacion = request.form.get('ubicacion_elemento' )or inventario[4]
        descripcion = request.form.get('descripcion_elemento') or inventario[2]

        if request.files['imagen_elemento'].filename != '':
            imagen_elemento = request.files['imagen_elemento']
            filename, file_extension = os.path.splitext(imagen_elemento.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
            else:
                flash('La noticia se ha actualizado satisfactoriamente','correcto')
            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_elemento.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension

            upload_path = os.path.join( basepath, app.root_path, 'static', 'images', 'inventario', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_elemento.save(upload_path)

        # Resto del código para procesar y guardar la imagen
        else:
            nuevoNombreImagen = inventario[6]

        query = "UPDATE inventario SET nombre_elemento = %s, categoria = %s, cantidad = %s, tipo_elemento = %s,ubicacion = %s,descripcion = %s, imagen=%s WHERE id_elemento = %s"
        params = [nombre_elemento, categoria_elemento, cantidad,tipo_elemento, ubicacion, descripcion,nuevoNombreImagen,inventario_id]
        cursor.execute(query, params)
        conexion.commit()
        flash('Ha sido actualizado correctamiente.', 'success')
        return redirect('/verInventario')
    
    return render_template('inventario/templates/editarInventario.html', inventario=inventario)

@app.route('/inventario/asignarInventario', methods=['GET', 'POST'])
def asignarInventario():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT usuario, Nombre, segundo_nombre, Apellido, segundo_apellido FROM general_users")
    usuario = cursor.fetchall()
    cursor.execute("SELECT id_elemento, nombre_elemento FROM inventario")
    inventario = cursor.fetchall()
    if request.method == 'POST':  
        if 'asignar_elemento' in request.form:
            elemento=request.form['elemento']
            usuario_elemento=request.form['usuario_elemento']
            cantidad_elemento=request.form['cantidad_elemento']
            descripcion_elemento=request.form['descripcion_elemento']
            fecha_actual=datetime.now()
            query = "INSERT INTO elementos_entregados (empleado_id, elemento_id, cantidad, fecha_entrega, observaciones) VALUES (%s,%s,%s, %s,%s)"
            params = [usuario_elemento, elemento,  cantidad_elemento, fecha_actual, descripcion_elemento]
            cursor.execute(query, params)
            conexion.commit()
            flash('Elemento asignado correctamente','correcto')
            return redirect(request.url)
    conexion.close()
    return render_template('inventario/templates/asignarInventario.html',inventario=inventario, usuario=usuario)


@app.route('/inventario/solicitarElemento/<id_inventario>',  methods=['GET','POST'])
def solicitarInventario(id_inventario):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    responsable = session['usuario']
    feha_actual=datetime.now()
    if request.method == 'POST':
        if 'solicitar_elemento' in request.form:
            tipo_movimiento='Salida'
            cantidad = request.form['cantidad_elemento']
            motivo = request.form['motivo_elemento']
            query = "INSERT INTO movimientos (id_elemento,tipo_movimiento, cantidad, responsable, fecha_solicitud, motivo) VALUES (%s,%s,%s, %s,%s, %s)"
            params = [id_inventario, tipo_movimiento, cantidad,  responsable, feha_actual, motivo]
            cursor.execute(query, params)
            conexion.commit()
            flash('Solicitud realizada','correcto')
            return redirect('/verInventario')
        else:
            print('no agrego ')
    else:
         print('No es POST')
    return render_template('inventario/templates/solicitudInventario.html')