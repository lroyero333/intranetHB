
import datetime as dt
import os
from datetime import datetime, time, timedelta
from random import sample

import pymysql
from flask import jsonify
from pymysql import IntegrityError
from werkzeug.utils import secure_filename

from main.run import (app, bcrypt, fecha_actualCO, flash, generarID, jsonify,
                      mysql, redirect, render_template, request, session,
                      stringAleatorio, url_for,tz)

extensionesImagenes = ['.jpg', '.jpeg', '.png']



@app.route('/calendario', methods=['GET', 'POST'])
def calendario():
    if not 'login' in session:
        return redirect('/')
    return render_template('calendario/templates/app-calendar.html')


@app.route('/misVacaciones', methods=['GET', 'POST'])
def misVacaciones():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT usuario, Nombre, Apellido,foto FROM general_users;")
    usuarios_vacaciones = cursor.fetchall()
    cursor.execute("SELECT vacaciones.*,DATE_FORMAT(fecha_inicio_vacaciones, '%d-%m-%Y') AS inicio_vacaciones,DATE_FORMAT(fecha_fin_vacaciones, '%d-%m-%Y') AS fin_vacaciones, general_users.Nombre, general_users.Apellido, general_users.foto FROM vacaciones LEFT JOIN general_users ON vacaciones.id_usuario = general_users.usuario ;")
    solicitudes_vacaciones = cursor.fetchall()

    cursor.execute("SELECT vacaciones_extemporaneas.*,DATE_FORMAT(fecha_inicio, '%d-%m-%Y') AS inicio_adelanto, DATE_FORMAT(fecha_fin, '%d-%m-%Y') AS fin_adelanto, general_users.Nombre, general_users.Apellido FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.id_usuario = general_users.usuario;")
    solicitudes_va_extemporaneas = cursor.fetchall()
    cursor.execute('SELECT usuario FROM general_users WHERE id_cargo_fk = 1')
    usuariosRH = cursor.fetchall()
    conexion.commit()

    if 'programar_vacaciones' in request.form:
        id_usuario = session['usuario']
        fecha_inicio_extemporanea = request.form['fecha_inicio_extemporanea']
        fecha_fin_extemporanea = request.form['fecha_fin_extemporanea']
        fecha_solicitud = fecha_actualCO()
        estado_solicitud = 'Pendiente'
        id_vacaciones_extemporaneas = generarID()
        tipo_notificacion = 'Vacaciones'
        mensaje = 'Ha solicitado una nueva petición de Vacaciones'
        diferencia_dias = datetime.strptime(
            fecha_fin_extemporanea, "%Y-%m-%d")-datetime.strptime(fecha_inicio_extemporanea, "%Y-%m-%d")
        dias_extemporanea = diferencia_dias.days+1
        cursor.execute(
            'SELECT dias_restantes FROM vacaciones WHERE id_usuario=%s', id_usuario)
        dias_vacaciones = cursor.fetchone()
        if dias_extemporanea > dias_vacaciones[0]:
            flash(
                'No puede solicitar más dias de las vacaciones que tiene actualmente', 'error')
            return redirect(request.url)
        query = "INSERT INTO vacaciones_extemporaneas (id_vacaciones_extemporaneas, fecha_inicio, fecha_fin ,dias_vacaciones,fecha_solicitud, estado_solicitud, id_usuario ) VALUES (%s,%s,%s,%s, %s,%s, %s)"
        params = [id_vacaciones_extemporaneas, fecha_inicio_extemporanea,
                  fecha_fin_extemporanea, dias_extemporanea, fecha_solicitud, estado_solicitud, id_usuario]
        cursor.execute(query, params)
        for usuariosRH in usuariosRH:
            query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
            params = [generarID(), tipo_notificacion, usuariosRH[0],
                      id_vacaciones_extemporaneas, id_usuario, mensaje, fecha_solicitud]
            cursor.execute(query, params)
            conexion.commit()
        flash('Solicitud de vacaciones programadas satisfactoriamente', 'correcto')

    if 'cancelar_programar_vacaciones' in request.form:
        id_vacaciones_ex = request.form['vacaciones_ex_id']
        cursor.execute(
            'SELECT dias_vacaciones, estado_solicitud, id_usuario FROM vacaciones_extemporaneas WHERE id_vacaciones_extemporaneas=%s', id_vacaciones_ex)
        dias_vacaciones_ex = cursor.fetchone()
        if dias_vacaciones_ex[1] == 'Aceptado':
            cursor.execute(
                'SELECT dias_restantes FROM vacaciones WHERE id_usuario=%s', dias_vacaciones_ex[2])
            dias_vacaciones = cursor.fetchone()
            dias_restantes = dias_vacaciones[0]+dias_vacaciones_ex[0]

            query = "UPDATE vacaciones SET dias_restantes=%s WHERE id_usuario = %s"
            params = [dias_restantes, dias_vacaciones_ex[2]]
            cursor.execute(query, params)

            cursor.execute(
                "DELETE FROM vacaciones_extemporaneas WHERE id_vacaciones_extemporaneas = %s;", (id_vacaciones_ex,))
            conexion.commit()
        else:
            cursor.execute(
                "DELETE FROM vacaciones_extemporaneas WHERE id_vacaciones_extemporaneas = %s;", (id_vacaciones_ex,))
            conexion.commit()
        flash('Vacaciones canceladas satisfactoriamente', 'correcto')
        return redirect('/misVacaciones')

    cursor.execute("SELECT vacaciones_extemporaneas.*, DATE_FORMAT(fecha_inicio, '%d-%m-%Y')as inicio_adelanto,DATE_FORMAT(fecha_fin, '%d-%m-%Y') as fin_adelanto, general_users.Nombre, general_users.Apellido FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.persona_aprueba = general_users.usuario;")
    solicitudes_vacaciones_extemporaneas = cursor.fetchall()
    conexion.commit()
    return render_template('calendario/templates/vacaciones/misVacaciones.html', usuarios_vacaciones=usuarios_vacaciones, solicitudes_vacaciones=solicitudes_vacaciones, solicitudes_vacaciones_extemporaneas=solicitudes_vacaciones_extemporaneas, solicitudes_va_extemporaneas=solicitudes_va_extemporaneas)


