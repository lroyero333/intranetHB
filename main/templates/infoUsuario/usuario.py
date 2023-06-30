import datetime
import json
import os
import webbrowser
from random import sample

from flask import send_file
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (app, bcrypt, flash, jsonify, mysql, redirect,
                      render_template, request, session, url_for,is_password_strong)


@app.route('/enviar_correo/<correo>')
def enviar_correo(correo):
    mailto_url = f"mailto:{correo}"
    webbrowser.open(mailto_url)
    return redirect('/contactos')


@app.route('/contactos')
def listaEmpleadosContact():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, Apellido, correo, celular, foto ,profesion FROM general_users WHERE usuario != %s and estado_usuario='Aceptado';", session["usuario"])
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)

    return render_template('infoUsuario/templates/app-contact.html', datosUsuarios=datosUsuarios)


@app.route('/myProfile', methods=['GET', 'POST'])
def myperfil():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT general_users.*, cargos.nombre_cargo FROM general_users LEFT JOIN usuario_cargo ON general_users.id = usuario_cargo.id_usuario_fk LEFT JOIN cargos ON usuario_cargo.id_cargo_fk = cargos.id_cargo WHERE usuario= %s;", session['usuario'])
    datosUsuarios = cursor.fetchone()
    conexion.commit()
    print(datosUsuarios)
    # Obtener la información de la sesión actual

    # Renderizar el perfil actualizado
    return render_template('infoUsuario/templates/profile.html',  datosUsuarios=datosUsuarios)


@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    if 'login' not in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        if 'cambio_contrasena' in request.form:

            actual_password = request.form['password']

            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if not is_password_strong(new_password):
                flash('La contraseña debe tener al menos 8 caracteres y contener al menos una letra mayúscula, una letra minúscula y un dígito.','error')
                return redirect(request.url)

            # Realizar la consulta para obtener la contraseña almacenada
            usuario = session['usuario']
            cursor.execute(
                "SELECT contrasena, usuario FROM general_users WHERE usuario = %s;", (usuario,))
            change_password = cursor.fetchall()
            stored_password_hash = change_password[0][0]
            print('DDDDDDDDD')
            if bcrypt.checkpw(actual_password.encode('utf-8'), stored_password_hash.encode('utf-8')):

                if new_password == confirm_password:
                    hashed_password = bcrypt.hashpw(
                        new_password.encode('utf-8'), bcrypt.gensalt())
                    query = "UPDATE general_users SET contrasena = %s WHERE usuario = %s"
                    params = [hashed_password, usuario]
                    cursor.execute(query, params)
                    conexion.commit()
                    flash('¡La contraseña se ha cambiado correctamente!', 'correcto')
                    return redirect(request.url)
                else:
                    flash('Las contraseñas no coinciden. Por favor, asegúrate de ingresar la misma contraseña en ambos campos.','error')
                    return redirect(request.url)
            else:

                flash('La contraseña actual no es correcta. Por favor, verifica que has ingresado la contraseña actual correctamente','error')
                return redirect(request.url)

        else:
            print('No es POST')

    # Renderizar el perfil actualizado
    return render_template('infoUsuario/templates/configuration.html')
