
import datetime as dt
import os
from datetime import datetime, time, timedelta
from random import sample

import pymysql
from flask import jsonify
from pymysql import IntegrityError
from werkzeug.utils import secure_filename

from main.run import (app, bcrypt, flash, jsonify, mysql, redirect,
                      render_template, request, session, url_for)

extensionesImagenes=['.jpg', '.jpeg', '.png']


def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud = 10
    secuencia = string_aleatorio.upper()
    resultado_aleatorio = sample(secuencia, longitud)
    string_aleatorio = "".join(resultado_aleatorio)
    return string_aleatorio



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
            flash('Curso agregado satisfactoriamente','correcto')

            return redirect('/calendario')

        elif 'crear_noticia' in request.form:
            usuarioPublica = session["usuario"]
            titulo_noticia = request.form['titulo_noticia']
            imagen_noticia = request.files['imagen_noticia']
            descripcion_noticia = request.form['descripcion_noticia']
            fecha_publicacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

          
            filename, file_extension = os.path.splitext(imagen_noticia.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
                return redirect('/calendario')
            else:
                flash('La noticia se ha agregado satisfactoriamente','correcto')

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
            flash('El curso ha sido eliminado.', 'correcto')
            return redirect('/calendario')
        
        noticia_id = request.form.get('noticia_id')
        if request.form.get('editar_noticia'):

            return redirect(f"/calendario/noticia/{noticia_id}")
        if request.form.get('borrar_noticia'):
            cursor.execute(
                "DELETE FROM noticias WHERE id_noticia = %s;", (noticia_id,))
            conexion.commit()
            flash('La noticia ha sido eliminada correctamente','correcto')
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

        flash('El curso ha sido editado correctamente.', 'correcto')
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
            filename, file_extension = os.path.splitext(imagen_noticia.filename)
            if file_extension.lower() not in extensionesImagenes:
                flash('La extensión de la imagen no está permitida. Solo se permiten archivos JPG, JPEG y PNG.','error')
            else:
                flash('La noticia se ha actualizado satisfactoriamente','correcto')
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
    curso_id = int(curso_id)

    query = "SELECT *, DATE_FORMAT(fecha_inicio, '%d %M %Y') AS fecha_inicio1, DATE_FORMAT(fecha_fin, '%d %M %Y') AS fecha_fin2 FROM cursos WHERE id_curso = {};".format(curso_id)
    cursor.execute(query)
    datosCursos = cursor.fetchone()
    query ="SELECT inscripcion_cursos.*, DATE_FORMAT(fecha_inscripcion_curso, '%d-%m-%Y') AS fecha_inscripcion, DATE_FORMAT(fecha_inscripcion_curso, '%H:%i %p') AS hora_inscripcion, general_users.Nombre, general_users.segundo_nombre, general_users.Apellido, general_users.segundo_apellido, general_users.foto, general_users.usuario FROM inscripcion_cursos LEFT JOIN general_users ON inscripcion_cursos.id_usuario_fk = general_users.usuario WHERE id_curso_fk= {};".format(curso_id)
    cursor.execute(query)
    datosCursosInscritos = cursor.fetchall()
    conexion.commit()

    # Buscar si el usuario actual está inscrito en el curso
    cursor.execute("SELECT * FROM inscripcion_cursos WHERE id_usuario_fk = %s AND id_curso_fk = %s", (session['usuario'], curso_id))
    resultado = cursor.fetchone()

    if request.method == 'POST':
        if resultado is not None:
            # Eliminar al usuario de la tabla de inscripción de cursos
            cursor.execute("DELETE FROM inscripcion_cursos WHERE id_usuario_fk=%s AND id_curso_fk=%s", (session['usuario'], curso_id))
            conexion.commit()
            flash("Has cancelado la inscripción en este curso.", 'correcto')
        else:
            # Insertar un nuevo usuario en la tabla de inscripción de cursos
            id_usuario_fk = session['usuario']
            id_curso_fk = curso_id
            fecha_inscripcion_curso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO inscripcion_cursos (id_usuario_fk, id_curso_fk, fecha_inscripcion_curso) VALUES (%s, %s, %s)"
            params = [id_usuario_fk, id_curso_fk, fecha_inscripcion_curso]

            cursor.execute(query, params)
            conexion.commit()

            flash("Te has inscrito exitosamente en este curso.", 'correcto')

        return redirect(f"/cursos/{curso_id}")

    return render_template('calendario/templates/verCurso.html', datosCursos=datosCursos, inscrito=(resultado is not None),datosCursosInscritos=datosCursosInscritos)


@app.route('/noticia/<string:noticia_id>', methods=['GET', 'POST'])
def verNoticia(noticia_id):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM noticias WHERE id_noticia= %s;", noticia_id)
    datosNoticias = cursor.fetchone()
    conexion.commit()

    return render_template('calendario/templates/verNoticia.html', datosNoticias=datosNoticias)

@app.route('/proyectos/usuarios/<string:project_id>', methods=['GET', 'POST'])
def userProyecto(project_id):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
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
                return render_template('calendario/templates/usersProjects.html', integrante=integrante, project_user=project_user,proyecto_nombre=proyecto_nombre)
            else:
                query = "INSERT INTO proyecto_users (id_proyecto, id_usuario, fecha_inicio_user,observaciones) VALUES (%s, %s, %s,%s)"
                params = [project_id, id_usuario, fecha_user, observaciones_user_proyecto]
                cursor.execute(query, params)
                conexion.commit()
                flash('Usuario agregado satisfactoriamente','correcto')
    cursor.close()
    return render_template('calendario/templates/usersProjects.html', integrante=integrante, project_user=project_user,proyecto_nombre=proyecto_nombre) 

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
    return render_template('calendario/templates/projects.html', datosProyectos=datosProyectos)

@app.route('/proyectos/lista/editar', methods=['GET', 'POST'])
def verProyectoEditar():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        proyecto_id = request.form.get('proyecto_id')
        if request.form.get('editar_proyecto'):
            return redirect(f"/proyectos/{proyecto_id}")
    cursor.execute(
        "SELECT * FROM proyectos;")
    datosProyectos = cursor.fetchall()
    conexion.commit()
    conexion.close()
    return render_template('calendario/templates/listaEditarProyecto.html', datosProyectos=datosProyectos)

@app.route('/proyectos/lista/eliminar', methods=['GET', 'POST'])
def verProyectoEliminar():
    if not 'login' in session:
        return redirect('/')
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
    return render_template('calendario/templates/listaEliminarProyecto.html', datosProyectos=datosProyectos)


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
    
    return render_template('calendario/templates/crearProyectos.html')

@app.route('/proyectos/<string:proyecto_id>', methods=['GET', 'POST'])
def editProyecto(proyecto_id):

    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 4:
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
    
    return render_template('calendario/templates/editarProyecto.html', proyecto=proyecto)

@app.route('/vacaciones', methods=['GET', 'POST'])
def verVacaciones():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT usuario, Nombre, Apellido,foto FROM general_users;")
    usuarios_vacaciones=cursor.fetchall()
    cursor.execute("SELECT vacaciones.*,DATE_FORMAT(fecha_inicio_vacaciones, '%d-%m-%Y') AS inicio_vacaciones,DATE_FORMAT(fecha_fin_vacaciones, '%d-%m-%Y') AS fin_vacaciones, general_users.Nombre, general_users.Apellido, general_users.foto FROM vacaciones LEFT JOIN general_users ON vacaciones.id_usuario = general_users.usuario ;")
    solicitudes_vacaciones = cursor.fetchall()
    
    cursor.execute("SELECT vacaciones_extemporaneas.*,DATE_FORMAT(fecha_inicio, '%d-%m-%Y') AS inicio_adelanto, DATE_FORMAT(fecha_fin, '%d-%m-%Y') AS fin_adelanto, general_users.Nombre, general_users.Apellido FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.id_usuario = general_users.usuario;")
    solicitudes_va_extemporaneas = cursor.fetchall()
    conexion.commit()
    

    if 'asignar_vacaciones' in request.form:
        id_usuario=request.form['usuario_id']
        tipo_vacaciones=request.form['tipo_vacaciones']
        fecha_inicio_vacaciones=request.form['fecha_inicio_vacaciones']
        fecha_fin_vacaciones=request.form['fecha_fin_vacaciones']
        # Verificar si el usuario ya existe
        resultado = None
        sql = "SELECT id_usuario FROM vacaciones WHERE id_usuario = %s "
        conexion = mysql.connect()
        cursor = conexion.cursor()
        cursor.execute(sql, id_usuario)
        resultado = cursor.fetchone()
        if resultado is not None:
            # El usuario ya existe
            
            cursor.close()
            flash('El usuario ya tiene vacaciones asignadas','error')
            return render_template('calendario/templates/vacaciones.html', usuarios_vacaciones=usuarios_vacaciones,solicitudes_vacaciones=solicitudes_vacaciones)
        else:
            query = "INSERT INTO vacaciones (tipo_vacaciones, fecha_inicio_vacaciones, fecha_fin_vacaciones, id_usuario ) VALUES (%s,%s, %s,%s)"
            params = [tipo_vacaciones, fecha_inicio_vacaciones,fecha_fin_vacaciones, id_usuario]
            cursor.execute(query, params)
            conexion.commit()
            flash('Vacaciones asignadas satisfactoriamente','correcto')

    if 'programar_vacaciones' in request.form:
        id_usuario=session['usuario']
        fecha_inicio_extemporanea=request.form['fecha_inicio_extemporanea']
        fecha_fin_extemporanea=request.form['fecha_fin_extemporanea']
        fecha_solicitud=datetime.now()
        estado_solicitud='Pendiente'
        
        query = "INSERT INTO vacaciones_extemporaneas (fecha_inicio, fecha_fin, fecha_solicitud, estado_solicitud, id_usuario ) VALUES (%s,%s, %s,%s, %s)"
        params = [fecha_inicio_extemporanea, fecha_fin_extemporanea,fecha_solicitud,estado_solicitud, id_usuario]
        cursor.execute(query, params)
        conexion.commit()
        flash('Vacaciones programadas satisfactoriamente','correcto')
        
    if 'cancelar_programar_vacaciones' in request.form:
        id_vacaciones_ex=request.form['vacaciones_ex_id']
        cursor.execute("DELETE FROM vacaciones_extemporaneas WHERE id_vacaciones_extemporaneas = %s;", (id_vacaciones_ex,))
        conexion.commit()
        flash('Vacaciones canceladas satisfactoriamente','correcto')
        return redirect('/vacaciones')


    cursor.execute("SELECT vacaciones_extemporaneas.*, DATE_FORMAT(fecha_inicio, '%d-%m-%Y')as inicio_adelanto,DATE_FORMAT(fecha_fin, '%d-%m-%Y') as fin_adelanto, general_users.Nombre, general_users.Apellido FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.persona_aprueba = general_users.usuario;")
    solicitudes_vacaciones_extemporaneas = cursor.fetchall()
    
    conexion.commit()

    return render_template('calendario/templates/vacaciones.html',usuarios_vacaciones=usuarios_vacaciones,solicitudes_vacaciones=solicitudes_vacaciones,solicitudes_vacaciones_extemporaneas=solicitudes_vacaciones_extemporaneas,solicitudes_va_extemporaneas=solicitudes_va_extemporaneas)

@app.route('/permisos',methods=['GET', 'POST'])
def verPermisos():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT solicitud_permisos.*,  DATE_FORMAT(fecha_inicio_permiso, '%d-%m-%Y %H:%i %p') AS inicio_permiso, DATE_FORMAT(fecha_fin_permiso, '%d-%m-%Y %H:%i %p') AS fin_permiso, DATE_FORMAT(fecha_inicio_recuperacion, '%d-%m-%Y %H:%i %p') AS inicio_recuperacion, DATE_FORMAT(fecha_fin_recuperacion, '%d-%m-%Y %H:%i %p') AS fin_recuperacion, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.id_usuario = general_users.usuario;")
    solicitudes_permisos = cursor.fetchall()
    cursor.execute("SELECT solicitud_permisos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.persona_aprueba = general_users.usuario;")
    solicitudes_permisos2 = cursor.fetchall()
    conexion.commit()
    
    if 'agendar_permiso' in request.form:
        id_usuario=session['usuario']
        inicio_dia_permiso=request.form['inicio_dia_permiso'] #2023-03-28
        inicio_hora_permiso=request.form['inicio_hora_permiso']#10:00 am
        fin_dia_permiso=request.form['fin_dia_permiso']
        fin_hora_permiso=request.form['fin_hora_permiso']
        contar_sabados=request.form.get('contar_sabados')
        motivo_permiso=request.form['motivo_permiso']
        fecha_inicio_permiso = inicio_dia_permiso + ' ' + inicio_hora_permiso
        fecha_hora = dt.datetime.strptime(fecha_inicio_permiso, '%Y-%m-%d %I:%M %p')
        inicio_permiso = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_permiso = fin_dia_permiso + ' ' + fin_hora_permiso
        fecha_hora = dt.datetime.strptime(fecha_fin_permiso, '%Y-%m-%d %I:%M %p')
        fin_permiso = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fecha_solicitud=datetime.now()
        duracion_permiso=dt.datetime.strptime(fin_permiso, '%Y-%m-%d %H:%M:%S') - dt.datetime.strptime(inicio_permiso, '%Y-%m-%d %H:%M:%S')
        print(duracion_permiso)
        print(inicio_permiso)
        print(fin_permiso)
        print(contar_sabados)
        # Inicializar lista de fechas
        fechas = []
        # Definir fechas de inicio y fin
        fecha_inicio = dt.datetime.strptime(inicio_permiso, '%Y-%m-%d %H:%M:%S')
        fecha_fin = dt.datetime.strptime(fin_permiso, '%Y-%m-%d %H:%M:%S')

        # Definir horario de trabajo
        hora_inicio_manana = time(8, 0, 0)
        hora_fin_manana = time(12, 30, 0)
        hora_inicio_tarde = time(14, 0, 0)
        hora_fin_tarde = time(18, 0, 0)


        if contar_sabados:
            print('Está activo')
         
            hora_inicio_manana_sabado = time(8, 0, 0)
            hora_fin_manana_sabado = time(12, 30, 0)

            dias_trabajo = set(range(0, 5))

            fecha_actual = fecha_inicio 
            while fecha_actual <= fecha_fin:
                if (fecha_actual.weekday() in dias_trabajo and 
                    ((fecha_actual.time() > hora_inicio_manana and fecha_actual.time() <= hora_fin_manana) or 
                    (fecha_actual.time() > hora_inicio_tarde and fecha_actual.time() <= hora_fin_tarde))):
                    fechas.append(fecha_actual)
                elif (fecha_actual.weekday() == 5 and 
                    hora_inicio_manana_sabado < fecha_actual.time() <= hora_fin_manana_sabado):
                    fechas.append(fecha_actual)
                fecha_actual += dt.timedelta(minutes=30)
                # Omitir los domingos
                if fecha_actual.weekday() == 6:
                    fecha_actual += dt.timedelta(days=1)
        else:
            dias_trabajo = set(range(0, 5))
            # Iterar entre fechas cada media hora
            fecha_actual = fecha_inicio 
            while fecha_actual <= fecha_fin:
                # Verificar si la hora actual está dentro del horario de trabajo
                if fecha_actual.weekday() in dias_trabajo:
                    if (fecha_actual.time() > hora_inicio_manana and fecha_actual.time() <= hora_fin_manana) or (fecha_actual.time() > hora_inicio_tarde and fecha_actual.time() <= hora_fin_tarde):
                        fechas.append(fecha_actual)
                fecha_actual += dt.timedelta(minutes=30)
        # Imprimir lista de fechas
        for fecha in fechas:
            print(fecha)
        cantidad_media_horas=len(fechas)
        cantidad_horas=cantidad_media_horas/2
        horas_enteras = int(cantidad_horas)
        minutos_fraccion = int((cantidad_horas - horas_enteras) * 60)
        if horas_enteras==0:
            cantidad_horas=f"{minutos_fraccion} minutos"
        elif minutos_fraccion==0 and horas_enteras==1:
            cantidad_horas=f"{horas_enteras} hora"
        elif minutos_fraccion==0:
            cantidad_horas=f"{horas_enteras} horas"
        elif horas_enteras==1:
            cantidad_horas=f"{horas_enteras} hora y {minutos_fraccion} minutos"
        else:
            cantidad_horas=f"{horas_enteras} horas y {minutos_fraccion} minutos"
        
        query = "INSERT INTO solicitud_permisos (fecha_inicio_permiso, fecha_fin_permiso, fecha_solicitud, horas_de_permiso, id_usuario, motivo_permiso ) VALUES (%s,%s, %s, %s, %s, %s)"
        params = [inicio_permiso, fin_permiso,fecha_solicitud,cantidad_horas, id_usuario, motivo_permiso]
        cursor.execute(query, params)
        conexion.commit()

        flash('Permiso solicitado satisfactoriamente','correcto')
        return redirect('/permisos')
    if 'cancelarPermiso' in request.form:
        permiso_id=request.form['permiso_id']
        cursor.execute("DELETE FROM solicitud_permisos WHERE id_permisos = %s;", (permiso_id,))
        conexion.commit()
        flash('Permiso cancelado satisfactoriamente','correcto')
        return redirect('/permisos')
    return render_template('calendario/templates/permisos.html', solicitudes_permisos=solicitudes_permisos, solicitudes_permisos2=solicitudes_permisos2)

@app.route('/eventos')
def obtener_cursos():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        'SELECT * FROM cursos')
    eventos = cursor.fetchall()
    cursor.execute(
        'SELECT tipo_vacaciones, fecha_inicio_vacaciones, fecha_fin_vacaciones FROM vacaciones WHERE id_usuario=%s', session['usuario'])
    vacaciones = cursor.fetchall()

    cursor.execute('SELECT tipo_vacaciones, fecha_inicio, fecha_fin FROM vacaciones_extemporaneas WHERE id_usuario=%s AND estado_solicitud=%s' , (session['usuario'], 'Aceptado'))
    vacaciones_ex = cursor.fetchall()

    cursor.execute('SELECT fecha_inicio_permiso, fecha_fin_permiso FROM solicitud_permisos WHERE id_usuario=%s AND estado_solicitud=%s' , (session['usuario'], 'Aceptado'))
    permisos = cursor.fetchall()

    cursor.execute('SELECT fecha_inicio_recuperacion, fecha_fin_recuperacion FROM solicitud_permisos WHERE id_usuario=%s AND estado_solicitud=%s' , (session['usuario'], 'Aceptado'))
    permisos_recuperar = cursor.fetchall()

    cursor.execute('SELECT Nombre, Apellido, Fecha_nacimiento FROM general_users')
    cumpleaños = cursor.fetchall()

    eventos_json = []
    for evento in eventos:
        evento_json = {'title': evento[2], 'start': evento[3].strftime(
            '%Y-%m-%d'), 'end': evento[4].strftime(
            '%Y-%m-%d'),  'location': evento[6], 'allDay': 'true', "className": 'bg-info'}
        eventos_json.append(evento_json)
    for vacaciones in vacaciones:
        evento_json = {'title': 'Vacaciones '+ vacaciones[0], 'start': vacaciones[1].strftime(
            '%Y-%m-%d'), 'end': vacaciones[2].strftime(
            '%Y-%m-%d'), 'allDay': 'true', "className": 'bg-success'}
        eventos_json.append(evento_json)
    for vacaciones_ex in vacaciones_ex:
        evento_json = {'title': 'Vacaciones Extemporanea '+ vacaciones_ex[0], 'start': vacaciones_ex[1].strftime(
            '%Y-%m-%d'), 'end': vacaciones_ex[2].strftime(
            '%Y-%m-%d'), 'allDay': 'true',  "backgroundColor": "#D0A9F5"}
        eventos_json.append(evento_json)
    for permisos in permisos:
        evento_json = {'title': 'Permiso ', 'start': permisos[0].strftime(
            '%Y-%m-%d %H:%M:%S'), 'end': permisos[1].strftime(
            '%Y-%m-%d %H:%M:%S'), 'allDay': 'false', "backgroundColor": "#2D89DA"}
        eventos_json.append(evento_json)
    for permisos_recuperar in permisos_recuperar:
        evento_json = {'title': 'Recuperar Permiso ', 'start': permisos_recuperar[0].strftime(
            '%Y-%m-%d %H:%M:%S'), 'end': permisos_recuperar[1].strftime(
            '%Y-%m-%d %H:%M:%S'), 'allDay': 'false', "backgroundColor": "#9B2DDA"}
        eventos_json.append(evento_json)
    for cumpleaños in cumpleaños:
        evento_json = {'title': f'Cumpleaños de {cumpleaños[0]} {cumpleaños[1]}','start': cumpleaños[2].strftime('%Y-%m-%d'),
        "recurrence": ["RRULE:FREQ=YEARLY"],'allDay': 'true',"backgroundColor": "#CFD13F"}
        eventos_json.append(evento_json)
    
    return jsonify(eventos_json)
