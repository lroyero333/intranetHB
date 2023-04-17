
from random import sample
from flask import jsonify
from main.run import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime


def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud = 10
    secuencia = string_aleatorio.upper()
    resultado_aleatorio = sample(secuencia, longitud)
    string_aleatorio = "".join(resultado_aleatorio)
    return string_aleatorio


"""@app.route('/calendario', methods=['GET', 'POST'])
def calendario():
    if not 'login' in session:
        return redirect('/')

    conexion = mysql.connect()
    cursor = conexion.cursor()

    # Manejar la creación de cursos
    if request.method == 'POST' and 'crear_curso' in request.form:
        id_usuario_fk = session["usuario"]
        nombre_curso = request.form['nombre_curso']
        fecha_inicio_curso = request.form['fecha_inicio_curso']
        Fecha_fin_curso = request.form['fecha_fin_curso']
        ubicacion = request.form['ubicacion_curso']
        descripcion = request.form['descripcion']
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = "INSERT INTO cursos (id_usuario_fk,nombre_curso, fecha_inicio, fecha_fin, fecha_publicacion, ubicacion, descripcion) VALUES (%s,%s,%s, %s, %s, %s, %s)"
        params = [id_usuario_fk, nombre_curso, fecha_inicio_curso,
                  Fecha_fin_curso, fecha_publicacion, ubicacion, descripcion]

        cursor.execute(query, params)
        conexion.commit()

        return redirect('/calendario')

    # Manejar la creación de noticias
    if request.method == 'POST' and 'crear_noticia' in request.form:
       
        usuarioPublica= session["usuario"]
        titulo_noticia = request.form['titulo_noticia']
        imagen_noticia = request.files['imagen_noticia']
        descripcion_noticia = request.form['descripcion_noticia']
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        basepath = os.path.dirname(__file__)
        filename = secure_filename(imagen_noticia.filename)

        extension = os.path.splitext(filename)[1]
        nuevoNombreImagen = stringAleatorio() +extension

        upload_path = os.path.join(basepath, '..', '..', 'static', 'images','Noticias', nuevoNombreImagen)
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        imagen_noticia.save(upload_path)


        query = "INSERT INTO noticias (titulo_noticia, imagen_noticia, descripcion_noticia, fecha_publicacion,id_usuario_fk) VALUES (%s,%s, %s, %s,%s)"
        params = [titulo_noticia, nuevoNombreImagen,descripcion_noticia, fecha_publicacion,usuarioPublica]

        cursor.execute(query, params)
        conexion.commit()

        return redirect('/calendario')
    
    

    # Obtener la lista de cursos y de noticias
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()

    cursor.execute("SELECT * FROM noticias")
    noticias = cursor.fetchall()


    return render_template('templates/light/app-calendar.html', cursos=cursos, noticias=noticias)

@app.route('/calendario', methods=['GET', 'POST'])
def eliminarCurso():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cursos;")
    cursos = cursor.fetchall()
    conexion.close()
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        if request.form.get('editar_curso'):
            # Lógica para editar el curso
            flash('El curso ha sido editado.', 'success')
        elif request.form.get('borrar_curso'):
            conexion = mysql.connect()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM cursos WHERE id_curso = %s;", request.form.get('borrar_curso'))
            conexion.commit()
            conexion.close()
            flash('El curso ha sido eliminado.', 'success')
        return redirect('/calendario')
    return render_template('templates/light/app-calendar.html', cursos=cursos)
"""


