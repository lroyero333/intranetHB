import datetime
import json
import os
from datetime import datetime
from random import sample

from flask import send_file
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (app, bcrypt, fecha_actualCO, flash, generarID, jsonify,
                      mysql, redirect, render_template, request, session,
                      stringAleatorio, url_for)

extensionArchivo = ['.pdf']
# Human Resource view the list of user and can select nomina and certificates


@app.route('/nomina_certificados', methods=['GET', 'POST'])
def verNominaCertificados():
    if not 'login' in session:
        return redirect('/')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Nombre, segundo_nombre, Apellido, segundo_apellido, usuario, profesion, correo, foto FROM general_users;")
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
    cursor.execute(
        "SELECT  Nombre, Apellido FROM general_users WHERE usuario = %s;", usuario_id)
    certificado_usuario = cursor.fetchone()
    conexion.commit()

    if request.method == 'POST':
        if 'crear_certificado' in request.form:
            nombre_certificado = request.form['nombre_certificado']
            usuario_sube_certificado = session["usuario"]
            fecha_subida =fecha_actualCO().strftime('%Y-%m-%d %H:%M:%S')
            archivo_certificado = request.files['archivo_certificado']
            filename, file_extension = os.path.splitext(
                archivo_certificado.filename)
            if file_extension.lower() not in extensionArchivo:
                flash(
                    'La extensión del archivo no está permitida. Solo se permiten archivos .PDF', 'error')
                return redirect(request.url)
            else:
                flash('El certificado se ha agregado satisfactoriamente', 'correcto')

            filename = secure_filename(archivo_certificado.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreCertificado = 'CERT' + \
                str(fecha_actualCO().strftime("%d%m%y")) + \
                stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, app.root_path, 'static', 'archivos', 'certificados', nuevoNombreCertificado)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            archivo_certificado.save(upload_path)

            query = "INSERT INTO certificados (id_certificado, id_usuario_fk, nombre_certificado, usuario_sube_certificado, fecha_subida,archivo_certificado) VALUES (%s,%s,%s,%s, %s, %s)"
            params = [generarID(), usuario_id, nombre_certificado,
                      usuario_sube_certificado,  fecha_subida, nuevoNombreCertificado]
            cursor.execute(query, params)
            conexion.commit()

            return redirect(f'/certificados/{usuario_id}')
        if 'eliminar_certificado' in request.form:

            nombre_archivo = request.form['eliminar_certificado']
            print(nombre_archivo)
            ruta_archivo = os.path.join(
                app.root_path, 'static', 'archivos', 'certificados', nombre_archivo)

            cursor.execute(
                "DELETE FROM certificados WHERE archivo_certificado = %s;", nombre_archivo)
            conexion.commit()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            flash('El certificado ha sido eliminado.', 'correcto')

            return redirect(f'/certificados/{usuario_id}')
        if 'descargar_certificado' in request.form:

            nombre_archivo = request.form['descargar_certificado']
            url_File = os.path.join(
                basepath, app.root_path, 'static', 'archivos', 'certificados', nombre_archivo)
            resp = send_file(url_File, as_attachment=True)

            return resp

    return render_template('nomina_certificados/templates/certificados.html',  certificado=certificado, certificado_usuario=certificado_usuario)