@app.route('/vacaciones', methods=['GET', 'POST'])
def verVacaciones():
    if not 'login' in session:
        return redirect('/')
    if session['cargo']!= 1 and session['cargo']!=0:
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT usuario, Nombre, Apellido,foto FROM general_users;")
    usuarios_vacaciones = cursor.fetchall()
    cursor.execute("SELECT vacaciones.*,DATE_FORMAT(fecha_inicio_vacaciones, '%d-%m-%Y') AS inicio_vacaciones,DATE_FORMAT(fecha_fin_vacaciones, '%d-%m-%Y') AS fin_vacaciones, general_users.Nombre, general_users.Apellido, general_users.foto FROM vacaciones LEFT JOIN general_users ON vacaciones.id_usuario = general_users.usuario ;")
    solicitudes_vacaciones = cursor.fetchall()

    cursor.execute("SELECT vacaciones_extemporaneas.*,DATE_FORMAT(fecha_inicio, '%d-%m-%Y') AS inicio_adelanto, DATE_FORMAT(fecha_fin, '%d-%m-%Y') AS fin_adelanto, general_users.Nombre, general_users.Apellido FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.id_usuario = general_users.usuario;")
    solicitudes_va_extemporaneas = cursor.fetchall()
    cursor.execute('SELECT usuario FROM general_users WHERE id_cargo_fk = 1')
    usuariosRH = cursor.fetchall()
    conexion.commit()

    if 'asignar_vacaciones' in request.form:
        id_usuario = request.form['usuario_id']
        tipo_vacaciones = request.form['tipo_vacaciones']
        fecha_inicio_vacaciones = request.form['fecha_inicio_vacaciones']
        fecha_fin_vacaciones = request.form['fecha_fin_vacaciones']
        diferencia_dias = datetime.strptime(
            fecha_fin_vacaciones, "%Y-%m-%d")-datetime.strptime(fecha_inicio_vacaciones, "%Y-%m-%d")
        dias_vacaciones = diferencia_dias.days+1
        print(dias_vacaciones)
        # Verificar si el usuario ya existe
        resultado = None
        sql = "SELECT id_usuario FROM vacaciones WHERE id_usuario = %s "
        cursor.execute(sql, id_usuario)
        resultado = cursor.fetchone()
        if resultado is not None:
            # El usuario ya existe

            flash('El usuario ya tiene vacaciones asignadas', 'error')
            return render_template('calendario/templates/vacaciones/vacaciones.html', usuarios_vacaciones=usuarios_vacaciones, solicitudes_vacaciones=solicitudes_vacaciones)
        else:
            query = "INSERT INTO vacaciones (id_vacaciones,tipo_vacaciones, fecha_inicio_vacaciones, fecha_fin_vacaciones, id_usuario, dias_vacaciones, dias_restantes ) VALUES (%s,%s,%s, %s,%s,%s,%s)"
            params = [generarID(), tipo_vacaciones, fecha_inicio_vacaciones,
                      fecha_fin_vacaciones, id_usuario, dias_vacaciones, dias_vacaciones]
            cursor.execute(query, params)
            conexion.commit()
            flash('Vacaciones asignadas satisfactoriamente', 'correcto')

    cursor.execute("SELECT vacaciones_extemporaneas.*, DATE_FORMAT(fecha_inicio, '%d-%m-%Y')as inicio_adelanto,DATE_FORMAT(fecha_fin, '%d-%m-%Y') as fin_adelanto, general_users.Nombre, general_users.Apellido FROM vacaciones_extemporaneas LEFT JOIN general_users ON vacaciones_extemporaneas.persona_aprueba = general_users.usuario;")
    solicitudes_vacaciones_extemporaneas = cursor.fetchall()
    conexion.commit()
    return render_template('calendario/templates/vacaciones/vacaciones.html', usuarios_vacaciones=usuarios_vacaciones, solicitudes_vacaciones=solicitudes_vacaciones, solicitudes_vacaciones_extemporaneas=solicitudes_vacaciones_extemporaneas, solicitudes_va_extemporaneas=solicitudes_va_extemporaneas)