@app.route('/calendario', methods=['GET', 'POST'])
def calendario():
    if not 'login' in session:
        return redirect('/')

    conexion = mysql.connect()
    cursor = conexion.cursor()

    # Manejar la creación de cursos y noticias
    if request.method == 'POST':
        if 'crear_curso' in request.form:
            id_usuario_fk = session["usuario"]
            nombre_curso = request.form['nombre_curso']
            fecha_inicio_curso = request.form['fecha_inicio_curso']
            Fecha_fin_curso = request.form['fecha_fin_curso']
            ubicacion = request.form['ubicacion_curso']
            descripcion = request.form['descripcion']
            fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO cursos (id_usuario_fk,nombre_curso, fecha_inicio, fecha_fin, fecha_publicacion, ubicacion, descripcion) VALUES (%s,%s,%s, %s, %s, %s, %s)"
            params = [id_usuario_fk, nombre_curso, fecha_inicio_curso,
                      Fecha_fin_curso, fecha_publicacion, ubicacion, descripcion]

            cursor.execute(query, params)
            conexion.commit()

            return redirect('/calendario')

        elif 'crear_noticia' in request.form:
            usuarioPublica = session["usuario"]
            titulo_noticia = request.form['titulo_noticia']
            imagen_noticia = request.files['imagen_noticia']
            descripcion_noticia = request.form['descripcion_noticia']
            fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_noticia.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, '..', '..', 'static', 'images', 'Noticias', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_noticia.save(upload_path)

            query = "INSERT INTO noticias (titulo_noticia, imagen_noticia, descripcion_noticia, fecha_publicacion,id_usuario_fk) VALUES (%s,%s, %s, %s,%s)"
            params = [titulo_noticia, nuevoNombreImagen,
                      descripcion_noticia, fecha_publicacion, usuarioPublica]

            cursor.execute(query, params)
            conexion.commit()

            return redirect('/calendario')

    # Manejar la edición de cursos
    if request.method == 'POST':
        curso_id = request.form.get('curso_id')
        if request.form.get('editar_curso'):
            return redirect(f"/calendario/curso/{curso_id}")
        if request.form.get('borrar_curso'):
            cursor.execute(
                "DELETE FROM cursos WHERE id_curso = %s;", (curso_id,))
            conexion.commit()
            flash('El curso ha sido eliminado.', 'success')
            return redirect('/calendario')
        
        noticia_id = request.form.get('noticia_id')
        if request.form.get('editar_noticia'):

            return redirect(f"/calendario/noticia/{noticia_id}")
        if request.form.get('borrar_noticia'):
            cursor.execute(
                "DELETE FROM cursos WHERE id_noticia = %s;", (noticia_id,))
            conexion.commit()
            flash('El curso ha sido eliminado.', 'success')
            return redirect('/calendario')

    # Obtener la lista de cursos y de noticias
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()

    cursor.execute("SELECT * FROM noticias")
    noticias = cursor.fetchall()

    conexion.close()

    return render_template('calendario/templates/app-calendar.html', cursos=cursos, noticias=noticias)

@app.route('/calendario/curso/<string:curso_id>', methods=['GET', 'POST'])
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
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = "UPDATE cursos SET id_usuario_fk = %s, nombre_curso = %s, fecha_inicio = %s, fecha_fin = %s, ubicacion = %s, descripcion = %s, fecha_publicacion = %s WHERE id_curso = %s"
        params = [id_usuario_fk, nombre_curso, fecha_inicio_curso,
                  fecha_fin_curso, ubicacion, descripcion, fecha_publicacion, curso_id]

        cursor.execute(query, params)
        conexion.commit()

        flash('El curso ha sido editado.', 'success')
        return redirect('/calendario')
    
    return render_template('calendario/templates/editarCurso.html', curso=curso)

