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

from main.run import app, mysql
from main.templates.calendario import calendario
from main.templates.error import error
from main.templates.infoUsuario import usuario
from main.templates.inventario import inventario
from main.templates.login import login
from main.templates.miTrabajo import miTrabajo
from main.templates.nomina_certificados import nomina_certificado
from main.templates.register import register
from main.templates.usersCRUD import usersCRUD


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

def agregar_tiempo_transcurrido(solicitudes, fecha_posicion):
    solicitudes_con_tiempo = []
    fecha_actual = datetime.now()

    for solicitud in solicitudes:
        fecha_insertado = solicitud[fecha_posicion]
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
        solicitud_con_tiempo = list(solicitud)
        solicitud_con_tiempo.append(tiempo_transcurrido)
        solicitudes_con_tiempo.append(solicitud_con_tiempo)
    return solicitudes_con_tiempo

@app.before_request
def notificacionesRH():
    if not 'login' in session:
        return

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT general_users.Nombre, general_users.Apellido, general_users.foto, cargos.nombre_cargo FROM general_users LEFT JOIN usuario_cargo ON general_users.id = usuario_cargo.id_usuario_fk LEFT JOIN cargos ON usuario_cargo.id_cargo_fk = cargos.id_cargo WHERE usuario= %s;", session['usuario'])
    usuario_base=cursor.fetchone()

    
    cursor.execute("SELECT solicitud_certificado.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_certificado LEFT JOIN general_users ON solicitud_certificado.solicitante = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_certificado = cursor.fetchall()
    cursor.execute("SELECT solicitud_nomina.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_nomina LEFT JOIN general_users ON solicitud_nomina.solicitante = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_nomina = cursor.fetchall()

    cursor.execute("SELECT vacaciones_extemporaneas.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.id_usuario = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_va_extemporaneas = cursor.fetchall()

    cursor.execute("SELECT solicitud_permisos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.id_usuario = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_permisos = cursor.fetchall()

    cursor.execute("SELECT movimientos_herramientas.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM movimientos_herramientas LEFT JOIN general_users ON movimientos_herramientas.responsable = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_tools = cursor.fetchall()

    cursor.execute("SELECT movimientos_materiales.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM movimientos_materiales LEFT JOIN general_users ON movimientos_materiales.responsable = general_users.usuario ORDER BY fecha_solicitud DESC;")
    solicitudes_material= cursor.fetchall()

    cursor.execute("SELECT * FROM solicitud_certificado WHERE estado_notificacion= %s;","No visto")
    notificacion_certificado = cursor.fetchall()
    cursor.execute("SELECT * FROM solicitud_nomina WHERE estado_notificacion= %s;","No visto")
    notificacion_nomina = cursor.fetchall()
    cursor.execute("SELECT * FROM vacaciones_extemporaneas WHERE estado_notificacion= %s;","No visto")
    notificacion_vacaciones = cursor.fetchall()
    cursor.execute("SELECT * FROM solicitud_permisos WHERE estado_notificacion= %s;","No visto")
    notificacion_permisos = cursor.fetchall()
    cursor.execute("SELECT * FROM movimientos_herramientas WHERE estado_notificacion= %s;","No visto")
    notificacion_tool = cursor.fetchall()
    cursor.execute("SELECT * FROM movimientos_materiales WHERE estado_notificacion= %s;","No visto")
    notificacion_material = cursor.fetchall()
    nada=[]
    conexion.commit()
    # Verificar si la sesión existe
    if 'cargo' in session:
        cargo = session['cargo']
        # Verificar el cargo del usuario
        if cargo == 1:
            solicitudes_total = (notificacion_certificado + notificacion_nomina + notificacion_vacaciones + notificacion_permisos)
            solicitudes_total_count = len(solicitudes_total)
        elif cargo == 3:
            solicitudes_total = notificacion_tool+notificacion_material
            solicitudes_total_count = len(solicitudes_total)
        else:
            solicitudes_total = nada
            solicitudes_total_count = len(solicitudes_total)
            print('Por ahora nada')
        # Obtener la cantidad de solicitudes totales
        solicitudes_total_count = len(solicitudes_total)
    else:
        # Si no existe la sesión, no se hace nada
        print('No existe la sesión')

    certificadooss_con_tiempo = agregar_tiempo_transcurrido(solicitudes_certificado, 4)
    nominaas_con_tiempo = agregar_tiempo_transcurrido(solicitudes_nomina, 3)
    vacaciones_con_tiempo = agregar_tiempo_transcurrido(solicitudes_va_extemporaneas, 6)
    permisos_con_tiempo = agregar_tiempo_transcurrido(solicitudes_permisos, 6)
    tools_con_tiempo = agregar_tiempo_transcurrido(solicitudes_tools, 7)
    material_con_tiempo = agregar_tiempo_transcurrido(solicitudes_material, 7)


    # Guardamos las solicitudes en la variable de contexto `g`
    g.usuario_base=usuario_base
    g.solicitudes_total_count = solicitudes_total_count
    g.solicitudes_certificado = certificadooss_con_tiempo
    g.solicitudes_nomina=nominaas_con_tiempo
    g.solicitudes_va_extemporaneas=vacaciones_con_tiempo
    g.solicitudes_permisos=permisos_con_tiempo
    g.solicitudes_tools=tools_con_tiempo
    g.solicitudes_material=material_con_tiempo

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
    elif tipo_solicitud == "herramienta":
        tabla_solicitud = "movimientos_herramientas"
        campo_id_solicitud = "id_movimiento"
    elif tipo_solicitud == "material":
        tabla_solicitud = "movimientos_materiales"
        campo_id_solicitud = "id_movimiento"
    else:
        # Si el tipo de solicitud no es reconocido, se redirige al usuario a una página de error o a otra acción
        return render_template('error/error-404.html')

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
    elif tipo_solicitud == "herramienta":
        cursor.execute("SELECT movimientos_herramientas.*, general_users.Nombre, general_users.Apellido, general_users.foto , herramientas.* FROM movimientos_herramientas LEFT JOIN general_users ON movimientos_herramientas.responsable = general_users.usuario LEFT JOIN herramientas ON movimientos_herramientas.id_herramienta=herramientas.id_herramientas WHERE id_movimiento=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_tool = cursor.fetchall()
        conexion.commit()
        print(solicitudes_tool)
        if request.method == 'POST':
            if 'aceptarSolicitudTool' in request.form:
                observaciones=request.form['comentarioSolicitudTool']
                estado_solicitud = "Aceptado"
                query = "UPDATE movimientos_herramientas SET fecha_movimiento = %s, persona_aprueba = %s ,fecha_resolucion=%s ,estado_solicitud=%s ,observaciones=%s WHERE id_movimiento = %s"
                params = [fechaResolucion , persona_resuelve_solicitud, fechaResolucion,estado_solicitud, observaciones,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/allNotificaciones/herramienta/{id_solicitud}')
            
            if 'rechazarSolicitudTool' in request.form:
                observaciones=request.form['comentarioSolicitudTool']
                estado_solicitud = "Rechazado"
                query = "UPDATE movimientos_herramientas SET fecha_movimiento = %s, persona_aprueba = %s ,fecha_resolucion=%s ,estado_solicitud=%s ,observaciones=%s WHERE id_movimiento = %s"
                params = [fechaResolucion , persona_resuelve_solicitud, fechaResolucion,estado_solicitud, observaciones,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/allNotificaciones/herramienta/{id_solicitud}')
        return render_template("templates/light/verNotificaciones.html", solicitudes_tool=solicitudes_tool[0],tipo_solicitud=tipo_solicitud)
    
    elif tipo_solicitud == "material":
        cursor.execute("SELECT movimientos_materiales.*, general_users.Nombre, general_users.Apellido, general_users.foto , materiales.* FROM movimientos_materiales LEFT JOIN general_users ON movimientos_materiales.responsable = general_users.usuario LEFT JOIN materiales ON movimientos_materiales.id_material=materiales.id_material WHERE id_movimiento=%s ORDER BY fecha_solicitud DESC;", id_solicitud)
        solicitudes_material = cursor.fetchall()
        conexion.commit()
        print(solicitudes_material)
        if request.method == 'POST':
            if 'aceptarSolicitudMaterial' in request.form:
                observaciones=request.form['comentarioSolicitudMaterial']
                estado_solicitud = "Aceptado"
                query = "UPDATE movimientos_materiales SET fecha_movimiento = %s, persona_aprueba = %s ,estado_solicitud=%s ,observaciones=%s WHERE id_movimiento = %s"
                params = [fechaResolucion , persona_resuelve_solicitud, fechaResolucion,estado_solicitud, observaciones,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/allNotificaciones/material/{id_solicitud}')
            
            if 'rechazarSolicitudMaterial' in request.form:
                observaciones=request.form['comentarioSolicitudMaterial']
                estado_solicitud = "Rechazado"
                query = "UPDATE movimientos_materiales SET fecha_movimiento = %s, persona_aprueba = %s ,estado_solicitud=%s ,observaciones=%s WHERE id_movimiento = %s"
                params = [fechaResolucion , persona_resuelve_solicitud, estado_solicitud, observaciones,id_solicitud]
                cursor.execute(query, params)
                conexion.commit()
                return redirect(f'/allNotificaciones/material/{id_solicitud}')
        return render_template("templates/light/verNotificaciones.html", solicitudes_material=solicitudes_material[0],tipo_solicitud=tipo_solicitud)
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
    cursos_con_tiempo = agregar_tiempo_transcurrido(datosCursos, 5)

    cursor.execute("SELECT noticias.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM noticias LEFT JOIN general_users ON noticias.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosNoticias = cursor.fetchall()
    conexion.commit()
    noticias_con_tiempo = agregar_tiempo_transcurrido(datosNoticias, 4)
    return render_template('templates/light/index.html', datosCursos=cursos_con_tiempo, datosNoticias=noticias_con_tiempo)

@app.route('/cursos')
def cursos():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT cursos.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM cursos LEFT JOIN general_users ON cursos.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosCursos = cursor.fetchall()
    conexion.commit()
    cursos_con_tiempo = agregar_tiempo_transcurrido(datosCursos, 5)
    return render_template('calendario/templates/cursos/Cursos.html', datosCursos=cursos_con_tiempo)

@app.route('/noticias')
def noticias():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT noticias.*, general_users.Nombre, general_users.Apellido, general_users.foto FROM noticias LEFT JOIN general_users ON noticias.id_usuario_fk = general_users.usuario ORDER BY fecha_publicacion DESC;")
    datosNoticias = cursor.fetchall()
    conexion.commit()
    noticias_con_tiempo = agregar_tiempo_transcurrido(datosNoticias, 4)
    return render_template('calendario/templates/noticias/Noticias.html',  datosNoticias=noticias_con_tiempo)


@app.route('/Noticias')
def noticiass():
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