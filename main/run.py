import os
import uuid

import bcrypt
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from flaskext.mysql import MySQL
import pytz
from werkzeug.utils import secure_filename

app=Flask(__name__, static_url_path='/static')
app.config['DEBUG'] = True
app.secret_key="18*=70Y3DugTJ;-~&Jnr"
mysql=MySQL()
"""
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='login'
"""
app.config['MYSQL_DATABASE_HOST']='34.16.128.53'
app.config['MYSQL_DATABASE_USER']='usuarioHB'
app.config['MYSQL_DATABASE_PASSWORD']='Human100.'
app.config['MYSQL_DATABASE_DB']='IntranetHB'

"""app.config['MYSQL_DATABASE_HOST']='srv652.hstgr.io'
app.config['MYSQL_DATABASE_USER']='u122395259_HumanBionics'
app.config['MYSQL_DATABASE_PASSWORD']='Human100.'
app.config['MYSQL_DATABASE_DB']='u122395259_intranerHB'
"""
mysql.init_app(app)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

def fecha_actualCO():
    colombia_tz = pytz.timezone('America/Bogota')
    fecha_actual_colombia = datetime.now(colombia_tz)
    fecha_formateada = fecha_actual_colombia.strftime('%Y-%m-%d %H:%M:%S')  # Formato de fecha deseado
    return fecha_formateada

def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud = 10
    secuencia = string_aleatorio.upper()
    resultado_aleatorio = sample(secuencia, longitud)
    string_aleatorio = "".join(resultado_aleatorio)
    return string_aleatorio

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

def generarID():
    return str(uuid.uuid4())
from main.routes import *