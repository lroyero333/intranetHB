from main.app import app, request,bcrypt,mysql,redirect, render_template, url_for,session

eventos = [
    {
        'titulo': 'Descanso',
        'fecha_inicio': '2023-03-10',
        'fecha_fin': '2023-03-12',
        'color': '#DC143C'
    },
    {
        'titulo': 'Permiso de trabajo',
        'fecha_inicio': '2023-03-15',
        'fecha_fin': '2023-03-16',
        'color': '#FFD700'
    }
]

@app.route('/reservas')
def mostrar_reservas():
    conn = mysql.connect()
    c = conn.cursor()
    c.execute('SELECT * FROM reservas')
    reservas = c.fetchall()
    conn.close()
    return render_template('reservas.html', reservas=reservas)

@app.route('/reservar', methods=['POST'])
def procesar_reserva():
    nombre = request.form['nombre']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    conn = mysql.connect()
    c = conn.cursor()
    c.execute('INSERT INTO reservas (nombre, fecha_inicio, fecha_fin) VALUES (?, ?, ?)', (nombre, fecha_inicio, fecha_fin))
    conn.commit()
    conn.close()
    return redirect('mostrar_reservas.html')


@app.route('/calendario')
def calendario():
    if not 'login' in session:
        return redirect('/login')
    return render_template('calendario/calendarioInterac.html',eventos=eventos)