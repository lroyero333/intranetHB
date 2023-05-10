from random import sample
from flask import request, redirect, send_file, send_from_directory
import os
import json
from flask import render_template, redirect, request, url_for, session, flash, g
import bcrypt
from werkzeug.utils import secure_filename
from main.run import app, mysql
import datetime as dt
from datetime import datetime, time, timedelta 
from dateutil.relativedelta import relativedelta
from main.templates.login import login
from main.templates.register import register
from main.templates.calendario import calendario
from main.templates.error import error
from main.templates.nomina_certificados import nomina_certificado
from main.templates.usersCRUD import usersCRUD
from main.templates.infoUsuario import usuario
from main.templates.inventario import inventario
from main.templates.miTrabajo import miTrabajo

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

    cursor.execute("SELECT solicitud_permisos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.id_usuario = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_permisos = cursor.fetchall()

    cursor.execute("SELECT * FROM solicitud_certificado WHERE estado_notificacion= %s;","No visto")
    notificacion_certificado = cursor.fetchall()
    cursor.execute("SELECT * FROM solicitud_nomina WHERE estado_notificacion= %s;","No visto")
    notificacion_nomina = cursor.fetchall()
    cursor.execute("SELECT * FROM vacaciones_extemporaneas WHERE estado_notificacion= %s;","No visto")
    notificacion_vacaciones = cursor.fetchall()
    cursor.execute("SELECT * FROM solicitud_permisos WHERE estado_notificacion= %s;","No visto")
    notificacion_permisos = cursor.fetchall()
    conexion.commit()
   
    solicitudes_total = notificacion_certificado + notificacion_nomina+ notificacion_vacaciones+notificacion_permisos
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

    permisos_con_tiempo = []
    
    for permisos in solicitudes_permisos:
        fecha_insertado = permisos[6]
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
        permisos_ex_tiempo = list(permisos)
        permisos_ex_tiempo.append(tiempo_transcurrido)
        permisos_con_tiempo.append(permisos_ex_tiempo)

    # Guardamos las solicitudes en la variable de contexto `g`
    g.solicitudes_total_count = solicitudes_total_count
    g.solicitudes_certificado = certificadooss_con_tiempo
    g.solicitudes_nomina=nominaas_con_tiempo
    g.solicitudes_va_extemporaneas=vacaciones_con_tiempo
    g.solicitudes_permisos=permisos_con_tiempo

@app.route('/allNotificaciones/<tipo_solicitud>/<id_solicitud>', methods=['GET','POST'])
def allNotificaciones(tipo_solicitud,id_solicitud):
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    print(id_solicitud)
    estado_notificacion = "Visto"

    if tipo_solicitud == "Nomina":
        tabla_solicitud = "solicitud_nomina"
        campo_id_solicitud = "id_solicitud_nomina"
    elif tipo_solicitud == "Vacaciones":
        tabla_solicitud = "vacaciones_extemporaneas"
        campo_id_solicitud = "id_vacaciones_extemporaneas"
    elif tipo_solicitud == "Certificado":
        tabla_solicitud = "solicitud_certificado"
        campo_id_solicitud = "id_solicitud"
    elif tipo_solicitud == "Permiso":
        tabla_solicitud = "solicitud_permisos"
        campo_id_solicitud = "id_permisos"
    else:
        # Si el tipo de solicitud no es reconocido, se redirige al usuario a una página de error o a otra acción
        return "Tipo de solicitud no reconocido"

    query = f"UPDATE {tabla_solicitud} SET estado_notificacion = %s WHERE {campo_id_solicitud} = %s"
    params = [estado_notificacion, id_solicitud]
    print(query, params)
    cursor.execute(query, params)
    conexion.commit()
    persona_resuelve_solicitud=session['usuario']
    fechaResolucion=datetime.now()

    if tipo_solicitud == "Nomina":
        cursor.execute("SELECT solicitud_nomina.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.solicitante = general_users.usuario WHERE id_solicitud_nomina=%s ORDER BY fecha_solicitud DESC;",id_solicitud)
        solicitudes_nomina = cursor.fetchall()
        conexion.commit()
        print(solicitudes_nomina)
        print(tipo_solicitud)
        
        if request.method == 'POST':
            if 'aceptarSolicitudNomina' in request.form:
                print("AAAAAAAAAAAAAAFfFfFfFfFfFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                id_solicitud = request.form['aceptarSolicitudNomina']
                user_nomina = request.form['user_nomina']
                comentarioSolicitudNomina=request.form['comentarioSolicitudNomina']
                estado_solicitud = "Completado"
                query = "UPDATE solicitud_nomina SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s,persona_resuelve_solicitud=%s WHERE id_solicitud_nomina = %s"
                params = [estado_solicitud, fechaResolucion,comentarioSolicitudNomina,persona_resuelve_solicitud,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/nominas/{user_nomina}')
            if 'rechazarSolicitudNomina' in request.form:
                id_solicitud=request.form['rechazarSolicitudNomina']
                comentarioSolicitudNomina=request.form['comentarioSolicitudNomina']
                estado_solicitud = "Rechazado"
                query = "UPDATE solicitud_nomina SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_resuelve_solicitud=%s WHERE id_solicitud_nomina = %s"
                params = [estado_solicitud, fechaResolucion,comentarioSolicitudNomina,persona_resuelve_solicitud,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect('/notificaciones')
        return render_template("templates/light/verNotificaciones.html", solicitudes_nomina=solicitudes_nomina[0],tipo_solicitud=tipo_solicitud)
    
    elif tipo_solicitud == "Vacaciones":
        cursor.execute("SELECT vacaciones_extemporaneas.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.id_usuario = general_users.usuario WHERE id_vacaciones_extemporaneas=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_va_extemporaneas = cursor.fetchall()
        print(solicitudes_va_extemporaneas)
        print(tipo_solicitud)
        
    
        if request.method == 'POST':
            if 'aceptarSolicitudVacaciones' in request.form:
                id_solicitud=request.form['aceptarSolicitudVacaciones']
                tipo_vacaciones=request.form['tipo_vacaciones']
                comentarioSolicitudVacaciones=request.form['comentarioSolicitudVacaciones']
                estado_solicitud = "Aceptado"
                query = "UPDATE vacaciones_extemporaneas SET tipo_vacaciones=%s,estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_aprueba=%s WHERE id_vacaciones_extemporaneas = %s"
                params = [tipo_vacaciones,estado_solicitud, fechaResolucion,comentarioSolicitudVacaciones,persona_resuelve_solicitud,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return render_template("templates/light/verNotificaciones.html", solicitudes_va_extemporaneas=solicitudes_va_extemporaneas[0],tipo_solicitud=tipo_solicitud)
            if 'rechazarSolicitudVacaciones' in request.form:
                tipo_vacaciones=request.form['tipo_vacaciones']
                id_solicitud=request.form['rechazarSolicitudVacaciones']
                comentarioSolicitudVacaciones=request.form['comentarioSolicitudVacaciones']
                estado_solicitud = "Rechazado"
                query = "UPDATE vacaciones_extemporaneas SET tipo_vacaciones=%s,estado_solicitud = %s ,fecha_resolucion=%s ,comentario=%s ,persona_aprueba=%s WHERE id_vacaciones_extemporaneas = %s"
                params = [tipo_vacaciones,estado_solicitud, fechaResolucion,comentarioSolicitudVacaciones,persona_resuelve_solicitud,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return render_template("templates/light/verNotificaciones.html", solicitudes_va_extemporaneas=solicitudes_va_extemporaneas[0],tipo_solicitud=tipo_solicitud)
        
        return render_template("templates/light/verNotificaciones.html", solicitudes_va_extemporaneas=solicitudes_va_extemporaneas[0],tipo_solicitud=tipo_solicitud)

    elif tipo_solicitud == "Certificado":
        cursor.execute("SELECT solicitud_certificado.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.solicitante = general_users.usuario WHERE id_solicitud=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_certificado = cursor.fetchall()
        conexion.commit()
        print(solicitudes_certificado)
        print(tipo_solicitud)
        print("ttttttttt")
        if request.method == 'POST':      
            if 'aceptarSolicitudCertificado' in request.form:
                id_solicitud=request.form['aceptarSolicitudCertificado']
                user_certificate=request.form['user_certificate']
                print(user_certificate)
                comentarioSolicitudCertificado=request.form['comentarioSolicitudCertificado']
                estado_solicitud = "Completado"
                query = "UPDATE solicitud_certificado SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario_solicitud=%s,persona_resuelve_solicitud=%s WHERE id_solicitud = %s"
                params = [estado_solicitud, fechaResolucion,comentarioSolicitudCertificado,persona_resuelve_solicitud,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                print("GGGGGGG333333GGGGGGG")
                return redirect(f'/certificados/{user_certificate}')
            if 'rechazarSolicitudCertificado' in request.form:
                id_solicitud=request.form['rechazarSolicitudCertificado']
                comentarioSolicitudCertificado=request.form['comentarioSolicitudCertificado']
                estado_solicitud = "Rechazado"
                query = "UPDATE solicitud_certificado SET estado_solicitud = %s ,fecha_resolucion=%s ,comentario_solicitud=%s,persona_resuelve_solicitud=%s WHERE id_solicitud = %s"
                params = [estado_solicitud, fechaResolucion,comentarioSolicitudCertificado,persona_resuelve_solicitud,id_solicitud]
            
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
        cursor.execute("SELECT solicitud_permisos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.id_usuario = general_users.usuario WHERE id_permisos=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_permiso = cursor.fetchall()
        conexion.commit()
        print(solicitudes_permiso)
        if request.method == 'POST':
            if 'aceptarSolicitudPermiso' in request.form:
                inicio_dia_recuperar=request.form['inicio_dia_recuperar']
                inicio_hora_recuperar=request.form['inicio_hora_recuperar']
                fin_dia_recuperar=request.form['fin_dia_recuperar']
                fin_hora_recuperar=request.form['fin_hora_recuperar']
                fecha_inicio_recuperar = inicio_dia_recuperar + ' ' + inicio_hora_recuperar
                fecha_hora = dt.datetime.strptime(fecha_inicio_recuperar, '%Y-%m-%d %I:%M %p')
                inicio_recuperar = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
                fecha_fin_recuperar = fin_dia_recuperar + ' ' + fin_hora_recuperar
                fecha_hora = dt.datetime.strptime(fecha_fin_recuperar, '%Y-%m-%d %I:%M %p')
                fin_recuperar = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
                comentarioSolicitudRecuperar=request.form['comentarioSolicitudRecuperar']
                estado_solicitud = "Aceptado"
                query = "UPDATE solicitud_permisos SET estado_solicitud = %s ,fecha_resolucion=%s ,observaciones=%s,persona_aprueba=%s, fecha_inicio_recuperacion=%s, fecha_fin_recuperacion=%s WHERE id_permisos = %s"
                params = [estado_solicitud, fechaResolucion,comentarioSolicitudRecuperar,persona_resuelve_solicitud,inicio_recuperar,fin_recuperar,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/allNotificaciones/Permiso/{id_solicitud}')
            
            if 'rechazarSolicitudPermiso' in request.form:
                comentarioSolicitudRecuperar=request.form['comentarioSolicitudRecuperar']
                estado_solicitud = "Rechazado"
                query = "UPDATE solicitud_permisos SET estado_solicitud = %s ,fecha_resolucion=%s ,observaciones=%s,persona_aprueba=%s WHERE id_permisos = %s"
                params = [estado_solicitud, fechaResolucion,comentarioSolicitudRecuperar,persona_resuelve_solicitud,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/allNotificaciones/Permiso/{id_solicitud}')


                
        return render_template("templates/light/verNotificaciones.html", solicitudes_permiso=solicitudes_permiso[0],tipo_solicitud=tipo_solicitud)
    else:
        # Si el tipo de solicitud no es reconocido, se redirige al usuario a una página de error o a otra acción
        return "Tipo de solicitud no reconocido"
        

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

@app.route('/ver_archivo/<tipo_archivo>/<path:nombre_archivo>')
def ver_imagen(tipo_archivo,nombre_archivo):
    if not 'login' in session:
        return redirect('/')
    if tipo_archivo == "Material":
        ruta_archivo = os.path.join(app.root_path, 'static', 'images', 'inventario', 'materiales', nombre_archivo)
    elif tipo_archivo == "Herramienta":
        ruta_archivo = os.path.join(app.root_path, 'static', 'images', 'inventario', 'herramientas', nombre_archivo)
    elif tipo_archivo == "Certificado":
        ruta_archivo = os.path.join(app.root_path, 'static', 'archivos', 'certificados', nombre_archivo)
    elif tipo_archivo == "Nomina":
        ruta_archivo = os.path.join(app.root_path, 'static', 'archivos', 'nominas', nombre_archivo)
    else:
        # Si el tipo de solicitud no es reconocido, se redirige al usuario a una página de error o a otra acción
        return "Tipo de solicitud no reconocido"
    return send_file(ruta_archivo)

@app.route('/url_pruebas')
def url_pruebas():
    return render_template('calendario/calendarioInterac.html')