@app.route('/misPermisos', methods=['GET', 'POST'])
def misPermisos():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    query="SELECT solicitud_permisos.*,  DATE_FORMAT(fecha_inicio_permiso, %s) AS inicio_permiso, DATE_FORMAT(fecha_fin_permiso, %s) AS fin_permiso, DATE_FORMAT(fecha_inicio_recuperacion, %s) AS inicio_recuperacion, DATE_FORMAT(fecha_fin_recuperacion, %s) AS fin_recuperacion, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.id_usuario = general_users.usuario WHERE id_usuario=%s;"
    cursor.execute(query,('%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p', session['usuario']))
    solicitudes_permisos = cursor.fetchall()
    query="SELECT id_extra, DATE_FORMAT(fecha_inicio, %s) AS fecha_inicio, DATE_FORMAT(fecha_fin, %s) AS fecha_fin FROM solicitud_permiso_extra WHERE id_usuario = %s AND estado_solicitud= 'Pendiente';"
    cursor.execute(query,('%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p', session['usuario']))
    solicitud_permiso_ex = cursor.fetchall()
    query="SELECT solicitud_permiso_extra.*, general_users.Nombre, general_users.Apellido, general_users.foto, DATE_FORMAT(fecha_inicio, %s) AS inicio_permiso, DATE_FORMAT(fecha_fin, %s) AS fecha_fin FROM solicitud_permiso_extra LEFT JOIN general_users ON solicitud_permiso_extra.resuelto_por = general_users.usuario WHERE estado_solicitud= 'Aceptado' AND id_usuario=%s;"
    cursor.execute(query,('%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p', session['usuario']))
    solicitud_permiso_extra = cursor.fetchall()
    conexion.commit()

    if 'agendar_permiso' in request.form:
        mensaje = 'Ha solicitado una nueva petición de Permiso'
        tipo_notificacion = 'Permiso'
        id_permisos = generarID()
        id_usuario = session['usuario']
        inicio_dia_permiso = request.form['inicio_dia_permiso']  # 2023-03-28
        inicio_hora_permiso = request.form['inicio_hora_permiso']  # 10:00 am
        fin_dia_permiso = request.form['fin_dia_permiso']
        fin_hora_permiso = request.form['fin_hora_permiso']
        contar_sabados = request.form.get('contar_sabados')
        motivo_permiso = request.form['motivo_permiso']
        fecha_inicio_permiso = inicio_dia_permiso + ' ' + inicio_hora_permiso
        fecha_hora = dt.datetime.strptime(
            fecha_inicio_permiso, '%Y-%m-%d %I:%M %p')
        inicio_permiso = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_permiso = fin_dia_permiso + ' ' + fin_hora_permiso
        fecha_hora = dt.datetime.strptime(
            fecha_fin_permiso, '%Y-%m-%d %I:%M %p')
        fin_permiso = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fecha_solicitud = fecha_actualCO()
        duracion_permiso = dt.datetime.strptime(
            fin_permiso, '%Y-%m-%d %H:%M:%S') - dt.datetime.strptime(inicio_permiso, '%Y-%m-%d %H:%M:%S')

        inicio_dia_recuperar = request.form['inicio_dia_recuperar']
        inicio_hora_recuperar = request.form['inicio_hora_recuperar']
        fin_dia_recuperar = request.form['fin_dia_recuperar']
        fin_hora_recuperar = request.form['fin_hora_recuperar']
        fecha_inicio_recuperar = inicio_dia_recuperar + ' ' + inicio_hora_recuperar
        fecha_hora = dt.datetime.strptime(
            fecha_inicio_recuperar, '%Y-%m-%d %I:%M %p')
        inicio_recuperar = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_recuperar = fin_dia_recuperar + ' ' + fin_hora_recuperar
        fecha_hora = dt.datetime.strptime(
            fecha_fin_recuperar, '%Y-%m-%d %I:%M %p')
        fin_recuperar = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        print(duracion_permiso)
        print(inicio_permiso)
        print(fin_permiso)
        print(contar_sabados)
        # Inicializar lista de fechas
        fechas = []
        # Definir fechas de inicio y fin
        fecha_inicio = dt.datetime.strptime(
            inicio_permiso, '%Y-%m-%d %H:%M:%S')
        fecha_fin = dt.datetime.strptime(fin_permiso, '%Y-%m-%d %H:%M:%S')

        # Definir horario de trabajo
        hora_inicio_manana = time(8, 0, 0)
        hora_fin_manana = time(12, 30, 0)
        hora_inicio_tarde = time(14, 0, 0)
        hora_fin_tarde = time(18, 0, 0)

        if contar_sabados:
            print('Está activo')

            hora_inicio_manana_sabado = time(8, 0, 0)
            hora_fin_manana_sabado = time(12, 30, 0)

            dias_trabajo = set(range(0, 5))

            fecha_actual = fecha_inicio
            while fecha_actual <= fecha_fin:
                if (fecha_actual.weekday() in dias_trabajo and
                    ((fecha_actual.time() > hora_inicio_manana and fecha_actual.time() <= hora_fin_manana) or
                        (fecha_actual.time() > hora_inicio_tarde and fecha_actual.time() <= hora_fin_tarde))):
                    fechas.append(fecha_actual)
                elif (fecha_actual.weekday() == 5 and
                      hora_inicio_manana_sabado < fecha_actual.time() <= hora_fin_manana_sabado):
                    fechas.append(fecha_actual)
                fecha_actual += dt.timedelta(minutes=30)
                # Omitir los domingos
                if fecha_actual.weekday() == 6:
                    fecha_actual += dt.timedelta(days=1)
        else:
            dias_trabajo = set(range(0, 5))
            # Iterar entre fechas cada media hora
            fecha_actual = fecha_inicio
            while fecha_actual <= fecha_fin:
                # Verificar si la hora actual está dentro del horario de trabajo
                if fecha_actual.weekday() in dias_trabajo:
                    if (fecha_actual.time() > hora_inicio_manana and fecha_actual.time() <= hora_fin_manana) or (fecha_actual.time() > hora_inicio_tarde and fecha_actual.time() <= hora_fin_tarde):
                        fechas.append(fecha_actual)
                fecha_actual += dt.timedelta(minutes=30)
        # Imprimir lista de fechas
        for fecha in fechas:
            print(fecha)
        cantidad_media_horas = len(fechas)
        cantidad_horas = cantidad_media_horas/2
        horas_enteras = int(cantidad_horas)
        minutos_fraccion = int((cantidad_horas - horas_enteras) * 60)
        if horas_enteras == 0:
            cantidad_horas = f"{minutos_fraccion} minutos"
        elif minutos_fraccion == 0 and horas_enteras == 1:
            cantidad_horas = f"{horas_enteras} hora"
        elif minutos_fraccion == 0:
            cantidad_horas = f"{horas_enteras} horas"
        elif horas_enteras == 1:
            cantidad_horas = f"{horas_enteras} hora y {minutos_fraccion} minutos"
        else:
            cantidad_horas = f"{horas_enteras} horas y {minutos_fraccion} minutos"

        cursor.execute(
            'SELECT usuario FROM general_users WHERE id_cargo_fk = 1')
        usuariosRH = cursor.fetchall()

        query = "INSERT INTO solicitud_permisos (id_permisos,fecha_inicio_permiso, fecha_fin_permiso, fecha_solicitud, horas_de_permiso, id_usuario, motivo_permiso , fecha_inicio_recuperacion, fecha_fin_recuperacion ) VALUES (%s, %s,%s, %s, %s, %s, %s,%s,%s)"
        params = [id_permisos, inicio_permiso, fin_permiso,
                  fecha_solicitud, cantidad_horas, id_usuario, motivo_permiso, inicio_recuperar, fin_recuperar]
        cursor.execute(query, params)
        conexion.commit()

        for usuariosRH in usuariosRH:
            query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
            params = [generarID(), tipo_notificacion, usuariosRH[0],
                      id_permisos, id_usuario, mensaje, fecha_solicitud]
            cursor.execute(query, params)
            conexion.commit()

        flash('Permiso solicitado satisfactoriamente', 'correcto')
        return redirect('/misPermisos')
    if 'agendar_permisoEX' in request.form:
        mensaje = 'Ha solicitado una nueva petición de Permiso a la empresa'
        tipo_notificacion = 'Permiso_Empresa'
        id_permisos = generarID()
        id_usuario = session['usuario']
        inicio_dia_permiso = request.form['inicio_dia_permisoEX']  # 2023-03-28
        inicio_hora_permiso = request.form['inicio_hora_permisoEX']  # 10:00 am
        fin_dia_permiso = request.form['fin_dia_permisoEX']
        fin_hora_permiso = request.form['fin_hora_permisoEX']
        motivo_permiso = request.form['motivo_permiso']
        fecha_inicio_permiso = inicio_dia_permiso + ' ' + inicio_hora_permiso
        fecha_hora = dt.datetime.strptime(
            fecha_inicio_permiso, '%Y-%m-%d %I:%M %p')
        inicio_permiso = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin_permiso = fin_dia_permiso + ' ' + fin_hora_permiso
        fecha_hora = dt.datetime.strptime(
            fecha_fin_permiso, '%Y-%m-%d %I:%M %p')
        fin_permiso = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
        fecha_solicitud = fecha_actualCO()
        duracion_permiso = dt.datetime.strptime(
            fin_permiso, '%Y-%m-%d %H:%M:%S') - dt.datetime.strptime(inicio_permiso, '%Y-%m-%d %H:%M:%S')

        print(duracion_permiso)
        print(inicio_permiso)
        print(fin_permiso)

        cursor.execute(
            'SELECT usuario FROM general_users WHERE id_cargo_fk = 1')
        usuariosRH = cursor.fetchall()

        query = "INSERT INTO solicitud_permiso_extra (id_extra,fecha_inicio, fecha_fin, fecha_solicitud, id_usuario, motivo) VALUES (%s, %s,%s, %s, %s, %s)"
        params = [id_permisos, inicio_permiso, fin_permiso,
                  fecha_solicitud, id_usuario, motivo_permiso]
        cursor.execute(query, params)
        conexion.commit()

        for usuariosRH in usuariosRH:
            query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
            params = [generarID(), tipo_notificacion, usuariosRH[0],
                      id_permisos, id_usuario, mensaje, fecha_solicitud]
            cursor.execute(query, params)
            conexion.commit()

        flash('Permiso solicitado satisfactoriamente', 'correcto')
        return redirect('/misPermisos')
    if 'cancelarPermiso' in request.form:
        permiso_id = request.form['permiso_id']
        cursor.execute("DELETE FROM solicitud_permisos WHERE id_permisos = %s;", (permiso_id,))
        conexion.commit()
        flash('Permiso cancelado satisfactoriamente', 'correcto')
        return redirect('/misPermisos')
    if 'cancelarPermisoEx' in request.form:
        print('BOTON BOTON')
        permiso_id = request.form['permiso_id_ex']
        print('BOTON BOTON', permiso_id)

        cursor.execute( "DELETE FROM solicitud_permiso_extra WHERE id_extra = %s;", (permiso_id,))
        conexion.commit()
        flash('Permiso de acceso a la empresa cancelado satisfactoriamente', 'correcto')
        return redirect('/misPermisos')
    return render_template('calendario/templates/permisos/misPermisos.html', solicitudes_permisos=solicitudes_permisos, solicitud_permiso_ex=solicitud_permiso_ex, solicitud_permiso_extra=solicitud_permiso_extra)

