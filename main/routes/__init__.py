from flask import request, redirect
from werkzeug.utils import secure_filename
import os
import json
from flask import render_template, redirect, request, url_for, session, flash
import bcrypt
from werkzeug.utils import secure_filename
import os
from main.app import app, mysql
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from main.templates.login import login

from main.templates.register import register

from main.templates.calendario import calendario

"""import pyrebase

config = {
    "apiKey": "AIzaSyDsjemDIJl28I1dkoGW4aFIojZ6pJeMZCY",
    "authDomain": "intranethb.firebaseapp.com",
    "databaseURL": "https://firebase.google.com/docs/web/setup#available-libraries",
    "projectId": "intranethb",
    "storageBucket": "intranethb.appspot.com",
    "messagingSenderId": "20219685128",
    "appId": "1:20219685128:web:3656bb076ac7222d9524bd"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

def upload_image_to_firebase_storage(file_path):
    filename = file_path.split("/")[-1]
    storage.child("images/" + filename).put(file_path)
    url = storage.child("images/" + filename).get_url(None)
    return url

"""

"""
@app.before_request
def datosUsuario():

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(
        "SELECT *  FROM general_users WHERE usuario = %s", (session["usuario"]))
    row = cursor.fetchone()
    conexion.commit()
    session["login"]=True
    session["usuario"]=row[26]
    session["nombre"]=row[1]
    session["nombre2"]=row[2]
    session["apellido"]=row[3]
    session["apellido2"]=row[4]
    session["genero"]=row[5]
    session["fecha_nacimiento"]=row[7]
    session["edad"]=row[28]
    session["correo"]=row[7]
    session["identificacion"]=row[8]
    session["direccion"]=row[9]
    session["barrio"]=row[10]
    session["ciudad"]=row[11]
    session["departamento"]=row[12]
    session["pais"]=row[13]
    session["telefono"]=row[14]
    session["celular"]=row[15]
    session["habilidades"]=row[16]
    session["profesion"]=row[17]
    session["cargo"]=row[18]
    session["institucion"]=row[19]
    session["posgrado"]=row[20]
    session["entidad_salud"]=row[21]
    session["tipo_sangre"]=row[22]
    session["foto"]=row[23]
    session["nombre_contacto"]=row[24]
    session["numero_contacto"]=row[25]
"""


@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect('/')


url_inicio = '/inicio'


"""@app.route('/notificaciones')
def notificaciones():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Recuperar las notificaciones sin leer de la base de datos
    notificaciones = Notification.query.filter_by(
        user_id=session['user_id'], leido=False).all()

    # Marcar las notificaciones como leídas y actualizar la base de datos
    for notificacion in notificaciones:
        notificacion.leido = True
        db.session.add(notificacion)
    db.session.commit()

    # Eliminar las notificaciones leídas de la sesión del usuario
    session.pop('notificaciones', None)

    return render_template('notificaciones.html', notificaciones=notificaciones)"""


@app.route('/inicio')
def inicio():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM cursos ;")
    datosCursos = cursor.fetchall()
    conexion.commit()
    cursos_con_tiempo = []
    for curso in datosCursos:
        fecha_insertado = curso[5]
        fecha_actual = datetime.now()
        diferencia = relativedelta(fecha_actual, fecha_insertado)
        if diferencia.years > 0:
            tiempo_transcurrido = f"hace {diferencia.years} años"
        elif diferencia.months > 0:
            tiempo_transcurrido = f"hace {diferencia.months} meses"
        elif diferencia.days > 0:
            tiempo_transcurrido = f"hace {diferencia.days} días"
        elif diferencia.hours > 0:
            tiempo_transcurrido = f"hace {diferencia.hours} horas"
        elif diferencia.minutes > 0:
            tiempo_transcurrido = f"hace {diferencia.minutes} minutos"
        else:
            tiempo_transcurrido = f"hace {diferencia.seconds} segundos"
        # convertir a lista para poder modificar
        curso_con_tiempo = list(curso)
        curso_con_tiempo.append(tiempo_transcurrido)
        cursos_con_tiempo.append(curso_con_tiempo)

    cursor.execute(
        "SELECT * FROM noticias ;")
    datosNoticias = cursor.fetchall()
    conexion.commit()
    noticias_con_tiempo = []
    for noticia in datosNoticias:
        fecha_insertado = noticia[5]
        fecha_actual = datetime.now()
        diferencia = relativedelta(fecha_actual, fecha_insertado)
        if diferencia.years > 0:
            tiempo_transcurrido = f"hace {diferencia.years} años"
        elif diferencia.months > 0:
            tiempo_transcurrido = f"hace {diferencia.months} meses"
        elif diferencia.days > 0:
            tiempo_transcurrido = f"hace {diferencia.days} días"
        elif diferencia.hours > 0:
            tiempo_transcurrido = f"hace {diferencia.hours} horas"
        elif diferencia.minutes > 0:
            tiempo_transcurrido = f"hace {diferencia.minutes} minutos"
        else:
            tiempo_transcurrido = f"hace {diferencia.seconds} segundos"
        # convertir a lista para poder modificar
        # Cambiar el nombre de la variable aquí
        noticia_con_tiempo = list(noticia)
        noticia_con_tiempo.append(tiempo_transcurrido)
        noticias_con_tiempo.append(noticia_con_tiempo)  # Agregar a la lista

    return render_template('templates/light/index.html', datosCursos=cursos_con_tiempo, datosNoticias=noticias_con_tiempo)


