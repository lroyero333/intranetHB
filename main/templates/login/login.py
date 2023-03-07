from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validar credenciales de usuario
        username = request.form['username']
        _password = request.form['password']
        

        conexion=mysql.connect()
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM registro WHERE Usuario = %s", (username))
        row = cursor.fetchone()
        conexion.commit()
        
        # Comprobar que el usuario existe en la base de datos
        # y que la contraseña es correcta
        
        if row is not None:
            hashed_password = bcrypt.hashpw(_password.encode('utf-8'), bcrypt.gensalt())
            if bcrypt.checkpw(_password.encode('utf-8'), hashed_password):
                session["login"]=True
                session["usuario"]=username
                
                return redirect(url_for('inicio'))
            else:
                error = 'Usuario o contraseña incorrecta'
                return render_template('login/login.html', error=error)
        else:
            error = 'Usuario o contraseña incorrecta'
            return render_template('login/login.html', error=error)
    else:
        return render_template('login/login.html')