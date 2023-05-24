import datetime
import os
from random import sample
from flask import send_file
from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for
import json
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for
from main.run import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
import webbrowser

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
        "SELECT Nombre, Apellido, correo, celular, foto ,profesion FROM general_users WHERE usuario != %s;", session["usuario"])
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
    datosUsuarios = cursor.fetchall()
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

            
            # Realizar la consulta para obtener la contraseña almacenada
            usuario = session['usuario']
            cursor.execute("SELECT contrasena, usuario FROM general_users WHERE usuario = %s;", (usuario,))
            change_password = cursor.fetchall()
            
            stored_password_hash = change_password[0][0]
            print('DDDDDDDDD')
            if bcrypt.checkpw(actual_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
              
                if new_password == confirm_password:
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    query = "UPDATE general_users SET contrasena = %s WHERE usuario = %s"
                    params = [hashed_password, usuario]
                    cursor.execute(query, params)
                    conexion.commit()  
                    alerta = 0                      
                    return render_template('infoUsuario/templates/configuration.html', alerta=alerta)
                else:
                 
                    alerta = 1
                    return render_template('infoUsuario/templates/configuration.html', alerta=alerta)
            else:
          
                alerta = 2
                return render_template('infoUsuario/templates/configuration.html', alerta=alerta)
        else:
            print('No es POST')

    # Renderizar el perfil actualizado
    return render_template('infoUsuario/templates/configuration.html')