@app.route('/nominas/<string:usuario_id>', methods=['GET', 'POST'])
def verNominas(usuario_id):
    if not 'login' in session:
        return redirect('/')
    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT nominas.*, general_users.Nombre AS nombre_sube, general_users.Apellido AS apellido_sube FROM nominas LEFT JOIN general_users ON nominas.usuario_sube_nomina = general_users.usuario WHERE id_usuario_fk = %s;", usuario_id)
    nomina = cursor.fetchall()
    cursor.execute(
        "SELECT  Nombre, Apellido FROM general_users WHERE usuario = %s;", usuario_id)
    nomina_usuario = cursor.fetchone()
    conexion.commit()

    if request.method == 'POST':
        if 'crear_nomina' in request.form:
            nombre_nomina = request.form['nombre_nomina']
            usuario_sube_nomina = session["usuario"]
            fecha_subida =fecha_actualCO().strftime('%Y-%m-%d %H:%M:%S')
            archivo_nomina = request.files['archivo_nomina']

            filename, file_extension = os.path.splitext(
                archivo_nomina.filename)
            if file_extension.lower() not in extensionArchivo:
                flash(
                    'La extensión del archivo no está permitida. Solo se permiten archivos .PDF', 'error')
                return redirect(request.url)
            else:
                flash('La nomina se ha agregado satisfactoriamente', 'correcto')

            filename = secure_filename(archivo_nomina.filename)

            extension = os.path.splitext(filename)[1]
            nuevoNombreNomina = 'NOM' + \
                str(fecha_actualCO().strftime("%d%m%y")) + \
                stringAleatorio() + extension

            upload_path = os.path.join(
                basepath, app.root_path, 'static', 'archivos', 'nominas', nuevoNombreNomina)
            if not os.path.exists(os.path.dirname(upload_path)):
                os.makedirs(os.path.dirname(upload_path))

            archivo_nomina.save(upload_path)

            query = "INSERT INTO nominas (id_nomina, id_usuario_fk,  usuario_sube_nomina, nombre_nomina, fecha_subida ,archivo_nomina) VALUES (%s, %s,%s,%s, %s, %s)"
            params = [generarID(), usuario_id,  usuario_sube_nomina,
                      nombre_nomina, fecha_subida, nuevoNombreNomina]

            cursor.execute(query, params)
            conexion.commit()

            return redirect(f'/nominas/{usuario_id}')
        if 'eliminar_nomina' in request.form:

            nombre_archivo = request.form['eliminar_nomina']
            print(nombre_archivo)
            ruta_archivo = os.path.join(
                app.root_path, 'static', 'archivos', 'nominas', nombre_archivo)

            cursor.execute(
                "DELETE FROM nominas WHERE archivo_nomina = %s;", nombre_archivo)
            conexion.commit()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            flash('La nomina se ha eliminado satisfactoriamente', 'correcto')
            return redirect(f'/nominas/{usuario_id}')

        if 'descargar_nomina' in request.form:
            nombre_archivo = request.form['descargar_nomina']
            url_File = os.path.join(
                basepath, app.root_path, 'static', 'archivos', 'nominas', nombre_archivo)
            resp = send_file(url_File, as_attachment=True)
            return resp

    return render_template('nomina_certificados/templates/nominas.html',  nomina=nomina, nomina_usuario=nomina_usuario)