@app.route('/calendario/noticia/<string:noticia_id>', methods=['GET', 'POST'])
def editNoticia(noticia_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM noticias WHERE id_noticia= %s", noticia_id)
    noticia = cursor.fetchone()
    
    if request.method == 'POST':
        # Obtener los valores de los campos del formulario

        usuarioPublica = session["usuario"]
        titulo_noticia = request.form.get('titulo_noticia') or noticia[1]
        
        descripcion_noticia = request.form.get('descripcion_noticia') or noticia[3]
        fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if request.files['imagen_noticia'].filename != '':
            imagen_noticia = request.files['imagen_noticia']
            basepath = os.path.dirname(__file__)
            filename = secure_filename(imagen_noticia.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreImagen = stringAleatorio() + extension

            upload_path = os.path.join( basepath, '..', '..', 'static', 'images', 'Noticias', nuevoNombreImagen)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            imagen_noticia.save(upload_path)

        # Resto del código para procesar y guardar la imagen
        else:
            nuevoNombreImagen = noticia[2]


        
        query = "UPDATE noticias SET id_usuario_fk = %s, titulo_noticia = %s, imagen_noticia = %s, descripcion_noticia = %s,fecha_publicacion = %s WHERE id_noticia = %s"
        params = [usuarioPublica, titulo_noticia, nuevoNombreImagen,descripcion_noticia, fecha_publicacion, noticia_id]

        cursor.execute(query, params)
        conexion.commit()

        flash('El curso ha sido editado.', 'success')
        return redirect('/calendario')
    
    return render_template('calendario/templates/editarNoticia.html', noticia=noticia)

@app.route('/cursos/<string:curso_id>', methods=['GET', 'POST'])
def verCursos(curso_id):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cursos WHERE id_curso= %s;", curso_id)
    datosCursos = cursor.fetchall()
    conexion.commit()

    # Buscar si el usuario actual está inscrito en el curso
    cursor.execute("SELECT * FROM inscripcion_cursos WHERE id_usuario_fk = %s AND id_curso_fk = %s",
                   (session['usuario'], curso_id))
    resultado = cursor.fetchone()

    if request.method == 'POST':
        if resultado is not None:
            # Eliminar al usuario de la tabla de inscripción de cursos
            cursor.execute("DELETE FROM inscripcion_cursos WHERE id_usuario_fk=%s AND id_curso_fk=%s", (session['usuario'], curso_id))
            conexion.commit()
            flash("Te has cancelado la inscripción en este curso.")
        else:
            # Insertar un nuevo usuario en la tabla de inscripción de cursos
            id_usuario_fk = session['usuario']
            id_curso_fk = curso_id
            fecha_inscripcion_curso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO inscripcion_cursos (id_usuario_fk, id_curso_fk, fecha_inscripcion_curso) VALUES (%s, %s, %s)"
            params = [id_usuario_fk, id_curso_fk, fecha_inscripcion_curso]

            cursor.execute(query, params)
            conexion.commit()

            flash("Te has inscrito exitosamente en este curso.")

        return redirect(f"/cursos/{curso_id}")

    return render_template('calendario/templates/verCurso.html', datosCursos=datosCursos, inscrito=(resultado is not None))

@app.route('/proyectos', methods=['GET', 'POST'])
def crearProyecto():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()

    if request.method == 'POST' and 'crear_proyecto' in request.form:

        nombre_proyecto = request.form['nombre_proyecto']
        imagen_proyecto = request.files['imagen_proyecto']
        descripcion_proyecto = request.form['descripcion_proyecto']

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
    
    if request.method == 'POST':
        proyecto_id = request.form.get('proyecto_id')
        if request.form.get('editar_proyecto'):
            return redirect(f"/proyectos/{proyecto_id}")
        if request.form.get('borrar_proyecto'):
            cursor.execute(
                "DELETE FROM proyectos WHERE id_proyecto = %s;", (proyecto_id,))
            conexion.commit()
            flash('El proyecto ha sido eliminado.', 'success')
            return redirect('/proyectos')
        
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM proyectos;")
    datosProyectos = cursor.fetchall()
    conexion.commit()
    conexion.close()
    return render_template('calendario/templates/projects.html', datosProyectos=datosProyectos)

@app.route('/proyectos/<string:proyecto_id>', methods=['GET', 'POST'])
def editProyecto(proyecto_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1:
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM proyectos WHERE id_proyecto= %s", proyecto_id)
    proyecto = cursor.fetchone()
    
    if request.method == 'POST':
        # Obtener los valores de los campos del formulario

        
        titulo_noticia = request.form.get('titulo_proyecto') or proyecto[1]
        
        descripcion_proyecto = request.form.get('descripcion_noticia') or proyecto[3]

        if request.files['imagen_proyecto'].filename != '':
            imagen_proyecto = request.files['imagen_proyecto']
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

        flash('El curso ha sido editado.', 'success')
        return redirect('/proyectos')
    
    return render_template('calendario/templates/editarProyecto.html', proyecto=proyecto)

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
            '%Y-%m-%d'), 'end': evento[4].strftime(
            '%Y-%m-%d'),  'location': evento[6], 'allDay': 'true', "className": 'bg-info'}
        eventos_json.append(evento_json)
    return jsonify(eventos_json)