@app.route('/Noticias')
def noticias():
    if not 'login' in session:
        return redirect('/')
    return render_template('sitio/Noticias.html')


@app.route('/static/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/agregar-cursos')
def tareas():
    if not 'login' in session:
        return redirect('/')
    return render_template('templates/light/agregarEvento.html')


@app.route('/proyectos', methods=['GET', 'POST'])
def crearProyecto():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()

    if request.method == 'POST' and 'crear_proyecto' in request.form:

        nombre_proyecto = request.form['nombre_proyecto']
        imagen_proyecto = request.form['imagen_proyecto']
        descripcion_proyecto = request.form['descripcion_proyecto']

        query = "INSERT INTO proyectos (nombre_proyecto, imagen_proyecto, descripcion_proyecto) VALUES (%s,%s, %s)"
        params = [nombre_proyecto, imagen_proyecto, descripcion_proyecto]

        cursor.execute(query, params)
        conexion.commit()
        conexion.close()
        return redirect('/proyectos')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM proyectos;")
    datosProyectos = cursor.fetchall()
    conexion.commit()
    conexion.close()
    return render_template('templates/light/projects.html', datosProyectos=datosProyectos)


@app.route('/empleados')
def listaEmpleados():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, Apellido, correo, celular, foto ,profesion ,usuario FROM general_users;")
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    return render_template('templates/light/contactEdit.html', datosUsuarios=datosUsuarios)


@app.route('/eliminar-usuario/<usuario>', methods=['GET', 'POST'])
def eliminarUsuario(usuario):
    if not 'login' in session:
        return redirect('/')
    if request.method == 'POST':
        conexion = mysql.connect()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM general_users WHERE usuario=%s;", usuario)
        conexion.commit()
        flash('El usuario ha sido eliminado.', 'success')
        return redirect('/empleados')
    else:
        return render_template('templates/light/contactEdit.html', usuario=usuario)


