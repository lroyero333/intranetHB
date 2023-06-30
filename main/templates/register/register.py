from main.run import (app, bcrypt, mysql, redirect, render_template, request,
                      url_for, is_password_strong, flash, generarID, fecha_actualCO)


@app.route('/register', methods=['GET', 'POST'])
def register():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if request.method == 'POST':
        # Obtener datos del formulario de registro
        _fullname = request.form['fullname']
        nombre_parts = _fullname.split()
        nombre = nombre_parts[0]
        segundoNombre = nombre_parts[1] if len(nombre_parts) > 1 else ''
        _fulllastname = request.form['fulllastname']

        apellido_parts = _fulllastname.split()
        apelliddo = apellido_parts[0]
        segundoApellido = apellido_parts[1] if len(apellido_parts) > 1 else ''

        _email = request.form['email']
        _username = request.form['username']
        _password = request.form['password']
        _passwordconfirm = request.form['confirm_password']
        tipo_notificacion = 'Registro'
        cursor.execute(
            'SELECT usuario FROM general_users WHERE id_cargo_fk = 1')
        usuariosRH = cursor.fetchall()
        mensaje = 'Tiene pendiente su registro'
        feha_actual = fecha_actualCO()
        id_usuario = generarID()
        if not is_password_strong(_password):
            flash('La contraseña debe tener al menos 8 caracteres y contener al menos una letra mayúscula, una letra minúscula y un dígito.', 'error')
            return redirect(request.url)

        # Verificar que las contraseñas coinciden
        if _password == _passwordconfirm:
            # Crear hash de la contraseña
            hashed_password = bcrypt.hashpw(
                _password.encode('utf-8'), bcrypt.gensalt())

            # Verificar si el usuario ya existe
            resultado = None
            sql = "SELECT * FROM `general_users` WHERE `usuario` = %s OR `correo` = %s"
            datos_usuario = (_username, _email)
            cursor.execute(sql, datos_usuario)
            resultado = cursor.fetchone()

            if resultado is not None:
                # El usuario ya existe
                flash(
                    'El nombre de usuario o correo electrónico ya está en uso', 'error')
                cursor.close()
                return render_template('register/register.html', campos=request.form)
            else:
                # El usuario no existe, crear nueva entrada en la base de datos
                sql = "INSERT INTO `general_users` (id,`Nombre`, segundo_nombre, `Apellido`, segundo_apellido, `Correo`, `Usuario`, `Contrasena`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
                datos_registro = (id_usuario,nombre, segundoNombre, apelliddo, segundoApellido,
                                  _email, _username, hashed_password)
                cursor.execute(sql, datos_registro)
                conexion.commit()
                for usuariosRH in usuariosRH:
                    query = "INSERT INTO notificaciones (id_notificacion, tipo_notificacion, id_usuario, id_solicitud, creador_solicitud ,mensaje, fecha_notificacion) VALUES (%s, %s,%s,%s,%s,%s,%s)"
                    params = [generarID(), tipo_notificacion, usuariosRH[0],
                              id_usuario, _username, mensaje, feha_actual]
                    cursor.execute(query, params)
                    conexion.commit()
                cursor.close()

                # Redirigir al usuario a la página de inicio de sesión
                flash('¡Registro completado con éxito!', 'correcto')
                return redirect('/')
        else:
            # Las contraseñas no coinciden
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register/register.html', campos=request.form)

    # Si el método HTTP es GET, mostrar la página de registro
    else:
        return render_template('register/register.html', campos=request.form)
