
from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for, timedelta,flash
import json
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
            if row[41]=='Aceptado':
                stored_password_hash = row[27]
                if bcrypt.checkpw(_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                    session["login"] = True
                    session["usuario"] = username
                    session["cargo"] = row[18]
                    session["foto"] = row[23]

                    if request.form.get('recuerdame'):
                        session.permanent = True
                        app.permanent_session_lifetime = timedelta(days=7)

                    return redirect(url_for('inicio'))
                else:
                    flash('Usuario o contraseña incorrecta','error')
                    return render_template('login/login.html', campos=request.form)
            else:
                flash('El usuario aún no ha sido aceptado. Por favor, espera a que el usuario sea aceptado antes de continuar.','error')
                return redirect('/')
        else:
            flash('Usuario o contraseña incorrecta','error')
            return render_template('login/login.html', campos=request.form)
    else:
        return render_template('login/login.html')

@app.route('/recuperar-contrasena')
def recover_password():
    return render_template('login/forgot-password.html')
