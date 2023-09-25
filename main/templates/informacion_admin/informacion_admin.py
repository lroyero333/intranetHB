import datetime
import json
import os
from random import sample

from flask import send_file
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (app, bcrypt, flash, jsonify, mysql, redirect,
                      render_template, request, session, url_for, generarID, constantes, fecha_actualCO, quitarFormatoDinero)

extensionesImagenes = ['.jpg', '.jpeg', '.png']

@app.route('/informacionAdmin', methods=['GET','POST'])
def informacionAdmin():
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    print('---------------------------------------------------')
    print(request.method)
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if(request.method == 'GET'):
        cursor.execute("SELECT * FROM informacion_administrativa ORDER BY fecha_registro DESC LIMIT 1;")
        dataAdmin = cursor.fetchone()
        ultimaInfoAdmin = {
            'id': dataAdmin[0],
            'costo_admin': dataAdmin[1],
            'costo_loc': dataAdmin[2],
            'costo_maq': dataAdmin[3],
            'salario_rob_elect': dataAdmin[4],
            'salario_dis_pub': dataAdmin[5],
            'salario_biomedica': dataAdmin[6],
            'salario_ind_prot': dataAdmin[7],
            'salario_sis_prog': dataAdmin[8],
            'fecha_registro': dataAdmin[9]
        }
    elif(request.method == 'POST'):
        datos = request.json['data']
        print(datos)
        fechaActual = fecha_actualCO()
        query = 'INSERT INTO informacion_administrativa (id_informacion_administrativa, costo_administrativo, costo_locativos, costo_maquinaria, salario_rob_elect, salario_dis_pub, salario_biomedica, salario_ind_prot, salario_sis_prog, fecha_registro) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query, (generarID(), datos['salarioAdmin'], datos['costoLoc'], datos['costoMaq'], datos['salarioRobElect'], datos['salarioDisPub'], datos['salarioBio'], datos['salarioIndProt'], datos['salarioSisProg'], fechaActual))
        conexion.commit()
        cursor.execute("SELECT * FROM informacion_administrativa ORDER BY fecha_registro DESC LIMIT 1;")
        dataAdmin = cursor.fetchone()
        ultimaInfoAdmin = {
            'id': dataAdmin[0],
            'costo_admin': dataAdmin[1],
            'costo_loc': dataAdmin[2],
            'costo_maq': dataAdmin[3],
            'salario_rob_elect': dataAdmin[4],
            'salario_dis_pub': dataAdmin[5],
            'salario_biomedica': dataAdmin[6],
            'salario_ind_prot': dataAdmin[7],
            'salario_sis_prog': dataAdmin[8],
            'fecha_registro': dataAdmin[9]
        }
    
    return render_template('informacion_admin/templates/informacionAdmin.html', datos_admin=ultimaInfoAdmin)