@app.route('/permisos', methods=['GET', 'POST'])
def verPermisos():
    if not 'login' in session:
        return redirect('/')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    query="SELECT solicitud_permisos.*,  DATE_FORMAT(fecha_inicio_permiso, %s) AS inicio_permiso, DATE_FORMAT(fecha_fin_permiso, %s) AS fin_permiso, DATE_FORMAT(fecha_inicio_recuperacion, %s) AS inicio_recuperacion, DATE_FORMAT(fecha_fin_recuperacion, %s) AS fin_recuperacion, general_users.Nombre, general_users.Apellido, general_users.foto FROM solicitud_permisos LEFT JOIN general_users ON solicitud_permisos.id_usuario = general_users.usuario WHERE estado_solicitud= 'Aceptado'"
    cursor.execute(query,('%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p'))
    solicitudes_permisos = cursor.fetchall()
    query="SELECT solicitud_permiso_extra.*, general_users.Nombre, general_users.Apellido, general_users.foto, DATE_FORMAT(fecha_inicio, %s) AS inicio_permiso, DATE_FORMAT(fecha_fin, %s) AS fecha_fin FROM solicitud_permiso_extra LEFT JOIN general_users ON solicitud_permiso_extra.resuelto_por = general_users.usuario WHERE estado_solicitud= 'Aceptado';"
    cursor.execute(query,('%d-%m-%Y %H:%i %p', '%d-%m-%Y %H:%i %p'))
    solicitud_permiso_extra = cursor.fetchall()
    conexion.commit()
    return render_template('calendario/templates/permisos/permisos.html', solicitudes_permisos=solicitudes_permisos, solicitud_permiso_extra=solicitud_permiso_extra)


