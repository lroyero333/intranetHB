import datetime
import os
from random import sample

from flask import send_file
from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for
import json
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for
from main.app import app, request, bcrypt, mysql, redirect, render_template, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename

def stringAleatorio():
    string_aleatorio="0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud=10
    secuencia=string_aleatorio.upper()
    resultado_aleatorio= sample(secuencia, longitud)
    string_aleatorio= "".join(resultado_aleatorio)
    return string_aleatorio

#Human Resource view the list of user and can select nomina and certificates
@app.route('/nomina_certificados', methods=['GET', 'POST'])
def verNominaCertificados():
    if not 'login' in session:
        return redirect('/')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT Nombre, segundo_nombre, Apellido, segundo_apellido, usuario, profesion, correo, foto FROM general_users;")
    datosUsuarios = cursor.fetchall()
    conexion.commit()
    print(datosUsuarios)
    
    return render_template('nomina_certificados/templates/nomina_certificadosRH.html',  datosUsuarios=datosUsuarios)

@app.route('/certificados/<string:usuario_id>', methods=['GET', 'POST'])
def verCertificados(usuario_id):
    if not 'login' in session:
        return redirect('/')
    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT certificados.*, general_users.Nombre AS nombre_sube, general_users.Apellido AS apellido_sube FROM certificados LEFT JOIN general_users ON certificados.usuario_sube_certificado = general_users.usuario WHERE id_usuario_fk = %s;", usuario_id)
    certificado = cursor.fetchall()
    conexion.commit()
   
    if request.method == 'POST':
        if 'crear_certificado' in request.form:
            nombre_certificado = request.form['nombre_certificado']
            usuario_sube_certificado = session["usuario"]
            fecha_subida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            archivo_certificado = request.files['archivo_certificado']

            
            filename = secure_filename(archivo_certificado.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreCertificado = stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, '..','..', 'static', 'archivos', 'certificados', nuevoNombreCertificado)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            archivo_certificado.save(upload_path)

            query = "INSERT INTO certificados (id_usuario_fk, nombre_certificado, usuario_sube_certificado, fecha_subida,archivo_certificado) VALUES (%s,%s,%s, %s, %s)"
            params = [usuario_id, nombre_certificado,  usuario_sube_certificado,  fecha_subida, nuevoNombreCertificado]



            cursor.execute(query, params)
            conexion.commit()

            return redirect(f'/certificados/{usuario_id}')
        if 'eliminar_certificado' in request.form:
    
            nombre_archivo = request.form['eliminar_certificado']
            print(nombre_archivo)
            ruta_archivo = os.path.join(app.root_path,'..', 'static', 'archivos', 'certificados', nombre_archivo)

            cursor.execute("DELETE FROM certificados WHERE archivo_certificado = %s;", nombre_archivo)
            conexion.commit()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            flash('El certificado ha sido eliminado.', 'success')
            
            return redirect(f'/certificados/{usuario_id}')
        if 'descargar_certificado'in request.form:

            nombre_archivo = request.form['descargar_certificado']
            url_File=os.path.join (basepath, '..','..', 'static', 'archivos', 'certificados', nombre_archivo)
            resp=send_file(url_File,as_attachment=True)

            return resp


    return render_template('nomina_certificados/templates/certificados.html',  certificado=certificado)

@app.route('/nominas/<string:usuario_id>', methods=['GET', 'POST'])
def verNominas(usuario_id):
    if not 'login' in session:
        return redirect('/')
    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT nominas.*, general_users.Nombre AS nombre_sube, general_users.Apellido AS apellido_sube FROM nominas LEFT JOIN general_users ON nominas.usuario_sube_nomina = general_users.usuario WHERE id_usuario_fk = %s;", usuario_id)
    nomina = cursor.fetchall()
    conexion.commit()
   
    if request.method == 'POST':
        if 'crear_nomina' in request.form:
            nombre_nomina = request.form['nombre_nomina']
            usuario_sube_nomina = session["usuario"]
            fecha_subida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            archivo_nomina = request.files['archivo_nomina']

            
            filename = secure_filename(archivo_nomina.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreNomina = stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, '..', '..', 'static', 'archivos', 'nominas', nuevoNombreNomina)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            archivo_nomina.save(upload_path)

            query = "INSERT INTO nominas (id_usuario_fk,  usuario_sube_nomina, nombre_nomina, fecha_subida ,archivo_nomina) VALUES (%s,%s,%s, %s, %s)"
            params = [usuario_id,  usuario_sube_nomina, nombre_nomina, fecha_subida, nuevoNombreNomina]



            cursor.execute(query, params)
            conexion.commit()

            return redirect(f'/nominas/{usuario_id}')
        if 'eliminar_nomina' in request.form:
    
            nombre_archivo = request.form['eliminar_nomina']
            print(nombre_archivo)
            ruta_archivo = os.path.join(app.root_path, '..', 'static', 'archivos', 'nominas', nombre_archivo)

            cursor.execute("DELETE FROM nominas WHERE archivo_nomina = %s;", nombre_archivo)
            conexion.commit()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            flash('La nomina ha sido eliminado.', 'success')
            
            return redirect(f'/nominas/{usuario_id}')
        
        if 'descargar_nomina'in request.form:
            nombre_archivo = request.form['descargar_nomina']
            url_File=os.path.join (basepath, '..', '..', 'static', 'archivos', 'nominas', nombre_archivo)
            resp=send_file(url_File,as_attachment=True)
            return resp

    return render_template('nomina_certificados/templates/nominas.html',  nomina=nomina)

@app.route('/nomina_certificados/', methods=['GET', 'POST'])
def verNominaCertificadosUsuario():
    if not 'login' in session:
        return redirect('/')
    
    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT certificados.*, general_users.Nombre AS nombre_sube, general_users.Apellido AS apellido_sube FROM certificados LEFT JOIN general_users ON certificados.usuario_sube_certificado = general_users.usuario WHERE id_usuario_fk = %s;", session["usuario"])
    certificado = cursor.fetchall()
    cursor.execute("SELECT nominas.*, general_users.Nombre AS nombre_sube, general_users.Apellido AS apellido_sube FROM nominas LEFT JOIN general_users ON nominas.usuario_sube_nomina = general_users.usuario WHERE id_usuario_fk = %s;", session["usuario"])
    nomina = cursor.fetchall()
    conexion.commit()

    if 'descargar_nomina'in request.form:
        nombre_archivo = request.form['descargar_nomina']
        url_File=os.path.join (basepath, '..','..', 'static', 'archivos', 'nominas', nombre_archivo)
        resp=send_file(url_File,as_attachment=True)
        return resp
    if 'descargar_certificado'in request.form:
        nombre_archivo = request.form['descargar_certificado']
        url_File=os.path.join (basepath, '..','..', 'static', 'archivos', 'certificados', nombre_archivo)
        resp=send_file(url_File,as_attachment=True)
        return resp
   
  
    return render_template('nomina_certificados/templates/nominas_certificados_usuario.html', nomina=nomina, certificado=certificado)