@app.route('/nomina_certificados/', methods=['GET', 'POST'])
def verNominaCertificadosUsuario():
    if not 'login' in session:
        return redirect('/')

    basepath = os.path.dirname(__file__)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT certificados.*, general_users.Nombre AS nombre_sube, general_users.Apellido AS apellido_sube FROM certificados LEFT JOIN general_users ON certificados.usuario_sube_certificado = general_users.usuario WHERE id_usuario_fk = %s;", session["usuario"])
    certificado = cursor.fetchall()
    cursor.execute(
        "SELECT nominas.*, general_users.Nombre AS nombre_sube, general_users.Apellido AS apellido_sube FROM nominas LEFT JOIN general_users ON nominas.usuario_sube_nomina = general_users.usuario WHERE id_usuario_fk = %s;", session["usuario"])
    nomina = cursor.fetchall()
    cursor.execute('SELECT usuario FROM general_users WHERE id_cargo_fk = 1')
    usuariosRH = cursor.fetchall()
    conexion.commit()

    if 'descargar_nomina' in request.form:
        nombre_archivo = request.form['descargar_nomina']
        url_File = os.path.join(
            basepath, '..', '..', 'static', 'archivos', 'nominas', nombre_archivo)
        resp = send_file(url_File, as_attachment=True)
        return resp
    if 'descargar_certificado' in request.form:
        nombre_archivo = request.form['descargar_certificado']
        url_File = os.path.join(
            basepath, '..', '..', 'static', 'archivos', 'certificados', nombre_archivo)
        resp = send_file(url_File, as_attachment=True)
        return resp

    if request.method == 'POST':

        if 'solicitar_certificado' in request.form:
            print(generarID())
            id_certificado = generarID()
            tipo_certificado = request.form['tipo_certificado']
            nombre_certificado = request.form['nombre_certificado']
            motivo_solicitud = request.form['motivo_solicitud']
            solicitante = session["usuario"]
            tipo_notificacion = 'Certificado'
            mensaje = 'Ha solicitado una nueva petición de Certificado'
            fecha_solicitud =fecha_actualCO().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO solicitud_certificado (id_solicitud,tipo_certificado, nombre_certificado, solicitante, fecha_solicitud ,motivo) VALUES (%s, %s, %s,%s,%s,%s)"
            params = [id_certificado, tipo_certificado, nombre_certificado,
                      solicitante, fecha_solicitud, motivo_solicitud]
            cursor.execute(query, params)

            for usuariosRH in usuariosRH:
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, usuariosRH[0],
                          id_certificado, solicitante, mensaje, fecha_solicitud]
                cursor.execute(query, params)
                conexion.commit()
            flash('Solicitud de certificado realizada.', 'correcto')
            return redirect('/nomina_certificados/')

        if 'cancelar_certificado' in request.form:
            certificadoCancelar = request.form['cancelar_certificado']
            cursor.execute(
                "DELETE FROM solicitud_certificado WHERE id_solicitud=%s;", certificadoCancelar)
            conexion.commit()
            flash('Solicitud de certificado cancelada.', 'correcto')

            return redirect('/nomina_certificados/')

        if 'solicitar_nomina' in request.form:
            id_nomina = generarID()
            mensaje = 'Ha solicitado una nueva petición de Nomina'
            tipo_notificacion = 'Nomina'
            solicitante = session["usuario"]
            nombre_nomina = request.form['nombre_nomina']
            fecha_solicitud =fecha_actualCO().strftime('%Y-%m-%d %H:%M:%S')
            motivo_solicitud = request.form['motivo_solicitud']
            query = "INSERT INTO solicitud_nomina (id_solicitud_nomina,nombre_nomina, solicitante, fecha_solicitud ,motivo_solicitud) VALUES (%s,%s,%s,%s,%s)"
            params = [id_nomina, nombre_nomina, solicitante,
                      fecha_solicitud, motivo_solicitud]
            cursor.execute(query, params)
            for usuariosRH in usuariosRH:
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, usuariosRH[0],
                          id_nomina, solicitante, mensaje, fecha_solicitud]
                cursor.execute(query, params)
                conexion.commit()
            flash('Solicitud de nomina realizada.', 'correcto')
            return redirect('/nomina_certificados/')

        if 'cancelar_nomina' in request.form:
            nominaCancelar = request.form['cancelar_nomina']
            cursor.execute(
                "DELETE FROM solicitud_nomina WHERE id_solicitud_nomina=%s;", nominaCancelar)
            conexion.commit()
            flash('Solicitud de nomina cancelada.', 'correcto')
            return redirect('/nomina_certificados/')

    cursor.execute(
        "SELECT solicitud_certificado.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.resuelto_por = general_users.usuario WHERE solicitante = %s ORDER BY fecha_solicitud DESC ;", session["usuario"])
    solicitudesCertificado = cursor.fetchall()
    cursor.execute(
        "SELECT solicitud_nomina.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.resuelto_por = general_users.usuario WHERE solicitante = %s ORDER BY fecha_solicitud DESC ;", session["usuario"])
    solicitudesNomina = cursor.fetchall()
    conexion.commit()

    return render_template('nomina_certificados/templates/nominas_certificados_usuario.html', nomina=nomina, certificado=certificado, solicitudesCertificado=solicitudesCertificado, solicitudesNomina=solicitudesNomina)
