import datetime
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

@app.route('/verInventario',  methods=['GET','POST'])
def verInventario():
    if not 'login' in session:
        return redirect('/')
    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM herramientas;")
    herramientas = cursor.fetchall()
    cursor.execute("SELECT * FROM materiales;")
    materiales = cursor.fetchall()
    if request.method == 'POST':
        if 'agregar_tool' in request.form:
            imagen_herramienta=request.files['imagen_tool']
            nombre_herramienta = request.form['nombre_herramienta']
            cantidad = request.form['cantidad_tool']
            ubicacion = request.form['ubicacion_tool']
            descripcion = request.form['descripcion_tool']

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

            flash('La herramienta ha sido eliminada.', 'success')
            
            return redirect('/verInventario')
        if 'agregar_material' in request.form:
            imagen_material=request.files['imagen_material']
            nombre_material = request.form['nombre_material']
            cantidad = request.form['cantidad_material']
            ubicacion = request.form['ubicacion_material']
            descripcion = request.form['descripcion_material']
            tipo_material=request.form['tipo_material']

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

            flash('El material ha sido eliminado.', 'success')
            
            return redirect('/verInventario')
        else:
            print('no agrego ')
    else:
         print('No es POST')
    return render_template('inventario/templates/verInventario.html', herramientas=herramientas, materiales=materiales)