@app.route('/eventos')
def obtener_cursos():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    fecha_actual = fecha_actualCO()
    cursor.execute(
        'SELECT * FROM cursos')
    eventos = cursor.fetchall()
    cursor.execute(
        'SELECT tipo_vacaciones, fecha_inicio_vacaciones, fecha_fin_vacaciones FROM vacaciones WHERE id_usuario=%s', session['usuario'])
    vacaciones = cursor.fetchall()

    cursor.execute('SELECT tipo_vacaciones, fecha_inicio, fecha_fin FROM vacaciones_extemporaneas WHERE id_usuario=%s AND estado_solicitud=%s',
                   (session['usuario'], 'Aceptado'))
    vacaciones_ex = cursor.fetchall()

    cursor.execute('SELECT fecha_inicio_permiso, fecha_fin_permiso FROM solicitud_permisos WHERE id_usuario=%s AND estado_solicitud=%s',
                   (session['usuario'], 'Aceptado'))
    permisos = cursor.fetchall()

    cursor.execute('SELECT fecha_inicio_recuperacion, fecha_fin_recuperacion FROM solicitud_permisos WHERE id_usuario=%s AND estado_solicitud=%s',
                   (session['usuario'], 'Aceptado'))
    permisos_recuperar = cursor.fetchall()

    cursor.execute(
        'SELECT Nombre, Apellido, Fecha_nacimiento FROM general_users')
    cumpleaños = cursor.fetchall()

    eventos_json = []
    for evento in eventos:
        evento_json = {'title': evento[2], 'url': f'/cursos/{evento[0]}', 'start': evento[3].strftime(
            '%Y-%m-%d'), 'end': evento[4].strftime(
            '%Y-%m-%d'),  'location': evento[6], 'allDay': 'true', "className": 'bg-info'}
        eventos_json.append(evento_json)
    for vacaciones in vacaciones:
        evento_json = {'title': 'Vacaciones ' + vacaciones[0], 'url': '/misVacaciones', 'start': vacaciones[1].strftime(
            '%Y-%m-%d'), 'end': vacaciones[2].strftime(
            '%Y-%m-%d'), 'allDay': 'true', "className": 'bg-success'}
        eventos_json.append(evento_json)
    for vacaciones_ex in vacaciones_ex:
        evento_json = {'title': 'Vacaciones Extemporanea ' + vacaciones_ex[0], 'url': '/misVacaciones', 'start': vacaciones_ex[1].strftime(
            '%Y-%m-%d'), 'end': vacaciones_ex[2].strftime(
            '%Y-%m-%d'), 'allDay': 'true',  "backgroundColor": "#D0A9F5"}
        eventos_json.append(evento_json)
    for permisos in permisos:
        evento_json = {'title': 'Permiso ', 'url': '/misPermisos', 'start': permisos[0].strftime(
            '%Y-%m-%d %H:%M:%S'), 'end': permisos[1].strftime(
            '%Y-%m-%d %H:%M:%S'), 'allDay': 'false', "backgroundColor": "#2D89DA"}
        eventos_json.append(evento_json)
    for permisos_recuperar in permisos_recuperar:
        evento_json = {'title': 'Recuperar Permiso ', 'url': '/misPermisos', 'start': permisos_recuperar[0].strftime(
            '%Y-%m-%d %H:%M:%S'), 'end': permisos_recuperar[1].strftime(
            '%Y-%m-%d %H:%M:%S'), 'allDay': 'false', "backgroundColor": "#9B2DDA"}
        eventos_json.append(evento_json)

    for cumpleaños in cumpleaños:
        fecha_nacimiento = cumpleaños[2]
        proximo_cumpleaños = datetime(
        fecha_actual.year, fecha_nacimiento.month, fecha_nacimiento.day, tzinfo=fecha_actual.tzinfo)
        if proximo_cumpleaños < fecha_actual:
            proximo_cumpleaños = proximo_cumpleaños.replace(
            year=fecha_actual.year + 1, tzinfo=fecha_actual.tzinfo)
        while proximo_cumpleaños <= fecha_actual + timedelta(days=365):
            evento_json = {
                'title': f"Cumpleaños de {cumpleaños[0]} {cumpleaños[1]}",
                'start': proximo_cumpleaños.strftime('%Y-%m-%d'),
                "recurrence": ["RRULE:FREQ=YEARLY"],
                'allDay': 'true',
                "backgroundColor": "#CFD13F"
            }
            eventos_json.append(evento_json)
            proximo_cumpleaños = proximo_cumpleaños.replace(
                year=proximo_cumpleaños.year + 1)
    return jsonify(eventos_json)
