from main.app import app, request,bcrypt,mysql,redirect, render_template, url_for

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener datos del formulario de registro
        _fullname=request.form['fullname']
        _email=request.form['email']
        _username = request.form['username']
        _password = request.form['password']
        _passwordconfirm = request.form['confirm_password']

        # Verificar que las contraseñas coinciden
        if _password == _passwordconfirm:
            # Crear hash de la contraseña
            hashed_password = bcrypt.hashpw(_password.encode('utf-8'), bcrypt.gensalt())

            # Verificar si el usuario ya existe
            resultado = None
            sql = "SELECT * FROM `registro` WHERE `Usuario` = %s OR `Correo` = %s"
            datos_usuario = (_username, _email)
            conexion=mysql.connect()
            cursor=conexion.cursor()           
            cursor.execute(sql, datos_usuario)
            resultado = cursor.fetchone()

            if resultado is not None:
                # El usuario ya existe
                error = 'El nombre de usuario o correo electrónico ya está en uso'
                cursor.close()
                return render_template('admin/register.html', error=error)
            else:
                # El usuario no existe, crear nueva entrada en la base de datos
                sql="INSERT INTO `registro` (`id`, `Nombre`, `Correo`, `Usuario`, `Contrasena`) VALUES ('NULL',%s,%s,%s,%s);"
                datos_registro=(_fullname,_email,_username,hashed_password )
                cursor.execute(sql,datos_registro)
                conexion.commit()
                cursor.close()

                # Redirigir al usuario a la página de inicio de sesión
                return redirect(url_for('login'))
        else:
            # Las contraseñas no coinciden
            error = 'Las contraseñas no coinciden'
            return render_template('register/register.html', error=error)

    # Si el método HTTP es GET, mostrar la página de registro
    else:
        return render_template('register/register.html')
