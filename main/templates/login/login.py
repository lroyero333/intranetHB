from main.routes import request, app,mysql,bcrypt,session,redirect,render_template,url_for
import json


from main.routes import request, app, mysql, bcrypt, session, redirect, render_template, url_for



@app.route('/', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        # Validar credenciales de usuario
        username = request.form['username']
        _password = request.form['password']
        

        conexion=mysql.connect()
        cursor=conexion.cursor()
        cursor.execute("SELECT *  FROM general_users WHERE usuario = %s", (username))
        row = cursor.fetchone()
        conexion.commit()
        
        # Comprobar que el usuario existe en la base de datos
        # y que la contraseña es correcta
        
        if row is not None:
            hashed_password = bcrypt.hashpw(_password.encode('utf-8'), bcrypt.gensalt())
            if bcrypt.checkpw(_password.encode('utf-8'), hashed_password):
                session["login"]=True
                session["usuario"]=username
                session["nombre"]=row[1]
                session["nombre2"]=row[2]
                session["apellido"]=row[3]
                session["apellido2"]=row[4]
                session["genero"]=row[5]
                session["fecha_nacimiento"]=row[7]
                session["edad"]=row[28]
                session["correo"]=row[7]
                session["identificacion"]=row[8]
                session["direccion"]=row[9]
                session["barrio"]=row[10]
                session["ciudad"]=row[11]
                session["departamento"]=row[12]
                session["pais"]=row[13]
                session["telefono"]=row[14]
                session["celular"]=row[15]
                session["habilidades"]=row[16]
                session["profesion"]=row[17]
                session["cargo"]=row[18]
                session["institucion"]=row[19]
                session["posgrado"]=row[20]
                session["entidad_salud"]=row[21]
                session["tipo_sangre"]=row[22]
                session["foto"]=row[23]
                session["nombre_contacto"]=row[24]
                session["numero_contacto"]=row[25]
                                
                return redirect(url_for('inicio'))
            else:
                error = 'Usuario o contraseña incorrecta'
                return render_template('login/login.html', error=error, campos=request.form)
        else:
            error = 'Usuario o contraseña incorrecta'
            return render_template('login/login.html', error=error, campos=request.form)
    else:
        user = 'daniel'
        return render_template('login/login.html')
    



"""@app.route('/', methods=['GET', 'POST'])
def login():
    usuario = {}
    if request.method == 'POST':
        # Validar credenciales de usuario
        username = request.form['username']
        _password = request.form['password']

        conexion = mysql.connect()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM general_users WHERE usuario = %s", (username,))
        row = cursor.fetchone()
        usuario = row
        usuario_json = json.dumps(usuario)
        conexion.close()
        
        # Comprobar que el usuario existe en la base de datos
        # y que la contraseña es correcta
        
        if row is not None:
            hashed_password = bcrypt.hashpw(_password.encode('utf-8'), bcrypt.gensalt())
            if bcrypt.checkpw(_password.encode('utf-8'), hashed_password):
                session["login"] = True
                session["usuario"] = row
                
                return redirect(url_for('inicio')+ '?usuario=' + usuario_json)
            else:
                error = 'Usuario o contraseña incorrecta'
                return render_template('login/login.html', error=error)
        else:
            error = 'Usuario o contraseña incorrecta'
            return render_template('login/login.html', error=error)
    else:
        return render_template('login/login.html')"""

"""@app.route('/', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        # Validar credenciales de usuario
        username = request.form['username']
        _password = request.form['password']
        

        conexion=mysql.connect()
        cursor=conexion.cursor()
        cursor.execute("SELECT usuario, Nombre, Apellido FROM general_users WHERE usuario = %s", (username))
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
        user = 'daniel'
        return render_template('login/login.html')"""