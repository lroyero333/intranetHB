from random import sample
from flask import request, redirect, send_file, send_from_directory
import os
import json
from flask import render_template, redirect, request, url_for, session, flash, g
import bcrypt
from werkzeug.utils import secure_filename
from main.run import app, mysql
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from main.templates.login import login
from main.templates.register import register
from main.templates.calendario import calendario
from main.templates.error import error
from main.templates.nomina_certificados import nomina_certificado
from main.templates.usersCRUD import usersCRUD
from main.templates.infoUsuario import usuario


def stringAleatorio():
    string_aleatorio="0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud=10
    secuencia=string_aleatorio.upper()
    resultado_aleatorio= sample(secuencia, longitud)
    string_aleatorio= "".join(resultado_aleatorio)
    return string_aleatorio

@app.route('/cerrar')
def cerrar():
    session.clear()
    return redirect('/')


url_inicio = '/inicio'


@app.route('/notificaciones', methods=['GET','POST'])
def notificaciones():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT solicitud_certificado.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.solicitante = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_certificado = cursor.fetchall()
    cursor.execute("SELECT solicitud_nomina.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.solicitante = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_nomina = cursor.fetchall()
    conexion.commit()
    persona_resuelve_solicitud=session['usuario']
    fechaResolucion=datetime.now()
    if request.method == 'POST':
       
        if 'aceptarSolicitudCertificado' in request.form:
            
            id_solicitud=request.form['aceptarSolicitudCertificado']
            comentarioSolicitudCertificado=request.form['comentarioSolicitudCertificado']
            estado_solicitud = "Completado"
            query = "UPDATE solicitud_certificado SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario_solicitud=%s,persona_resuelve_solicitud=%s WHERE id_solicitud = %s"
            params = [estado_solicitud, fechaResolucion,comentarioSolicitudCertificado,persona_resuelve_solicitud,id_solicitud]
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/nomina_certificados')
        if 'rechazarSolicitudCertificado' in request.form:
            
            id_solicitud=request.form['rechazarSolicitudCertificado']
            comentarioSolicitudCertificado=request.form['comentarioSolicitudCertificado']
            estado_solicitud = "Rechazado"
            
            query = "UPDATE solicitud_certificado SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario_solicitud=%s,persona_resuelve_solicitud=%s WHERE id_solicitud = %s"
            params = [estado_solicitud, fechaResolucion,comentarioSolicitudCertificado,persona_resuelve_solicitud,id_solicitud]
            
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/notificaciones')
        if 'aceptarSolicitudNomina' in request.form:
            
            id_solicitud=request.form['aceptarSolicitudNomina']
            comentarioSolicitudNomina=request.form['comentarioSolicitudNomina']
            estado_solicitud = "Completado"
            
            query = "UPDATE solicitud_nomina SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s,persona_resuelve_solicitud=%s WHERE id_solicitud_nomina = %s"
            params = [estado_solicitud, fechaResolucion,comentarioSolicitudNomina,persona_resuelve_solicitud,id_solicitud]
            
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/nomina_certificados')
        if 'rechazarSolicitudNomina' in request.form:
            
            id_solicitud=request.form['rechazarSolicitudNomina']
            comentarioSolicitudNomina=request.form['comentarioSolicitudNomina']
            estado_solicitud = "Rechazado"
            query = "UPDATE solicitud_nomina SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_resuelve_solicitud=%s WHERE id_solicitud_nomina = %s"
            params = [estado_solicitud, fechaResolucion,comentarioSolicitudNomina,persona_resuelve_solicitud,id_solicitud]
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/notificaciones')
        if 'aceptarSolicitudVacaciones' in request.form:
            
            id_solicitud=request.form['aceptarSolicitudVacaciones']
            tipo_vacaciones=request.form['tipo_vacaciones']
            comentarioSolicitudVacaciones=request.form['comentarioSolicitudVacaciones']
            estado_solicitud = "Aceptado"
            query = "UPDATE vacaciones_extemporaneas SET tipo_vacaciones=%s,estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_aprueba=%s WHERE id_vacaciones_extemporaneas = %s"
            params = [tipo_vacaciones,estado_solicitud, fechaResolucion,comentarioSolicitudVacaciones,persona_resuelve_solicitud,id_solicitud]
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/notificaciones')
        if 'rechazarSolicitudVacaciones' in request.form:
            tipo_vacaciones=request.form['tipo_vacaciones']
            id_solicitud=request.form['rechazarSolicitudVacaciones']
            comentarioSolicitudVacaciones=request.form['comentarioSolicitudVacaciones']
            estado_solicitud = "Rechazado"
            query = "UPDATE vacaciones_extemporaneas SET tipo_vacaciones=%s,estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_aprueba=%s WHERE id_vacaciones_extemporaneas = %s"
            params = [tipo_vacaciones,estado_solicitud, fechaResolucion,comentarioSolicitudVacaciones,persona_resuelve_solicitud,id_solicitud]
            cursor.execute(query, params)
            conexion.commit()
            return redirect('/notificaciones')
     
    return render_template('templates/light/verNotificaciones.html',  solicitudes_certificado=solicitudes_certificado,solicitudes_nomina=solicitudes_nomina)

@app.before_request
def notificacionesRH():
    if not 'login' in session:
        return

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT solicitud_certificado.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.solicitante = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_certificado = cursor.fetchall()
    cursor.execute("SELECT solicitud_nomina.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.solicitante = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_nomina = cursor.fetchall()

    cursor.execute("SELECT vacaciones_extemporaneas.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.id_usuario = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_va_extemporaneas = cursor.fetchall()

    cursor.execute("SELECT * FROM solicitud_certificado WHERE estado_notificacion= %s;","No visto")
    notificacion_certificado = cursor.fetchall()
    cursor.execute("SELECT * FROM solicitud_nomina WHERE estado_notificacion= %s;","No visto")
    notificacion_nomina = cursor.fetchall()
    cursor.execute("SELECT * FROM vacaciones_extemporaneas WHERE estado_notificacion= %s;","No visto")
    notificacion_vacaciones = cursor.fetchall()
    conexion.commit()
   
    solicitudes_total = notificacion_certificado + notificacion_nomina+ notificacion_vacaciones
    solicitudes_total_count = len(solicitudes_total)

    certificadooss_con_tiempo = []
    fecha_actual = datetime.now()
    for certificadoos in solicitudes_certificado:
        fecha_insertado = certificadoos[4]
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
        certificadoos_con_tiempo = list(certificadoos)
        certificadoos_con_tiempo.append(tiempo_transcurrido)
        certificadooss_con_tiempo.append(certificadoos_con_tiempo)

    nominaas_con_tiempo = []
    
    for nominas in solicitudes_nomina:
        fecha_insertado = nominas[3]
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
        nominas_con_tiempo = list(nominas)
        nominas_con_tiempo.append(tiempo_transcurrido)
        nominaas_con_tiempo.append(nominas_con_tiempo)

    vacaciones_con_tiempo = []
    
    for vacaciones in solicitudes_va_extemporaneas:
        fecha_insertado = vacaciones[6]
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
        vacaciones_ex_tiempo = list(vacaciones)
        vacaciones_ex_tiempo.append(tiempo_transcurrido)
        vacaciones_con_tiempo.append(vacaciones_ex_tiempo)

    # Guardamos las solicitudes en la variable de contexto `g`
    g.solicitudes_total_count = solicitudes_total_count
    g.solicitudes_certificado = certificadooss_con_tiempo
    g.solicitudes_nomina=nominaas_con_tiempo
    g.solicitudes_va_extemporaneas=vacaciones_con_tiempo

@app.route('/vistoNotificacionesCertificado/<id_solicitud>', methods=['GET','POST'])
def vistoNotificacionCertificado(id_solicitud):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    print(id_solicitud)
    estado_notificacion = "Visto"
    query = "UPDATE solicitud_certificado SET estado_notificacion = %s WHERE id_solicitud = %s"
    params = [estado_notificacion, id_solicitud]
    print(query, params)
    cursor.execute(query, params)
    conexion.commit()
    
    return redirect('/notificaciones')
    
@app.route('/vistoNotificacionesnNomina/<id_solicitud>', methods=['GET','POST'])
def vistoNotificacionNomina(id_solicitud):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    print(id_solicitud)
    estado_notificacion = "Visto"
    query = "UPDATE solicitud_nomina SET estado_notificacion = %s WHERE id_solicitud_nomina = %s"
    params = [estado_notificacion, id_solicitud]
    print(query, params)
    cursor.execute(query, params)
    conexion.commit()
    return redirect("/notificaciones")

@app.route('/vistoNotificacionesVacaciones/<id_solicitud>', methods=['GET','POST'])
def vistoNotificacionVacaciones(id_solicitud):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    print(id_solicitud)
    estado_notificacion = "Visto"
    query = "UPDATE vacaciones_extemporaneas SET estado_notificacion = %s WHERE id_vacaciones_extemporaneas = %s"
    params = [estado_notificacion, id_solicitud]
    print(query, params)
    cursor.execute(query, params)
    conexion.commit()
    return redirect("/notificaciones")


@app.route('/inicio')
def inicio():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT cursos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM cursos LEFT JOIN general_users ON cursos.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
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

    cursor.execute("SELECT noticias.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM noticias LEFT JOIN general_users ON noticias.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosNoticias = cursor.fetchall()
    conexion.commit()
    noticias_con_tiempo = []
    for noticia in datosNoticias:
        fecha_insertado = noticia[4]
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

@app.route('/ver_archivo/<string:filename>', methods=['GET','POST'])
def ver_archivo(filename):
    if 'ver_certificado':
        ruta_archivo = os.path.join(app.root_path, 'static', 'archivos', 'certificados', filename)
    elif 'ver_nomina':
        directorio_archivos = os.path.abspath(os.path.join(app.root_path, '..', 'static', 'archivos', 'certificados', filename))

    return send_file(ruta_archivo, as_attachment=True)

@app.route('/url_pruebas')
def url_pruebas():
    return render_template('templates/light/app-taskboard.html')