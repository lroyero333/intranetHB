
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for, timedelta
import json


from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'login' in session:
        return redirect('/inicio')
    if request.method == 'POST':
        # Validar credenciales de usuario
        username = request.form['username']
        _password = request.form['password']
        conexion = mysql.connect()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT *  FROM general_users WHERE usuario = %s", (username))
        row = cursor.fetchone()
        conexion.commit()
        # Comprobar que el usuario existe en la base de datos
        # y que la contraseña es correcta

        if row is not None:
            stored_password_hash = row[27]
            if bcrypt.checkpw(_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                session["login"] = True
                session["usuario"] = username
                session["nombre"] = row[1]
                session["nombre2"] = row[2]
                session["apellido"] = row[3]
                session["apellido2"] = row[4]
                session["genero"] = row[5]
                session["fecha_nacimiento"] = row[7]
                session["edad"] = row[28]
                session["correo"] = row[7]
                session["identificacion"] = row[8]
                session["direccion"] = row[9]
                session["barrio"] = row[10]
                session["ciudad"] = row[11]
                session["departamento"] = row[12]
                session["pais"] = row[13]
                session["telefono"] = row[14]
                session["celular"] = row[15]
                session["habilidades"] = row[16]
                session["profesion"] = row[17]
                session["cargo"] = row[18]
                session["institucion"] = row[19]
                session["posgrado"] = row[20]
                session["entidad_salud"] = row[21]
                session["tipo_sangre"] = row[22]
                session["foto"] = row[23]
                session["nombre_contacto"] = row[24]
                session["numero_contacto"] = row[25]

                if request.form.get('recuerdame'):
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(days=7)

                return redirect(url_for('inicio'))
            else:
                error = 'Usuario o contraseña incorrecta'
                return render_template('login/login.html', error=error, campos=request.form)
        else:
            error = 'Usuario o contraseña incorrecta'
            return render_template('login/login.html', error=error, campos=request.form)
    else:
        return render_template('login/login.html')


@app.route('/recuperar-contrasena')
def recover_password():
    return render_template('login/forgot-password.html')
