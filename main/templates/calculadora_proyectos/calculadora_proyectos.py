import datetime
import json
import os
from random import sample

from flask import send_file
from werkzeug.utils import secure_filename

from main.routes import (app, bcrypt, mysql, redirect, render_template,
                         request, session, url_for)
from main.run import (app, bcrypt, flash, jsonify, mysql, redirect,
                      render_template, request, session, url_for, generarID, constantes, fecha_actualCO)

extensionesImagenes = ['.jpg', '.jpeg', '.png']

@app.route('/calculadoraProyectos', methods=['POST', 'GET'])
def calculadoraProyectos():
    if not 'login' in session:
        return redirect('/')
    
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
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
        'fecha_registro': dataAdmin[9],
        'num_proyectos_activos': 0
    }
    cursor.execute("SELECT COUNT(*) FROM proyectos AS p WHERE p.activo = 1;")
    #Se suma 1 porque, si tenemos 0 proyectos activos, la división del costo administrativo sería en 0 también.
    #Además de que es mejor mostrar el costo si el proyecto que se está planeando se tomara como activo también
    ultimaInfoAdmin['num_proyectos_activos'] = cursor.fetchone()[0] + 1

    if request.method == 'POST':
        #print(request.form.keys())
        proyectoId = generarID()
        nombreProyecto = request.form['nombre_proyecto']
        imagenProyecto = ''
        descripcionProyecto = request.form['desc_proyecto']
        activo = 0
        proyectoDuracion = request.form['dias_totales_sinReserva']
        proyectoDiasExtra = request.form['dias_totales_num']
        proyecccionMatProt = request.form['costo_matProt']
        proyeccionMaqTerc = request.form['costo_maqTerc']
        proyeccionSoft = request.form['costo_softAd']
        proyeccionTec = request.form['costo_maqAd']
        proyeccionRentabilidad = request.form['porcentaje_retorno']
        idAdminInfo = ultimaInfoAdmin['id']

        query = "INSERT INTO proyectos (id_proyecto, nombre_proyecto, imagen_proyecto, descripcion_proyecto, activo, proyecto_duracion, proyecto_dias_extra, proyeccion_mat_prot, proyeccion_maq_terc, proyeccion_soft, proyeccion_tec, proyeccion_rentabilidad, id_informacion_administrativa) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [proyectoId, nombreProyecto, imagenProyecto, descripcionProyecto, activo,
                    proyectoDuracion, proyectoDiasExtra, proyecccionMatProt, proyeccionMaqTerc, proyeccionSoft,
                    proyeccionTec, proyeccionRentabilidad, idAdminInfo]
        cursor.execute(query, params)

        actividadNombre = ''
        actividadDepartamento = ''
        actividadDuracion = 0
        actividadColaboradores = 0

        actividades = []

        for key in request.form.keys():
            #print('{}: {}'.format(key, request.form[key]))
            if(key.find('actividad') != -1):
                if (key.find('nombre') != -1):
                    actividadNombre = request.form[key]
                if (key.find('departamentoPicker') != -1):
                    deptNombre = request.form[key]
                    if(deptNombre == 'robElectColab'):
                        actividadDepartamento = constantes['id_dept_robElect']
                        actividadColaboradores = request.form['dept_robElect_colab']
                    elif(deptNombre == 'disPubColab'):
                        actividadDepartamento = constantes['id_dept_disPub']
                        actividadColaboradores = request.form['dept_disPub_colab']
                    elif(deptNombre == 'biomedColab'):
                        actividadDepartamento = constantes['id_dept_biomedica']
                        actividadColaboradores = request.form['dept_biomed_colab']
                    elif(deptNombre == 'indsProtColab'):
                        actividadDepartamento = constantes['id_dept_indProt']
                        actividadColaboradores = request.form['dept_indsProt_colab']
                    elif(deptNombre == 'sisProgColab'):
                        actividadDepartamento = constantes['id_dept_sisProg']
                        actividadColaboradores = request.form['dept_sisProg_colab']
                if(key.find('tiempo') != -1):
                    actividadDuracion = request.form[key]
                if(key.find('tipoTiempoPicker') != -1):
                    tipoTiempo = request.form[key]
                    if(tipoTiempo == 's'):
                        #Está en semanas el tiempo, por lo que se multiplica por 5 para obtener los días
                        actividadDuracion = float(actividadDuracion) * 5
                    actividades.append((generarID(), actividadNombre, actividadDuracion, actividadColaboradores, proyectoId, actividadDepartamento))
                    
        query = "INSERT INTO proyecto_actividad (id_proyecto_actividad, nombre, duracion, num_colaboradores, id_proyecto, id_departamento) VALUES (%s,%s,%s,%s,%s,%s)"
        cursor.executemany(query, actividades)
        conexion.commit()
        
        return redirect('/listaProyectos')
    elif request.method == 'GET':
        return render_template('calculadora_proyectos/templates/estimacionCostos.html', datos_admin=ultimaInfoAdmin)
    else:
        print("Método no permitido: " + request.method)
        return redirect('/')

