import datetime as dt
import json
import os
from datetime import datetime, time, timedelta
from random import sample

import bcrypt
from dateutil.relativedelta import relativedelta
from flask import (flash, g, redirect, render_template, request, send_file,
                   send_from_directory, session, url_for)
from werkzeug.utils import secure_filename

from main.run import (agregar_tiempo_transcurrido, app, generarID, mysql,
                      stringAleatorio, fecha_actualCO)
from main.templates.calendario import (avisos, calendario, cursos, noticias,
                                       proyectos)
from main.templates.error import error
from main.templates.infoUsuario import usuario
from main.templates.inventario import inventario
from main.templates.login import login
from main.templates.miTrabajo import miTrabajo
from main.templates.nomina_certificados import nomina_certificado
from main.templates.register import register
from main.templates.usersCRUD import usersCRUD


@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect('/')


url_inicio = '/inicio'


@app.before_request
def notificacionesRH():
    if not 'login' in session:
        return
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT general_users.Nombre, general_users.Apellido, general_users.foto, cargos.nombre_cargo, general_users.usuario_trello, general_users.usuario_slack FROM general_users LEFT JOIN usuario_cargo ON general_users.id = usuario_cargo.id_usuario_fk LEFT JOIN cargos ON usuario_cargo.id_cargo_fk = cargos.id_cargo WHERE usuario= %s;", session['usuario'])
    usuario_base = cursor.fetchone()

    cursor.execute("SELECT notificaciones.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM notificaciones LEFT JOIN general_users ON notificaciones.creador_solicitud= general_users.usuario WHERE id_usuario= %s and estado_notificacion= %s ORDER BY fecha_notificacion DESC;",
                   (session['usuario'], "No visto"))
    notificaciones = cursor.fetchall()

    conexion.commit()
    solicitudes_total_count = len(notificaciones)

    if 'ver_notificacion_nomina' in request.form:
        tipo_notificacion=request.form['tipo_notificacion']
        id_solicitud=request.form['id_solicitud']
        estado_notificacion = "Visto"
        query = "UPDATE notificaciones SET estado_notificacion = %s WHERE id_solicitud = %s"
        params = [estado_notificacion, id_solicitud]
        print(query, params)
        cursor.execute(query, params)
        conexion.commit()
        return redirect(f'/allNotificaciones/{tipo_notificacion}/{id_solicitud}')
    
    notificaciones_con_tiempo = agregar_tiempo_transcurrido(notificaciones, 6)
    g.usuario_base = usuario_base
    g.solicitudes_total_count = solicitudes_total_count
    g.notificaciones = notificaciones_con_tiempo