@app.route('/verEmpleado/<string:usuario_id>')
def verEmpleados(usuario_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT general_users.*, cargos.nombre_cargo FROM general_users LEFT JOIN usuario_cargo ON general_users.id = usuario_cargo.id_usuario_fk LEFT JOIN cargos ON usuario_cargo.id_cargo_fk = cargos.id_cargo WHERE usuario= %s;", usuario_id)
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    return render_template('templates/light/verUser.html', datosUsuarios=datosUsuarios)


@app.route('/editEmpleados/<string:usuario_id>', methods=['GET', 'POST'])
def editEmpleados(usuario_id):
    if not 'login' in session:
        return redirect('/')
    print(session['cargo'])
    if session['cargo'] != 1:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM general_users WHERE usuario= %s", usuario_id)
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    if request.method == 'POST':
        foto = request.files['foto']
        Nombre = request.form['Nombre']
        segundo_nombre = request.form['segundo_nombre']
        Apellido = request.form['Apellido']
        segundo_apellido = request.form['segundo_apellido']
        genero = request.form['genero']
        fecha_nacimiento = request.form['Fecha_nacimiento']
        correo = request.form['correo']
        identificacion = request.form['identificacion']
        direccion = request.form['direccion']
        barrio = request.form['barrio']
        ciudad = request.form['ciudad']
        departamento = request.form['departamento']
        pais = request.form['pais']
        telefono = request.form['telefono']
        celular = request.form['celular']
        habilidades = request.form['habilidades']
        profesion = request.form['profesion']
        cargo = request.form['cargo']
        institucion = request.form['institucion']
        posgrado = request.form['posgrado']
        entidad_salud = request.form['entidad_salud']
        tipo_sangre = request.form['tipo_sangre']
        nombre_contacto = request.form['nombre_contacto']
        numero_contacto = request.form['numero_contacto']
        contrasena = request.form['contrasena']
        hashed_password = bcrypt.hashpw(
            contrasena.encode('utf-8'), bcrypt.gensalt())

        basepath = os.path.dirname(__file__)
        filename = secure_filename(foto.filename)

        extension = os.path.splitext(filename)[1]
        nuevoNombreFoto = usuario_id+'Foto'+extension

        upload_path = os.path.join(
            basepath, '..', 'static', 'images', nuevoNombreFoto)
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        foto.save(upload_path)

        # Actualizar los campos que no están vacíos
        query = "UPDATE general_users SET"
        params = []

        if nuevoNombreFoto:
            query += " foto = %s,"
            params.append(nuevoNombreFoto)
        if Nombre:
            query += " Nombre = %s,"
            params.append(Nombre)
        if segundo_nombre:
            query += " segundo_nombre = %s,"
            params.append(segundo_nombre)
        if Apellido:
            query += " Apellido = %s,"
            params.append(Apellido)
        if segundo_apellido:
            query += " segundo_apellido = %s,"
            params.append(segundo_apellido)
        if genero:
            query += " genero = %s,"
            params.append(genero)
        if fecha_nacimiento:
            query += " fecha_nacimiento = %s,"
            params.append(fecha_nacimiento)
        if correo:
            query += " correo = %s,"
            params.append(correo)
        if identificacion:
            query += " identificacion = %s,"
            params.append(identificacion)
        if direccion:
            query += " direccion = %s,"
            params.append(direccion)
        if barrio:
            query += " barrio = %s,"
            params.append(barrio)
        if ciudad:
            query += " ciudad = %s,"
            params.append(ciudad)
        if departamento:
            query += " departamento = %s,"
            params.append(departamento)
        if pais:
            query += " pais = %s,"
            params.append(pais)
        if telefono:
            query += " telefono = %s,"
            params.append(telefono)
        if celular:
            query += " celular = %s,"
            params.append(celular)
        if habilidades:
            query += " habilidades = %s,"
            params.append(habilidades)
        if profesion:
            query += " profesion = %s,"
            params.append(profesion)
        if cargo:
            query += " id_cargo_fk = %s,"
            params.append(cargo)

        if institucion:
            query += " institucion = %s,"
            params.append(institucion)
        if posgrado:
            query += " posgrado = %s,"
            params.append(posgrado)
        if entidad_salud:
            query += " entidad_salud = %s,"
            params.append(entidad_salud)
        if tipo_sangre:
            query += " tipo_sangre = %s,"
            params.append(tipo_sangre)
        if nombre_contacto:
            query += " nombre_contacto = %s,"
            params.append(nombre_contacto)
        if numero_contacto:
            query += " numero_contacto = %s,"
            params.append(numero_contacto)
        if hashed_password:
            query += " contrasena = %s,"
            params.append(hashed_password)

        # Eliminar la coma final de la consulta SQL
        query = query.rstrip(',')

        # Agregar la cláusula WHERE
        query += " WHERE usuario = %s"
        params.append(usuario_id)

        # Ejecutar la consulta SQL
        cursor.execute(query, params)

        # Confirmar los cambios en la base de datos
        conexion.commit()

        # Redirigir a la página de detalles del usuario actualizado
        return redirect(url_for('verEmpleados', usuario_id=usuario_id))

    return render_template('templates/light/editUser.html', datosUsuarios=datosUsuarios)


@app.route('/registrarEmpleados', methods=['GET', 'POST'])
def crearEmpleados():
    if not 'login' in session:
        return redirect('/')
    print(session['cargo'])
    if session['cargo'] != 1:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM general_users")
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    if request.method == 'POST':

        usuario = request.form['usuario']
        # Verificar si el usuario ya existe
        cursor.execute(
            "SELECT * FROM general_users WHERE usuario=%s", (usuario,))
        if cursor.fetchone() is not None:
            error = 'El nombre de usuario o correo electrónico ya está en uso'
            cursor.close()
            return render_template('templates/light/agregarUsuario.html', error=error, datosUsuarios=datosUsuarios, campos=request.form)
        foto = request.files['foto']
        Nombre = request.form['Nombre']
        segundo_nombre = request.form['segundo_nombre']
        Apellido = request.form['Apellido']
        segundo_apellido = request.form['segundo_apellido']
        genero = request.form['genero']
        fecha_nacimiento = request.form['Fecha_nacimiento']
        correo = request.form['correo']
        identificacion = request.form['identificacion']
        direccion = request.form['direccion']
        barrio = request.form['barrio']
        ciudad = request.form['ciudad']
        departamento = request.form['departamento']
        pais = request.form['pais']
        telefono = request.form['telefono']
        celular = request.form['celular']
        habilidades = request.form['habilidades']
        profesion = request.form['profesion']
        cargo = request.form['cargo']
        institucion = request.form['institucion']
        posgrado = request.form['posgrado']
        entidad_salud = request.form['entidad_salud']
        tipo_sangre = request.form['tipo_sangre']
        nombre_contacto = request.form['nombre_contacto']
        numero_contacto = request.form['numero_contacto']
        contrasena = request.form['contrasena']

        hashed_password = bcrypt.hashpw(
            contrasena.encode('utf-8'), bcrypt.gensalt())

        basepath = os.path.dirname(__file__)
        filename = secure_filename(foto.filename)

        extension = os.path.splitext(filename)[1]
        nuevoNombreFoto = usuario+'Foto'+extension

        upload_path = os.path.join(
            basepath, '..', 'static', 'images', nuevoNombreFoto)
        if not os.path.exists(os.path.dirname(upload_path)):
            os.makedirs(os.path.dirname(upload_path))

        foto.save(upload_path)

        # Insertar un nuevo usuario en la tabla
        query = "INSERT INTO general_users (Nombre, segundo_nombre, Apellido, segundo_apellido, genero, fecha_nacimiento, correo, identificacion, direccion, barrio, ciudad, departamento, pais, telefono, celular, habilidades, profesion, id_cargo_fk, institucion, posgrado, entidad_salud, tipo_sangre,foto, nombre_contacto, numero_contacto, usuario,contrasena) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)"
        params = [Nombre, segundo_nombre, Apellido, segundo_apellido, genero, fecha_nacimiento, correo, identificacion, direccion, barrio, ciudad, departamento, pais,
                  telefono, celular, habilidades, profesion, cargo, institucion, posgrado, entidad_salud, tipo_sangre, nuevoNombreFoto, nombre_contacto, numero_contacto, usuario, hashed_password]

        # Ejecutar la consulta SQL
        cursor.execute(query, params)

        # Confirmar los cambios en la base de datos
        conexion.commit()

        # Redirigir a la página de detalles del nuevo usuario registrado
        usuario_id = cursor.lastrowid
        return redirect('/empleados')

    return render_template('templates/light/agregarUsuario.html', datosUsuarios=datosUsuarios, campos=request.form)


@app.route('/contactos')
def listaEmpleadosContact():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, Apellido, correo, celular, foto ,profesion FROM general_users WHERE usuario != %s;", session["usuario"])
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)

    return render_template('templates/light/app-contact.html', datosUsuarios=datosUsuarios)


@app.route('/myProfile', methods=['GET', 'POST'])
def myperfil():
    if not 'login' in session:
        return redirect('/')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT general_users.*, cargos.nombre_cargo FROM general_users LEFT JOIN usuario_cargo ON general_users.id = usuario_cargo.id_usuario_fk LEFT JOIN cargos ON usuario_cargo.id_cargo_fk = cargos.id_cargo WHERE usuario= %s;", session['usuario'])
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)
    # Obtener la información de la sesión actual

    # Renderizar el perfil actualizado
    return render_template('templates/light/profile.html',  datosUsuarios=datosUsuarios)


@app.errorhandler(404)
def error_404(error):
    return render_template('templates/light/error-404.html')


@app.errorhandler(400)
def error_400(error):
    return render_template('templates/light/error-400.html')


@app.errorhandler(401)
def error_401(error):
    return render_template('templates/light/error-401.html')


@app.errorhandler(403)
def error_403(error):
    return render_template('templates/light/error-403.html')