@app.route('/registroCostos/rrhh/<string:p_id>', methods=['PUT', 'GET'])
def registroCosto_rrhh(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if (request.method == 'PUT'):
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
            'fecha_registro': dataAdmin[9],
            'num_proyectos_activos': 0
        }
        cursor.execute("SELECT COUNT(*) FROM proyectos AS p WHERE p.activo = 1;")
        ultimaInfoAdmin['num_proyectos_activos'] = cursor.fetchone()[0] + 1
        cursor.execute("SELECT num_mes FROM proyectos WHERE id_proyecto = %s;", ((p_id)))
        mesActual = cursor.fetchone()
        if mesActual is None:
            mesActual = 1
        else:
            mesActual = mesActual[0] + 1

        cursor.execute("UPDATE proyectos SET num_mes = %s WHERE id_proyecto = %s;", ((mesActual, p_id)))

        datos = request.json
        costos = []
        fechaActual = fecha_actualCO()
        for key in datos['rrhh'].keys():
            departamentoId = ''
            if(key == 'robElect'):
                departamentoId = constantes['id_dept_robElect']
            elif(key == 'disPub'):
                departamentoId = constantes['id_dept_disPub']
            elif(key == 'biomedica'):
                departamentoId = constantes['id_dept_biomedica']
            elif(key == 'indProt'):
                departamentoId = constantes['id_dept_indProt']
            elif(key == 'sisProg'):
                departamentoId = constantes['id_dept_sisProg']
            costos.append((generarID(), fechaActual, datos['rrhh'][key], p_id, ultimaInfoAdmin['id'], departamentoId))  
        #Costos administrativos
        costos.append((generarID(), fechaActual, 160, p_id, ultimaInfoAdmin['id'], constantes['id_admin']))
        query = "INSERT INTO costos_rrhh_proyectos (id_costos_rrhh_proyectos, fecha_registro, horas, id_proyecto, id_informacion_administrativa, id_departamento) VALUES (%s,%s,%s,%s,%s,%s)"
        cursor.executemany(query, costos)

        query = "INSERT INTO costos_mat_proyectos (id_costos_mat_proyectos, fecha_registro, materiales_prototipos, maquila_terceros, software_adicional, tecnologia_adicional, id_proyecto, id_informacion_administrativa) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (generarID(), fechaActual, datos['materiales']['matProt'], datos['materiales']['maqTerc'], datos['materiales']['softAd'], datos['materiales']['tec'], p_id, ultimaInfoAdmin['id']))
        conexion.commit()
        return({'response': 'success'})
    elif(request.method == 'GET'):
        query = '''
                SELECT
                    SUM(c_rrhh.horas *
                        CASE(dept.nombre)
                            WHEN 'Sistemas y Programación' THEN infoAdm.salario_sis_prog
                            WHEN 'Biomédica' THEN infoAdm.salario_biomedica
                            WHEN 'Robótica y Electrónica' THEN infoAdm.salario_rob_elect
                            WHEN 'Industrial y Prototipado' THEN infoAdm.salario_ind_prot
                            WHEN 'Diseño y Publicidad' THEN infoAdm.salario_dis_pub
                            WHEN 'Administracion' THEN (infoAdm.costo_administrativo / (SELECT COUNT(*) FROM proyectos WHERE activo = 1))
                            ELSE 0
                        END) AS costo,
                    c_rrhh.fecha_registro
                FROM costos_rrhh_proyectos AS c_rrhh
                JOIN departamentos AS dept on c_rrhh.id_departamento = dept.id_departamento
                JOIN informacion_administrativa AS infoAdm ON c_rrhh.id_informacion_administrativa = infoAdm.id_informacion_administrativa
                WHERE c_rrhh.id_proyecto = %s
                GROUP BY c_rrhh.fecha_registro
                ORDER BY c_rrhh.fecha_registro
            '''
        cursor.execute(query, (p_id))
        costosMensuales_rrhh = cursor.fetchall()

        query = '''
            SELECT (c_mat.materiales_prototipos + c_mat.maquila_terceros +
                    c_mat.software_adicional + c_mat.tecnologia_adicional + (infoAdm.costo_locativos * 20) + (infoAdm.costo_maquinaria * 20)) AS costo,
                    c_mat.fecha_registro
            FROM costos_mat_proyectos AS c_mat
            JOIN informacion_administrativa AS infoAdm ON c_mat.id_informacion_administrativa = infoAdm.id_informacion_administrativa
            WHERE c_mat.id_proyecto = %s
            ORDER BY c_mat.fecha_registro;
        '''
        cursor.execute(query, (p_id))
        costosMensuales_mat = cursor.fetchall()

        return({'costos_rrhh': costosMensuales_rrhh, 'costos_mat': costosMensuales_mat})
    return redirect('/')



    