@app.route('/allNotificaciones/<tipo_solicitud>/<id_solicitud>', methods=['GET', 'POST'])
def allNotificaciones(tipo_solicitud, id_solicitud):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    print(id_solicitud)
    persona_resuelve_solicitud = session['usuario']
    fechaResolucion = datetime.now()

    if tipo_solicitud == "Nomina":
        if session['cargo'] != 1 and session['cargo'] != 0:
            return redirect('/miCartelera')
        cursor.execute("SELECT solicitud_nomina.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.solicitante = general_users.usuario WHERE id_solicitud_nomina=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_nomina = cursor.fetchall()
        conexion.commit()
        print(solicitudes_nomina)
        print(tipo_solicitud)

        if request.method == 'POST':
            if 'aceptarSolicitudNomina' in request.form:
                id_solicitud = request.form['aceptarSolicitudNomina']
                user_nomina = request.form['user_nomina']
                comentarioSolicitudNomina = request.form['comentarioSolicitudNomina']
                estado_solicitud = "Completado"
                tipo_notificacion = 'Nomina'
                mensaje = 'Ha solucionado su petición de Nómina'
                query = "UPDATE solicitud_nomina SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s,resuelto_por=%s WHERE id_solicitud_nomina = %s"
                params = [estado_solicitud, fechaResolucion,
                          comentarioSolicitudNomina, persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_nomina, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/nominas/{user_nomina}')
            if 'rechazarSolicitudNomina' in request.form:
                id_solicitud = request.form['rechazarSolicitudNomina']
                comentarioSolicitudNomina = request.form['comentarioSolicitudNomina']
                estado_solicitud = "Rechazado"
                tipo_notificacion = 'Nomina'
                mensaje = 'Ha rechazado su petición de Nómina'
                user_nomina = request.form['user_nomina']
                mensaje = 'Ha rechazado su petición de Nómina'
                query = "UPDATE solicitud_nomina SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,resuelto_por=%s WHERE id_solicitud_nomina = %s"
                params = [estado_solicitud, fechaResolucion,
                          comentarioSolicitudNomina, persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_nomina, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                return redirect('/nomina_certificados')
        return render_template("templates/light/verNotificaciones.html", solicitudes_nomina=solicitudes_nomina[0], tipo_solicitud=tipo_solicitud)
    elif tipo_solicitud == "Vacaciones":
        if session['cargo'] != 1 and session['cargo'] != 0:
            return redirect('/miCartelera')
        query = "SELECT vacaciones_extemporaneas.*, DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio, DATE_FORMAT(fecha_fin, %s) AS fecha_fin, general_users.Nombre, general_users.Apellido, general_users.foto FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.id_usuario = general_users.usuario WHERE id_vacaciones_extemporaneas = %s ORDER BY fecha_solicitud DESC;"
        cursor.execute(query, ('%d-%M-%Y', '%d-%M-%Y', id_solicitud))
        solicitudes_va_extemporaneas = cursor.fetchall()
        print(solicitudes_va_extemporaneas)
        print(tipo_solicitud)
        if request.method == 'POST':
            if 'aceptarSolicitudVacaciones' in request.form:
                id_solicitud = request.form['aceptarSolicitudVacaciones']
                user_vacaiones = request.form['user_vacaciones']
                dias_extemporanea = request.form['dias_extemporanea']
                tipo_vacaciones = request.form['tipo_vacaciones']
                comentarioSolicitudVacaciones = request.form['comentarioSolicitudVacaciones']
                estado_solicitud = "Aceptado"
                tipo_notificacion = 'Vacaciones'
                mensaje = 'Ha solucionado su petición de Vacaciones'
                cursor.execute(
                    'SELECT dias_restantes FROM vacaciones WHERE id_usuario=%s', user_vacaiones)
                dias_actuales = cursor.fetchone()
                dias_restantes = dias_actuales[0]-int(dias_extemporanea)
                query = "UPDATE vacaciones SET dias_restantes=%s WHERE id_usuario = %s"
                params = [dias_restantes, user_vacaiones]
                cursor.execute(query, params)
                query = "UPDATE vacaciones_extemporaneas SET tipo_vacaciones=%s,estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_aprueba=%s WHERE id_vacaciones_extemporaneas = %s"
                params = [tipo_vacaciones, estado_solicitud, fechaResolucion,
                          comentarioSolicitudVacaciones, persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_vacaiones, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()

                flash('Respuesta a solicitud realizada correctamente', 'correcto')
                return redirect("/vacaciones")
            if 'rechazarSolicitudVacaciones' in request.form:
                tipo_vacaciones = request.form['tipo_vacaciones']
                id_solicitud = request.form['rechazarSolicitudVacaciones']
                comentarioSolicitudVacaciones = request.form['comentarioSolicitudVacaciones']
                estado_solicitud = "Rechazado"
                tipo_notificacion = 'Vacaciones'
                user_vacaiones = request.form['user_vacaciones']
                mensaje = 'Ha rechazado su petición de Vacaciones'
                query = "UPDATE vacaciones_extemporaneas SET tipo_vacaciones=%s,estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_aprueba=%s WHERE id_vacaciones_extemporaneas = %s"
                params = [tipo_vacaciones, estado_solicitud, fechaResolucion,
                          comentarioSolicitudVacaciones, persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_vacaiones, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                flash('Respuesta a solicitud realizada correctamente', 'correcto')
                return redirect("/vacaciones")

        return render_template("templates/light/verNotificaciones.html", solicitudes_va_extemporaneas=solicitudes_va_extemporaneas[0], tipo_solicitud=tipo_solicitud)
    elif tipo_solicitud == "Certificado":
        if session['cargo'] != 1 and session['cargo'] != 0:
            return redirect('/miCartelera')
        cursor.execute("SELECT solicitud_certificado.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.solicitante = general_users.usuario WHERE id_solicitud=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_certificado = cursor.fetchall()
        conexion.commit()
        print(solicitudes_certificado)
        print(tipo_solicitud)
        print("ttttttttt")
        if request.method == 'POST':
            if 'aceptarSolicitudCertificado' in request.form:
                id_solicitud = request.form['aceptarSolicitudCertificado']
                user_certificate = request.form['user_certificate']
                tipo_notificacion = 'Certificado'
                mensaje = 'Ha solucionado su petición de Certificado'
                comentarioSolicitudCertificado = request.form['comentarioSolicitudCertificado']
                estado_solicitud = "Completado"
                query = "UPDATE solicitud_certificado SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario_solicitud=%s,resuelto_por=%s WHERE id_solicitud = %s"
                params = [estado_solicitud, fechaResolucion,
                          comentarioSolicitudCertificado, persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_certificate, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()

                print("GGGGGGG333333GGGGGGG")
                return redirect(f'/certificados/{user_certificate}')
            if 'rechazarSolicitudCertificado' in request.form:
                id_solicitud = request.form['rechazarSolicitudCertificado']
                comentarioSolicitudCertificado = request.form['comentarioSolicitudCertificado']
                estado_solicitud = "Rechazado"
                user_certificate = request.form['user_certificate']
                tipo_notificacion = 'Certificado'
                mensaje = 'Ha rechazado su petición de Certificado'
                query = "UPDATE solicitud_certificado SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario_solicitud=%s,resuelto_por=%s WHERE id_solicitud = %s"
                params = [estado_solicitud, fechaResolucion,
                          comentarioSolicitudCertificado, persona_resuelve_solicitud, id_solicitud]

                cursor.execute(query, params)
                conexion.commit()

                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_certificate, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                return redirect('/nomina_certificados')
            else:
                print('No Entró')
        else:
            print("no entro primer if")
        return render_template("templates/light/verNotificaciones.html", solicitudes_certificado=solicitudes_certificado[0],
                               tipo_solicitud=tipo_solicitud)
    elif tipo_solicitud == "Permiso":
        if session['cargo'] != 1 and session['cargo'] != 0:
            return redirect('/miCartelera')
        query = "SELECT solicitud_permisos.*, DATE_FORMAT(fecha_inicio_permiso, %s) AS fecha_permiso, DATE_FORMAT(fecha_fin_permiso, %s) AS fecha_fin_permiso, DATE_FORMAT(fecha_inicio_recuperacion, %s) AS fecha_inicio_recuperacion, DATE_FORMAT(fecha_fin_recuperacion, %s) AS fecha_fin_recuperacion, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.id_usuario = general_users.usuario WHERE id_permisos=%s ORDER BY fecha_solicitud DESC;"
        cursor.execute(query, ('%d-%M-%Y', '%d-%M-%Y',
                       '%d-%b-%Y %H:%i %p', '%d-%b-%Y %H:%i %p', id_solicitud))
        solicitudes_permiso = cursor.fetchall()
        conexion.commit()
        print(solicitudes_permiso)
        if request.method == 'POST':
            if 'aceptarSolicitudPermiso' in request.form:

                comentarioSolicitudRecuperar = request.form['comentarioSolicitudRecuperar']
                user_permiso = request.form['user_permiso']
                mensaje = 'Ha solucionado su petición de Permiso'
                estado_solicitud = "Aceptado"
                tipo_notificacion = 'Permiso'
                query = "UPDATE solicitud_permisos SET estado_solicitud = %s ,fecha_resolucion=%s ,observaciones=%s,persona_aprueba=%s WHERE id_permisos = %s"
                params = [estado_solicitud, fechaResolucion, comentarioSolicitudRecuperar,
                          persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()

                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_permiso, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                flash('Respuesta realizada correctamente', 'correcto')
                return redirect(f'/allNotificaciones/Permiso/{id_solicitud}')

            if 'rechazarSolicitudPermiso' in request.form:
                comentarioSolicitudRecuperar = request.form['comentarioSolicitudRecuperar']
                estado_solicitud = "Rechazado"
                user_permiso = request.form['user_permiso']
                tipo_notificacion = 'Permiso'
                mensaje = 'Ha solucionado su petición de Permiso'
                query = "UPDATE solicitud_permisos SET estado_solicitud = %s ,fecha_resolucion=%s ,observaciones=%s,persona_aprueba=%s WHERE id_permisos = %s"
                params = [estado_solicitud, fechaResolucion,
                          comentarioSolicitudRecuperar, persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_permiso, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                flash('Respuesta realizada correctamente', 'correcto')
                return redirect(f'/allNotificaciones/Permiso/{id_solicitud}')

        return render_template("templates/light/verNotificaciones.html", solicitudes_permiso=solicitudes_permiso[0], tipo_solicitud=tipo_solicitud)
    elif tipo_solicitud == "Permiso_Empresa":
        if session['cargo'] != 1 and session['cargo'] != 0:
            return redirect('/miCartelera')
        query = "SELECT solicitud_permiso_extra.*, DATE_FORMAT(fecha_inicio, %s) AS fecha_permiso, DATE_FORMAT(fecha_fin, %s) AS fecha_fin_permiso, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permiso_extra LEFT JOIN general_users ON solicitud_permiso_extra.id_usuario = general_users.usuario WHERE id_extra=%s ORDER BY fecha_solicitud DESC;"
        cursor.execute(query, ('%d-%M-%Y %H:%i %p', '%d-%M-%Y %H:%i %p', id_solicitud))
        solicitudes_permiso = cursor.fetchall()
        conexion.commit()
        print(solicitudes_permiso)
        if request.method == 'POST':
            if 'aceptarSolicitudPermisoEX' in request.form:

                comentarioSolicitudRecuperar = request.form['comentarioSolicitudRecuperar']
                user_permiso = request.form['user_permiso']
                mensaje = 'Ha solucionado su petición de Permiso'
                estado_solicitud = "Aceptado"
                tipo_notificacion = 'Permiso_Empresa'
                query = "UPDATE solicitud_permiso_extra SET estado_solicitud = %s ,fecha_resolucion=%s ,observaciones=%s,resuelto_por=%s WHERE id_extra = %s"
                params = [estado_solicitud, fechaResolucion, comentarioSolicitudRecuperar,
                          persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()

                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_permiso, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                flash('Respuesta realizada correctamente', 'correcto')
                return redirect(f'/allNotificaciones/Permiso_Empresa/{id_solicitud}')

            if 'rechazarSolicitudPermisoEX' in request.form:
                comentarioSolicitudRecuperar = request.form['comentarioSolicitudRecuperar']
                estado_solicitud = "Rechazado"
                user_permiso = request.form['user_permiso']
                tipo_notificacion = 'Permiso_Empresa'
                mensaje = 'Ha solucionado su petición de Permiso'
                query = "UPDATE solicitud_permiso_extra SET estado_solicitud = %s ,fecha_resolucion=%s ,observaciones=%s,resuelto_por=%s WHERE id_extra = %s"
                params = [estado_solicitud, fechaResolucion,
                          comentarioSolicitudRecuperar, persona_resuelve_solicitud, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_permiso, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                flash('Respuesta realizada correctamente', 'correcto')
                return redirect(f'/allNotificaciones/Permiso_Empresa/{id_solicitud}')

        return render_template("templates/light/verNotificaciones.html", solicitudes_permiso=solicitudes_permiso[0], tipo_solicitud=tipo_solicitud)

    elif tipo_solicitud == "Inventario":
        cursor.execute("SELECT movimientos.*, general_users.Nombre, general_users.Apellido, general_users.foto , inventario.* FROM movimientos LEFT JOIN general_users ON movimientos.responsable = general_users.usuario LEFT JOIN inventario ON movimientos.id_elemento=inventario.id_elemento WHERE id_movimiento=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_inventario = cursor.fetchall()
        conexion.commit()
        print(solicitudes_inventario)
        if request.method == 'POST':
            if 'aceptarSolicitudInventario' in request.form:
                tipo_notificacion = 'Inventario'
                mensaje = 'Ha solucionado su petición de Inventario'
                user_inventario = request.form['user_inventario']
                observaciones = request.form['comentarioSolicitudInventario']
                estado_solicitud = "Aceptado"
                query = "UPDATE movimientos SET  persona_aprueba = %s ,fecha_movimiento=%s ,estado_solicitud=%s ,observaciones=%s WHERE id_movimiento = %s"
                params = [persona_resuelve_solicitud, fechaResolucion,
                          estado_solicitud, observaciones, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_inventario, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                flash('Respuesta realizada correctamente', 'correcto')
                return redirect(f'/allNotificaciones/Inventario/{id_solicitud}')

            if 'rechazarSolicitudInventario' in request.form:
                tipo_notificacion = 'Inventario'
                mensaje = 'Ha rechazado su petición de Inventario'
                user_inventario = request.form['user_inventario']
                observaciones = request.form['comentarioSolicitudInventario']
                estado_solicitud = "Rechazado"
                query = "UPDATE movimientos SET  persona_aprueba = %s ,fecha_movimiento=%s ,estado_solicitud=%s ,observaciones=%s WHERE id_movimiento = %s"
                params = [persona_resuelve_solicitud, fechaResolucion,
                          estado_solicitud, observaciones, id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                params = [generarID(), tipo_notificacion, user_inventario, id_solicitud,
                          persona_resuelve_solicitud, mensaje, fechaResolucion]
                cursor.execute(query, params)
                conexion.commit()
                flash('Respuesta realizada correctamente', 'correcto')
                return redirect(f'/allNotificaciones/Inventario/{id_solicitud}')
        return render_template("templates/light/verNotificaciones.html", solicitudes_inventario=solicitudes_inventario[0], tipo_solicitud=tipo_solicitud)
    elif tipo_solicitud == "Reporte":
        return redirect('/miCartelera')
    else:
        # Si el tipo de solicitud no es reconocido, se redirige al usuario a una página de error o a otra acción
        return "Tipo de solicitud no reconocido"


@app.route('/inicio')
def inicio():
    if not 'login' in session:
        return redirect('/')
    fecha_actual = datetime.now()
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT cursos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM cursos LEFT JOIN general_users ON cursos.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosCursos = cursor.fetchall()
    conexion.commit()
    cursos_con_tiempo = agregar_tiempo_transcurrido(datosCursos, 5)

    cursor.execute("SELECT noticias.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM noticias LEFT JOIN general_users ON noticias.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosNoticias = cursor.fetchall()
    conexion.commit()
    noticias_con_tiempo = agregar_tiempo_transcurrido(datosNoticias, 4)

    cursor.execute("SELECT avisos.*,DATE_FORMAT(fecha_publicacion, '%d-%m-%Y') AS fecha_publicacion, general_users.Nombre, general_users.Apellido, general_users.foto FROM avisos LEFT JOIN general_users ON avisos.usuario_publica = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosAvisos = cursor.fetchall()

    # Eliminar cuando se agregue correctamente en la base de datos
    cursor.execute("SELECT * FROM cursos WHERE fecha_fin < %s",
                   (fecha_actual,))
    datos_a_eliminar = cursor.fetchall()
    for dato in datos_a_eliminar:
        cursor.execute("DELETE FROM cursos WHERE id_curso = %s", (dato[0],))
    fecha_limite = fecha_actual - dt.timedelta(days=6 * 30)
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM noticias WHERE fecha_publicacion < %s", (fecha_limite,))
    conexion.commit()
    avisos_con_tiempo = agregar_tiempo_transcurrido(datosAvisos, 3)
    return render_template('templates/light/index.html', datosCursos=cursos_con_tiempo, datosNoticias=noticias_con_tiempo, datosAvisos=avisos_con_tiempo)


@app.route('/miCartelera')
def miCartelera():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT inscripcion_cursos.*, cursos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM inscripcion_cursos LEFT JOIN general_users ON inscripcion_cursos.id_usuario_fk = general_users.usuario LEFT JOIN cursos ON inscripcion_cursos.id_curso_fk = cursos.id_curso WHERE inscripcion_cursos.id_usuario_fk =%s ORDER BY fecha_inscripcion_curso DESC;", session['usuario'])
    cursosInscritos = cursor.fetchall()

    query = "SELECT reportes_inventario.*, DATE_FORMAT(fecha_reporte, %s) AS fecha_reporte,inventario.nombre_elemento, general_users.Nombre, general_users.Apellido FROM reportes_inventario LEFT JOIN general_users ON reportes_inventario.reportado_por = general_users.usuario LEFT JOIN inventario ON reportes_inventario.elemento_entregado = inventario.id_elemento"
    cursor.execute(query, ('%d %M %Y %h:%i %p'))
    reportes_inventario = cursor.fetchall()

    query = "SELECT solicitud_certificado.nombre_certificado,DATE_FORMAT(fecha_solicitud, %s) AS fecha_solicitud,solicitud_certificado.estado_solicitud,solicitud_certificado.comentario_solicitud,DATE_FORMAT(fecha_resolucion, %s) AS fecha_resolucion,solicitud_certificado.resuelto_por, general_users.Nombre, general_users.Apellido FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.resuelto_por = general_users.usuario WHERE solicitante=%s;"
    cursor.execute(query, ('%d %M %Y %h:%i %p',
                   '%d %M %Y %h:%i %p', session['usuario']))
    solicitudes_certificado = cursor.fetchall()

    query = "SELECT solicitud_nomina.nombre_nomina,DATE_FORMAT(fecha_solicitud, %s) AS fecha_solicitud,solicitud_nomina.estado_solicitud,solicitud_nomina.comentario,DATE_FORMAT(fecha_resolucion, %s) AS fecha_resolucion,solicitud_nomina.resuelto_por, general_users.Nombre, general_users.Apellido FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.resuelto_por = general_users.usuario WHERE solicitante=%s;"
    cursor.execute(query, ('%d %M %Y %h:%i %p',
                   '%d %M %Y %h:%i %p', session['usuario']))
    solicitudes_nomina = cursor.fetchall()

    query = "SELECT solicitud_permisos.motivo_permiso,DATE_FORMAT(fecha_solicitud, %s) AS fecha_solicitud,solicitud_permisos.estado_solicitud,solicitud_permisos.observaciones,DATE_FORMAT(fecha_resolucion, %s) AS fecha_resolucion,solicitud_permisos.persona_aprueba, general_users.Nombre, general_users.Apellido FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.persona_aprueba = general_users.usuario WHERE id_usuario=%s;"
    cursor.execute(query, ('%d %M %Y %h:%i %p',
                   '%d %M %Y %h:%i %p', session['usuario']))
    solicitudes_permiso = cursor.fetchall()

    query = "SELECT DATE_FORMAT(fecha_solicitud, %s) AS fecha_solicitud,vacaciones_extemporaneas.estado_solicitud,vacaciones_extemporaneas.comentario,DATE_FORMAT(fecha_resolucion, %s) AS fecha_resolucion,vacaciones_extemporaneas.persona_aprueba, general_users.Nombre, general_users.Apellido FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.persona_aprueba = general_users.usuario WHERE id_usuario=%s;"
    cursor.execute(query, ('%d %M %Y %h:%i %p',
                   '%d %M %Y %h:%i %p', session['usuario']))
    solicitudes_vacaciones = cursor.fetchall()

    query = "SELECT DATE_FORMAT(fecha_solicitud, %s) AS fecha_solicitud,solicitud_permiso_extra.estado_solicitud,solicitud_permiso_extra.observaciones,DATE_FORMAT(fecha_resolucion, %s) AS fecha_resolucion,solicitud_permiso_extra.resuelto_por, general_users.Nombre, general_users.Apellido FROM solicitud_permiso_extra LEFT JOIN general_users ON solicitud_permiso_extra.resuelto_por = general_users.usuario WHERE id_usuario=%s;"
    cursor.execute(query, ('%d %M %Y %h:%i %p',
                   '%d %M %Y %h:%i %p', session['usuario']))
    solicitud_permiso_extra = cursor.fetchall()
    conexion.commit()
    cursos_con_tiempo = agregar_tiempo_transcurrido(cursosInscritos, 11)

    return render_template('templates/light/miCartelera.html', datosCursos=cursos_con_tiempo, reportes_inventario=reportes_inventario, solicitudes_certificado=solicitudes_certificado, solicitudes_nomina=solicitudes_nomina, solicitudes_permiso=solicitudes_permiso, solicitudes_vacaciones=solicitudes_vacaciones,solicitud_permiso_extra=solicitud_permiso_extra)


@app.route('/Noticias')
def noticiass():
    if not 'login' in session:
        return redirect('/')
    return render_template('sitio/Noticias.html')


@app.route('/static/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/ver_archivo/<tipo_archivo>/<path:nombre_archivo>')
def ver_imagen(tipo_archivo, nombre_archivo):
    if not 'login' in session:
        return redirect('/')
    if tipo_archivo == "inventario":
        ruta_archivo = os.path.join(
            app.root_path, 'static', 'images', 'inventario', nombre_archivo)
    elif tipo_archivo == "Certificado":
        ruta_archivo = os.path.join(
            app.root_path, 'static', 'archivos', 'certificados', nombre_archivo)
    elif tipo_archivo == "Nomina":
        ruta_archivo = os.path.join(
            app.root_path, 'static', 'archivos', 'nominas', nombre_archivo)
    else:
        # Si el tipo de solicitud no es reconocido, se redirige al usuario a una página de error o a otra acción
        return "Tipo de solicitud no reconocido"
    return send_file(ruta_archivo)


@app.route('/url_pruebas')
def url_pruebas():
    return render_template('calendario/calendarioInterac.html')
