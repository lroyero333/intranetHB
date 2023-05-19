import datetime as dt
from datetime import datetime, time, timedelta 
import os
from random import sample
from flask import send_file
from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for
import json
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for
from main.run import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename

def stringAleatorio():
    string_aleatorio="0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud=10
    secuencia=string_aleatorio.upper()
    resultado_aleatorio= sample(secuencia, longitud)
    string_aleatorio= "".join(resultado_aleatorio)
    return string_aleatorio

extensionesImagenes=['.jpg', '.jpeg', '.png']
@app.route('/verInventario',  methods=['GET','POST'])
def verInventario():
    if not 'login' in session:
        return redirect('/')
    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM herramientas;")
    herramientas = cursor.fetchall()
    cursor.execute("SELECT movimientos_herramientas.*, general_users.Nombre, general_users.Apellido, general_users.foto , herramientas.* FROM movimientos_herramientas LEFT JOIN general_users ON movimientos_herramientas.responsable = general_users.usuario LEFT JOIN herramientas ON movimientos_herramientas.id_herramienta=herramientas.id_herramientas WHERE tipo_movimiento='Salida' and estado_solicitud='Aceptado' ORDER BY fecha_solicitud DESC;")
    herramientas_prestadas = cursor.fetchall()
    cursor.execute("SELECT * FROM materiales;")
    materiales = cursor.fetchall()
    cursor.execute("SELECT movimientos_materiales.*, general_users.Nombre, general_users.Apellido, general_users.foto , materiales.* FROM movimientos_materiales LEFT JOIN general_users ON movimientos_materiales.responsable = general_users.usuario LEFT JOIN materiales ON movimientos_materiales.id_material=materiales.id_material WHERE tipo_movimiento='Salida' and estado_solicitud='Aceptado' ORDER BY fecha_solicitud DESC;")
    materiales_prestados = cursor.fetchall()
    fecha_actual=datetime.now()
    if request.method == 'POST':
        if 'agregar_tool' in request.form:
            imagen_herramienta=request.files['imagen_tool']
            nombre_herramienta = request.form['nombre_herramienta']
            cantidad = request.form['cantidad_tool']
            ubicacion = request.form['ubicacion_tool']
            descripcion = request.form['descripcion_tool']

            filename, file_extension = os.path.splitext(imagen_herramienta.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
                return redirect(request.url)
            else:
                flash('Se ha agregado satisfactoriamente','correcto')
            
            filename = secure_filename(imagen_herramienta.filename)
            extension = os.path.splitext(filename)[1]
            nuevoNombreTool = stringAleatorio() + extension
            upload_path = os.path.join(basepath, app.root_path, 'static', 'images', 'inventario','herramientas', nuevoNombreTool)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_herramienta.save(upload_path)

            query = "INSERT INTO herramientas (nombre_herramientas, cantidad, ubicacion, descripcion,imagen_herramienta) VALUES (%s,%s,%s, %s,%s)"
            params = [nombre_herramienta, cantidad,  ubicacion,  descripcion, nuevoNombreTool]

            cursor.execute(query, params)
            conexion.commit()

            return redirect('/verInventario')
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
        if 'agregar_material' in request.form:
            imagen_material=request.files['imagen_material']
            nombre_material = request.form['nombre_material']
            cantidad = request.form['cantidad_material']
            ubicacion = request.form['ubicacion_material']
            descripcion = request.form['descripcion_material']
            tipo_material=request.form['tipo_material']

            filename, file_extension = os.path.splitext(imagen_material.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
                return redirect(request.url)
            else:
                flash('Se ha agregado satisfactoriamente','correcto')
            filename = secure_filename(imagen_material.filename)
            extension = os.path.splitext(filename)[1]
            nuevoNombreMaterial = stringAleatorio() + extension
            upload_path = os.path.join(basepath, app.root_path, 'static', 'images', 'inventario','materiales', nuevoNombreMaterial)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_material.save(upload_path)

            query = "INSERT INTO materiales (nombre_material, cantidad, ubicacion, consumible, descripcion, imagen_material) VALUES (%s,%s,%s, %s,%s, %s)"
            params = [nombre_material, cantidad,  ubicacion, tipo_material,  descripcion, nuevoNombreMaterial]

            cursor.execute(query, params)
            conexion.commit()

            return redirect('/verInventario')
        if 'eliminar_material' in request.form:
            
            imagen_material = request.form['imagen_material']
            print('material',imagen_material)
            ruta_archivo = os.path.join(app.root_path, 'static', 'images', 'inventario','materiales', imagen_material)

            cursor.execute("DELETE FROM materiales WHERE imagen_material=%s;", imagen_material)
            conexion.commit()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            flash('El material ha sido eliminado.', 'correcto')
            
            return redirect('/verInventario')
        if 'entregar_tool' in request.form:
            id_inventario=request.form['herramienta_prestada']
            tipo_movimiento='Entrada'
            cantidad = request.form['cantidad_herramienta']
            observaciones = request.form['observaciones_tool']
            query = "UPDATE movimientos_herramientas SET tipo_movimiento = %s, cantidad = %s, fecha_movimiento = %s, observaciones = %s WHERE id_movimiento = %s"
            params = [tipo_movimiento, cantidad,  fecha_actual, observaciones, id_inventario]

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
    return render_template('inventario/templates/verInventario.html', herramientas=herramientas, materiales=materiales,herramientas_prestadas=herramientas_prestadas,materiales_prestados=materiales_prestados)

@app.route('/inventario/<tipo_solicitud>/<id_inventario>',  methods=['GET','POST'])
def solicitarInventario(tipo_solicitud, id_inventario):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    responsable = session['usuario']
    feha_actual=datetime.now()
    if request.method == 'POST':
        if 'solicitar_tool' in request.form:
            tipo_movimiento='Salida'
            cantidad = request.form['cantidad_tool']
            motivo = request.form['motivo_tool']
            query = "INSERT INTO movimientos_herramientas (id_herramienta,tipo_movimiento, cantidad, fecha_movimiento, responsable, fecha_solicitud, motivo) VALUES (%s, %s,%s,%s, %s,%s, %s)"
            params = [id_inventario, tipo_movimiento, cantidad,  feha_actual,  responsable, feha_actual, motivo]

            cursor.execute(query, params)
            conexion.commit()

            flash('Solicitud realizada','correcto')

            return redirect('/verInventario')
        if 'eliminar_tool' in request.form:
            return redirect('/verInventario')
        if 'solicitar_material' in request.form:
            tipo_movimiento='Salida'
            cantidad = request.form['cantidad_material']
            motivo = request.form['motivo_material']
            query = "INSERT INTO movimientos_materiales (id_material,tipo_movimiento, cantidad, responsable, fecha_solicitud, motivo) VALUES (%s, %s,%s,%s, %s,%s)"
            params = [id_inventario, tipo_movimiento, cantidad,  responsable, feha_actual, motivo]
            cursor.execute(query, params)
            conexion.commit()
            flash('Solicitud realizada','correcto')
            return redirect('/verInventario')
        else:
            print('no agrego ')
    else:
         print('No es POST')
    return render_template('inventario/templates/solicitudInventario.html',  tipo_solicitud=tipo_solicitud)