@app.route('/registroCostos/<string:p_id>', methods=['GET'])
def registroCostos(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    queryProyecto = '''
        SELECT
            p.*, SUM(8 * pa.duracion * pa.num_colaboradores *
                CASE(dept.nombre)
                    WHEN 'Sistemas y Programación' THEN infoAdm.salario_sis_prog
                    WHEN 'Biomédica' THEN infoAdm.salario_biomedica
                    WHEN 'Robótica y Electrónica' THEN infoAdm.salario_rob_elect
                    WHEN 'Industrial y Prototipado' THEN infoAdm.salario_ind_prot
                    WHEN 'Diseño y Publicidad' THEN infoAdm.salario_dis_pub
                    ELSE 0
                END
            )
            + (infoAdm.costo_administrativo * p.proyecto_duracion * 8 /(
                    SELECT
                        CASE
                            WHEN COUNT(*) = 0 THEN  1
                            ELSE (COUNT(*))
                        END
                FROM proyectos AS pActivos WHERE pActivos.activo = 1)
                )
            AS costo_rrhh,
            (infoAdm.costo_locativos * p.proyecto_duracion) AS costo_loc,
            (infoAdm.costo_maquinaria * p.proyecto_duracion)  AS costo_maq
        FROM proyectos AS p
        JOIN proyecto_actividad AS pa ON p.id_proyecto = pa.id_proyecto
        JOIN informacion_administrativa as infoAdm ON p.id_informacion_administrativa = infoAdm.id_informacion_administrativa
        JOIN departamentos as dept on pa.id_departamento = dept.id_departamento
        WHERE p.activo = 1 AND p.id_proyecto = %s;
    '''
    queryCostos_fijos = '''
    SELECT ((infoAdm.costo_administrativo * 8 * 20) / (SELECT
                            CASE
                                WHEN COUNT(*) = 0 THEN  1
                                ELSE COUNT(*)
                            END
                    FROM proyectos AS pActivos WHERE pActivos.activo = 1)) AS costo_admin_mensual,
        (infoAdm.costo_locativos * 20) AS costo_locativo_mensual,
        (infoAdm.costo_maquinaria * 20) AS costo_maquinaria_mensual
    FROM informacion_administrativa AS infoAdm
    WHERE infoAdm.id_informacion_administrativa = %s;
    '''
    queryCostos_fijosUltimo = '''
    SELECT ((infoAdm.costo_administrativo * 8 * 20) / (SELECT
                            CASE
                                WHEN COUNT(*) = 0 THEN  1
                                ELSE COUNT(*)
                            END
                    FROM proyectos AS pActivos WHERE pActivos.activo = 1)) AS costo_admin_mensual,
        (infoAdm.costo_locativos * 20) AS costo_locativo_mensual,
        (infoAdm.costo_maquinaria * 20) AS costo_maquinaria_mensual
    FROM informacion_administrativa AS infoAdm
    ORDER BY fecha_registro DESC LIMIT 1;
    '''
    queryCostos_rrhh = '''
    SELECT
        SUM(c_rrhh.horas *
            CASE(dept.nombre)
                WHEN 'Sistemas y Programación' THEN infoAdm.salario_sis_prog
                WHEN 'Biomédica' THEN infoAdm.salario_biomedica
                WHEN 'Robótica y Electrónica' THEN infoAdm.salario_rob_elect
                WHEN 'Industrial y Prototipado' THEN infoAdm.salario_ind_prot
                WHEN 'Diseño y Publicidad' THEN infoAdm.salario_dis_pub
                WHEN 'Administracion' THEN (infoAdm.costo_administrativo / (SELECT COUNT(*) FROM proyectos WHERE activo = 1))
                ELSE 0
            END) AS costo,
        c_rrhh.fecha_registro
    FROM costos_rrhh_proyectos AS c_rrhh
    JOIN departamentos AS dept on c_rrhh.id_departamento = dept.id_departamento
    JOIN informacion_administrativa AS infoAdm ON c_rrhh.id_informacion_administrativa = infoAdm.id_informacion_administrativa
    WHERE c_rrhh.id_proyecto = %s
    GROUP BY c_rrhh.fecha_registro
    '''
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(queryProyecto, (p_id))
    datosProyecto = cursor.fetchone();

    cursor.execute(queryCostos_rrhh, (p_id))
    datosCostos_rrhh = cursor.fetchall();

    proyectoDic = {
        'id_proyecto': datosProyecto[0],
        'nombre_proyecto': datosProyecto[1],
        'descripcion_proyecto': datosProyecto[3],
        'num_mes': datosProyecto[5],
        'fecha_inicio': datosProyecto[6],
        'proyecto_duracion': datosProyecto[7],
        'proyecto_dias_extra': datosProyecto[8],
        'proyeccion_mat_prot': datosProyecto[9],
        'proyeccion_maq_terc': datosProyecto[10],
        'proyeccion_soft': datosProyecto[11],
        'proyeccion_tec': datosProyecto[12],
        'proyeccion_rentabilidad': datosProyecto[13],
        'id_informacion_administrativa': datosProyecto[14],
        'costo_rrhh': datosProyecto[15],
        'costo_loc': datosProyecto[16],
        'costo_maq': datosProyecto[17]
    }

    cursor.execute(queryCostos_fijos, (proyectoDic['id_informacion_administrativa']))
    datosCostosFijos = cursor.fetchone()
    costosFijosDic = {
        'costo_admin_mensual': datosCostosFijos[0],
        'costo_locativo_mensual': datosCostosFijos[1],
        'costo_maquinaria_mensual': datosCostosFijos[2]
    }

    cursor.execute(queryCostos_fijosUltimo)
    datosCostosFijos_Ultimo = cursor.fetchone()
    costosFijosUltimoDic = {
        'costo_admin_mensual': datosCostosFijos_Ultimo[0],
        'costo_locativo_mensual': datosCostosFijos_Ultimo[1],
        'costo_maquinaria_mensual': datosCostosFijos_Ultimo[2]
    }

    return render_template('calculadora_proyectos/templates/registroCostos.html', datosProyecto=proyectoDic, datosCostos_rrhh=datosCostos_rrhh, datosCostos_fijos=costosFijosDic, datosCostos_fijosUltimo = costosFijosUltimoDic)

@app.route('/inicializarDatos')
def inicializarDatosPagina():
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    return render_template('calculadora_proyectos/templates/inicializarDatos.html')

@app.route('/activarProyecto/<string:p_id>')
def activarProyecto(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute('UPDATE proyectos SET activo = 1 WHERE id_proyecto = %s;', (p_id))
    conexion.commit()
    return redirect('/listaProyectos')

@app.route('/desactivarProyecto/<string:p_id>')
def desactivarProyecto(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute('UPDATE proyectos SET activo = 0 WHERE id_proyecto = %s;', (p_id))
    conexion.commit()
    return redirect('/listaProyectos')

@app.route('/eliminarProyecto/<string:p_id>')
def eliminarProyecto(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute('DELETE FROM proyectos WHERE id_proyecto = %s;', (p_id))
    conexion.commit()
    return redirect('/listaProyectos')

@app.route('/listaProyectos')
def listaProyectos():
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    queryProyectosInactivos = '''
        SELECT
            p.*, SUM(8 * pa.duracion * pa.num_colaboradores *
                CASE(dept.nombre)
                    WHEN 'Sistemas y Programación' THEN infoAdm.salario_sis_prog
                    WHEN 'Biomédica' THEN infoAdm.salario_biomedica
                    WHEN 'Robótica y Electrónica' THEN infoAdm.salario_rob_elect
                    WHEN 'Industrial y Prototipado' THEN infoAdm.salario_ind_prot
                    WHEN 'Diseño y Publicidad' THEN infoAdm.salario_dis_pub
                    ELSE 0
                END
            )
            + (infoAdm.costo_administrativo * p.proyecto_duracion * 8 /(
                    SELECT
                        CASE
                            WHEN COUNT(*) = 0 THEN  1
                            ELSE (COUNT(*) + 1)
                        END
                FROM proyectos AS pActivos WHERE pActivos.activo = 1)
                )
            AS costo_rrhh,
            (infoAdm.costo_locativos * p.proyecto_duracion) AS costo_loc,
            (infoAdm.costo_maquinaria * p.proyecto_duracion)  AS costo_maq
        FROM proyectos AS p
        JOIN proyecto_actividad AS pa ON p.id_proyecto = pa.id_proyecto
        JOIN informacion_administrativa as infoAdm ON p.id_informacion_administrativa = infoAdm.id_informacion_administrativa
        JOIN departamentos as dept on pa.id_departamento = dept.id_departamento
        WHERE p.activo = 0
        GROUP BY p.id_proyecto;
    '''
    queryProyectosActivos = '''
        SELECT
            p.*, SUM(8 * pa.duracion * pa.num_colaboradores *
                CASE(dept.nombre)
                    WHEN 'Sistemas y Programación' THEN infoAdm.salario_sis_prog
                    WHEN 'Biomédica' THEN infoAdm.salario_biomedica
                    WHEN 'Robótica y Electrónica' THEN infoAdm.salario_rob_elect
                    WHEN 'Industrial y Prototipado' THEN infoAdm.salario_ind_prot
                    WHEN 'Diseño y Publicidad' THEN infoAdm.salario_dis_pub
                    ELSE 0
                END
            )
            + (infoAdm.costo_administrativo * p.proyecto_duracion * 8 /(
                    SELECT
                        CASE
                            WHEN COUNT(*) = 0 THEN  1
                            ELSE (COUNT(*))
                        END
                FROM proyectos AS pActivos WHERE pActivos.activo = 1)
                )
            AS costo_rrhh,
            (infoAdm.costo_locativos * p.proyecto_duracion) AS costo_loc,
            (infoAdm.costo_maquinaria * p.proyecto_duracion)  AS costo_maq,
            (
                SELECT
                    SUM(c_rrhh.horas *
                        CASE(dept.nombre)
                            WHEN 'Sistemas y Programación' THEN infoAdm.salario_sis_prog
                            WHEN 'Biomédica' THEN infoAdm.salario_biomedica
                            WHEN 'Robótica y Electrónica' THEN infoAdm.salario_rob_elect
                            WHEN 'Industrial y Prototipado' THEN infoAdm.salario_ind_prot
                            WHEN 'Diseño y Publicidad' THEN infoAdm.salario_dis_pub
                            WHEN 'Administracion' THEN (infoAdm.costo_administrativo / (SELECT COUNT(*) FROM proyectos WHERE activo = 1))
                            ELSE 0
                        END) AS costo
                FROM costos_rrhh_proyectos AS c_rrhh
                JOIN departamentos AS dept on c_rrhh.id_departamento = dept.id_departamento
                JOIN informacion_administrativa AS infoAdm ON c_rrhh.id_informacion_administrativa = infoAdm.id_informacion_administrativa
                WHERE c_rrhh.id_proyecto = p.id_proyecto
            ) AS costo_rrhh_ejecutado,
            (
                SELECT (SUM(c_mat.materiales_prototipos + c_mat.maquila_terceros + c_mat.software_adicional + c_mat.tecnologia_adicional +
                        20 * infoAdm.costo_locativos + 20 * infoAdm.costo_maquinaria)) AS costo_mat_ejecutado
                FROM costos_mat_proyectos AS c_mat
                JOIN informacion_administrativa AS infoAdm ON infoAdm.id_informacion_administrativa = c_mat.id_informacion_administrativa
                WHERE c_mat.id_proyecto = p.id_proyecto
            ) AS costo_mat_ejecutado
        FROM proyectos AS p
        JOIN proyecto_actividad AS pa ON p.id_proyecto = pa.id_proyecto
        JOIN informacion_administrativa AS infoAdm ON p.id_informacion_administrativa = infoAdm.id_informacion_administrativa
        JOIN departamentos as dept on pa.id_departamento = dept.id_departamento
        WHERE p.activo = 1
        GROUP BY p.id_proyecto;
    '''
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(queryProyectosInactivos)
    listaProyectosInactivos = cursor.fetchall()
    cursor.execute(queryProyectosActivos)
    listaProyectosActivos = cursor.fetchall()
    return render_template('calculadora_proyectos/templates/listaProyectos.html', pInactivos=listaProyectosInactivos, pActivos=listaProyectosActivos)


# LISTA_DEPARTAMENTOS = ['Robótica y Electrónica', 'Diseño y Publicidad', 'Biomédica', 'Industrial y Prototipado', 'Sistemas y Programación']
LISTA_DEPARTAMENTOS = ['Administración']

@app.route('/adminTools', methods=['POST'])
def prueba():
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()

    for name in LISTA_DEPARTAMENTOS:
        query = "INSERT INTO departamentos (id_departamento, nombre) VALUES (%s,%s)"
        params = [generarID(), name]
        cursor.execute(query, params)
    conexion.commit()

    msg = 'Datos de departamentos inicializados'

    returnData = {
        'respuesta': msg
    }

    print(msg)
    return jsonify(returnData)
