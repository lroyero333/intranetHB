import datetime
import os
from random import sample
from datetime import datetime
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
            ruta_archivo = os.path.join(app.root_path, 'static', 'archivos', 'certificados', nombre_archivo)

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
            ruta_archivo = os.path.join(app.root_path, 'static', 'archivos', 'nominas', nombre_archivo)

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
    
    if request.method == 'POST':

        if 'solicitar_certificado'in request.form:
            tipo_certificado = request.form['tipo_certificado']
            nombre_certificado=request.form['nombre_certificado']
            solicitante = session["usuario"]
            fecha_solicitud = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO solicitud_certificado (tipo_certificado, nombre_certificado, solicitante, fecha_solicitud ) VALUES (%s,%s,%s,%s)"
            params = [tipo_certificado, nombre_certificado, solicitante, fecha_solicitud]
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/nomina_certificados/')
        
        if 'cancelar_certificado'in request.form:
            certificadoCancelar=request.form['cancelar_certificado']
            cursor.execute("DELETE FROM solicitud_certificado WHERE id_solicitud=%s;", certificadoCancelar)
            conexion.commit()
            return redirect('/nomina_certificados/')
        
        if 'solicitar_nomina'in request.form:
            solicitante = session["usuario"]
            nombre_nomina=request.form['nombre_nomina']
            fecha_solicitud = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            motivo_solicitud=request.form['motivo_solicitud']
            query = "INSERT INTO solicitud_nomina (nombre_nomina, solicitante, fecha_solicitud ,motivo_solicitud) VALUES (%s,%s,%s,%s)"
            params = [nombre_nomina,solicitante, fecha_solicitud, motivo_solicitud]
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/nomina_certificados/')
        
        if 'cancelar_nomina'in request.form:
            nominaCancelar=request.form['cancelar_nomina']
            cursor.execute("DELETE FROM solicitud_nomina WHERE id_solicitud_nomina=%s;", nominaCancelar)
            conexion.commit()
            return redirect('/nomina_certificados/')
        
    cursor.execute("SELECT solicitud_certificado.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.persona_resuelve_solicitud = general_users.usuario WHERE solicitante = %s ORDER BY fecha_solicitud DESC ;", session["usuario"])
    solicitudesCertificado = cursor.fetchall()
    cursor.execute("SELECT solicitud_nomina.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.persona_resuelve_solicitud = general_users.usuario WHERE solicitante = %s ORDER BY fecha_solicitud DESC ;", session["usuario"])
    solicitudesNomina = cursor.fetchall()
    conexion.commit()

    return render_template('nomina_certificados/templates/nominas_certificados_usuario.html', nomina=nomina, certificado=certificado,solicitudesCertificado=solicitudesCertificado,solicitudesNomina=solicitudesNomina)


