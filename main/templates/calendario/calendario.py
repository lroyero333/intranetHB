from flask import jsonify
from main.app import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify

from datetime import datetime


@app.route('/calendario', methods=['GET', 'POST'])
def calendario():
    if not 'login' in session:
        return redirect('/')

    conexion = mysql.connect()
    cursor = conexion.cursor()

    # Manejar la creación de cursos
    if request.method == 'POST' and 'crear_curso' in request.form:
        id_usuario = session["nombre"] + " " + session["apellido"]
        foto_usuario= session["foto"]
        nombre_curso = request.form['nombre_curso']
        fecha_inicio_curso = request.form['fecha_inicio_curso']
        Fecha_fin_curso = request.form['fecha_fin_curso']
        ubicacion = request.form['ubicacion_curso']
        descripcion = request.form['descripcion']
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = "INSERT INTO cursos (nombre_usuario,foto_usuario,nombre_curso, fecha_inicio, fecha_fin, fecha_publicacion, ubicacion, descripcion) VALUES (%s,%s,%s, %s, %s, %s, %s, %s)"
        params = [id_usuario,foto_usuario, nombre_curso, fecha_inicio_curso,
                  Fecha_fin_curso, fecha_publicacion, ubicacion, descripcion]

        cursor.execute(query, params)
        conexion.commit()

        return redirect('/calendario')

    # Manejar la creación de noticias
    if request.method == 'POST' and 'crear_noticia' in request.form:
        nombre_usuario = session["nombre"] + " " + session["apellido"]
        foto_usuario= session["foto"]
        titulo_noticia = request.form['titulo_noticia']
        imagen_noticia = request.form['imagen_noticia']
        descripcion_noticia = request.form['descripcion_noticia']
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = "INSERT INTO noticias (nombre_usuario,titulo_noticia, imagen_noticia, descripcion_noticia, fecha_publicacion,foto_usuario) VALUES (%s,%s, %s, %s, %s,%s)"
        params = [nombre_usuario ,titulo_noticia, imagen_noticia,
                  descripcion_noticia, fecha_publicacion, foto_usuario]

        cursor.execute(query, params)
        conexion.commit()

        return redirect('/calendario')

    # Obtener la lista de cursos y de noticias
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()

    cursor.execute("SELECT * FROM noticias")
    noticias = cursor.fetchall()

    return render_template('templates/light/app-calendar.html', cursos=cursos, noticias=noticias)


@app.route('/cursos')
def obtener_cursos():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        'SELECT * FROM cursos')
    eventos = cursor.fetchall()
    eventos_json = []
    for evento in eventos:
        evento_json = {'title': evento[2], 'start': evento[3].strftime(
            '%Y-%m-%d'),  'location': evento[6], 'allDay': 'true', "className": 'bg-info'}
        eventos_json.append(evento_json)
    return jsonify(eventos_json)



