import os
import uuid
from dateutil import tz
import bcrypt
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from flaskext.mysql import MySQL
import pytz
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')
# Create an instance of the Flask application with the module name and static URL path
app.config['DEBUG'] = True
# Enable debug mode for the Flask application
app.secret_key = "18*=70Y3DugTJ;-~&Jnr"
# Set a secret key for the Flask application, used for signing cookies and sessions
mysql = MySQL()
# Create an instance of the MySQL extension to interact with the database


app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'IntranetHB'
"""
app.config['MYSQL_DATABASE_HOST'] = '34.16.128.53'
app.config['MYSQL_DATABASE_USER'] = 'usuarioHB'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Human100.'
app.config['MYSQL_DATABASE_DB'] = 'IntranetHB'


app.config['MYSQL_DATABASE_HOST'] = 'srv652.hstgr.io'
app.config['MYSQL_DATABASE_USER'] = 'u122395259_HumanBionics'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Human100.'
app.config['MYSQL_DATABASE_DB'] = 'u122395259_intranerHB'
"""
# Configure the database parameters, such as host, user, password, and database name
mysql.init_app(app)
# Initialize the MySQL extension with the Flask application
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
# Set the maximum file size limit for requests

def is_password_strong(password):
    # Verificar si la contraseña cumple con los requisitos de fortaleza
    if len(password) < 8:
        return False

    if not any(c.isupper() for c in password):
        return False

    if not any(c.islower() for c in password):
        return False

    if not any(c.isdigit() for c in password):
        return False

    return True

# Get the current date and time in the Colombia time zone
def fecha_actualCO():
    colombia_tz = pytz.timezone('America/Bogota')
    fecha_actual_colombia = datetime.now(colombia_tz)
    return fecha_actual_colombia

# Generate a random string of length 10
def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnñopqrstuvwxyz_"
    longitud = 10
    secuencia = string_aleatorio.upper()
    resultado_aleatorio = sample(secuencia, longitud)
    string_aleatorio = "".join(resultado_aleatorio)
    return string_aleatorio

# Add the elapsed time to the requests
def agregar_tiempo_transcurrido(solicitudes, fecha_posicion):
    solicitudes_con_tiempo = []
    fecha_actual = fecha_actualCO()

    for solicitud in solicitudes:
        if solicitud[fecha_posicion] is not None:
         fecha_insertado = solicitud[fecha_posicion].replace(
            tzinfo=tz.gettz('America/Bogota'))

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

# Generate a unique ID using the uuid module
def generarID():
    return str(uuid.uuid4())

constantes = {
    'id_dept_sisProg': '0c3134a5-06e0-4a98-966c-65b44e509ab8',
    'id_dept_biomedica': '0ea84002-9d4e-4e36-baf2-b291b919074e',
    'id_dept_robElect': '84b29dc6-d9ce-4e14-a99e-1e52c3928078',
    'id_dept_indProt': 'ad1369e7-7569-4e85-b530-8deffd7e5f31',
    'id_dept_disPub': 'e9a8b714-f21a-4a5f-9c09-c701d67c0427',
    'id_admin': 'fb0cfeba-e4a7-4c21-ab5e-e8e9f603a5b4'
}


from main.routes import *
