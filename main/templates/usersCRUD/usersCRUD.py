import datetime
import os
from random import sample

from flask import send_file
from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for
import json
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for
from main.app import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename

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
    return render_template('usersCRUD/templates/contactEdit.html', datosUsuarios=datosUsuarios)

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
            basepath, '..', '..','static', 'images', nuevoNombreFoto)
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

    return render_template('usersCRUD/templates/agregarUsuario.html', datosUsuarios=datosUsuarios, campos=request.form)

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
        return render_template('usersCRUD/templates/contactEdit.html', usuario=usuario)


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
    return render_template('usersCRUD/templates/verUser.html', datosUsuarios=datosUsuarios)


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
              

        # Actualizar los campos que no están vacíos
        query = "UPDATE general_users SET"
        params = []

        if foto:
            basepath = os.path.dirname(__file__)
            filename = secure_filename(foto.filename)
            extension = os.path.splitext(filename)[1]
            nuevoNombreFoto = usuario_id+'Foto'+extension
            upload_path = os.path.join(
            basepath, '..','..', 'static', 'images', nuevoNombreFoto)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))
            foto.save(upload_path)
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
        if contrasena:
            hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
            query += "contrasena = %s,"
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

    return render_template('usersCRUD/templates/editUser.html', datosUsuarios=datosUsuarios)

