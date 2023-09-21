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
        proyecccionMatProt = float(quitarFormatoDinero(request.form['costo_matProt'])) if request.form['costo_matProt'] else 0.0
        proyeccionMaqTerc = float(quitarFormatoDinero(request.form['costo_maqTerc'])) if request.form['costo_maqTerc'] else 0.0
        proyeccionSoft = float(quitarFormatoDinero(request.form['costo_softAd'])) if request.form['costo_softAd'] else 0.0
        proyeccionTec = float(quitarFormatoDinero(request.form['costo_maqAd'])) if request.form['costo_maqAd'] else 0.0
        proyeccionRentabilidad = float(request.form['porcentaje_retorno']) if request.form['porcentaje_retorno'] else 0.0
        idAdminInfo = ultimaInfoAdmin['id']

        query = "INSERT INTO proyectos (id_proyecto, nombre_proyecto, imagen_proyecto, descripcion_proyecto, activo, proyecto_duracion, proyecto_dias_extra, proyeccion_mat_prot, proyeccion_maq_terc, proyeccion_soft, proyeccion_tec, proyeccion_rentabilidad, id_informacion_administrativa) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [proyectoId, nombreProyecto, imagenProyecto, descripcionProyecto, activo,
                    proyectoDuracion, proyectoDiasExtra, proyecccionMatProt, proyeccionMaqTerc, proyeccionSoft,
                    proyeccionTec, proyeccionRentabilidad, idAdminInfo]
        cursor.execute(query, params)

        agregarActividadFlag = False
        actividadNombre = ''
        actividadIdActiva = ''

        actividadDepartamento = ''
        actividadDuracion = 0
        actividadColaboradores = 0

        actividades = []
        actividadesDetalles = []

        for key in request.form.keys():
            #print('{}: {}'.format(key, request.form[key]))
            if(key.find('actividad') != -1):
                if (key.find('nombre') != -1):
                    actividadNombre = request.form[key]
                    actividadIdActiva = generarID()
                    actividades.append((actividadIdActiva, actividadNombre, proyectoId))
                if (key.find('checkbox') != -1 and request.form[key] == 'on'):
                    agregarActividadFlag = True
                    deptNombre = key.split('-')[-1]
                    if(deptNombre == 'robElect'):
                        actividadDepartamento = constantes['id_dept_robElect']
                        actividadColaboradores = request.form['dept_robElect_colab']
                    elif(deptNombre == 'disPub'):
                        actividadDepartamento = constantes['id_dept_disPub']
                        actividadColaboradores = request.form['dept_disPub_colab']
                    elif(deptNombre == 'biomed'):
                        actividadDepartamento = constantes['id_dept_biomedica']
                        actividadColaboradores = request.form['dept_biomed_colab']
                    elif(deptNombre == 'indsProt'):
                        actividadDepartamento = constantes['id_dept_indProt']
                        actividadColaboradores = request.form['dept_indsProt_colab']
                    elif(deptNombre == 'sisProg'):
                        actividadDepartamento = constantes['id_dept_sisProg']
                        actividadColaboradores = request.form['dept_sisProg_colab']
                if(key.find('tiempo-departamento') != -1):
                    actividadDuracion = request.form[key]
                if(key.find('tiempo-tipoTiempoPicker') != -1):
                    tipoTiempo = request.form[key]
                    if(tipoTiempo == 's'):
                        #Está en semanas el tiempo, por lo que se multiplica por 5 para obtener los días
                        actividadDuracion = float(actividadDuracion) * 5
                    if(agregarActividadFlag):
                        actividadesDetalles.append((generarID(), actividadColaboradores, actividadDuracion, actividadIdActiva, actividadDepartamento))
                        agregarActividadFlag = False
                    
        query = "INSERT INTO proyecto_actividad (id_proyecto_actividad, nombre, id_proyecto) VALUES (%s,%s,%s)"
        cursor.executemany(query, actividades)
        query = "INSERT INTO proyecto_actividad_detalles (id_proyecto_actividad_detalles, num_colaboradores, duracion, id_proyecto_actividad, id_departamento) VALUES (%s,%s,%s,%s,%s)"
        cursor.executemany(query, actividadesDetalles)
        conexion.commit()
        
        return redirect('/listaProyectos')
    elif request.method == 'GET':
        return render_template('calculadora_proyectos/templates/estimacionCostos.html', datos_admin=ultimaInfoAdmin)
    else:
        print("Método no permitido: " + request.method)
        return redirect('/')
    
@app.route('/registroCostos/rrhh/<string:p_id>/<string:c_rrhh_id>', methods=['PUT', 'GET'])
def registroCosto_rrhh(p_id, c_rrhh_id):
    pass

@app.route('/registroCostos/rrhh/<string:p_id>', methods=['POST', 'GET'])
def registroCosto_rrhh(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if (request.method == 'POST'):
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
        ultimaInfoAdmin['num_proyectos_activos'] = cursor.fetchone()[0]
        # cursor.execute("SELECT num_mes FROM proyectos WHERE id_proyecto = %s;", ((p_id)))
        # mesActual = cursor.fetchone()
        # if mesActual is None:
        #     mesActual = 1
        # else:
        #     mesActual = mesActual[0] + 1

        # cursor.execute("UPDATE proyectos SET num_mes = %s WHERE id_proyecto = %s;", ((mesActual, p_id)))

        datos = request.json
        # costos = []
        fechaActual = fecha_actualCO()
        # for key in datos['rrhh'].keys():
        #     departamentoId = ''
        #     if(key == 'robElect'):
        #         departamentoId = constantes['id_dept_robElect']
        #     elif(key == 'disPub'):
        #         departamentoId = constantes['id_dept_disPub']
        #     elif(key == 'biomedica'):
        #         departamentoId = constantes['id_dept_biomedica']
        #     elif(key == 'indProt'):
        #         departamentoId = constantes['id_dept_indProt']
        #     elif(key == 'sisProg'):
        #         departamentoId = constantes['id_dept_sisProg']
        #     costos.append((generarID(), fechaActual, datos['rrhh'][key], p_id, ultimaInfoAdmin['id'], departamentoId))  
        # #Costos administrativos
        # costos.append((generarID(), fechaActual, (160/ultimaInfoAdmin['num_proyectos_activos']), p_id, ultimaInfoAdmin['id'], constantes['id_admin']))
        query = "INSERT INTO costos_rrhh_proyectos (id_costos_rrhh_proyectos, fecha_registro, horas_sistemas, horas_biomedica, horas_robotica, horas_industrial, horas_diseno, horas_admin, id_proyecto, id_informacion_administrativa) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        print(datos['rrhh'])
        cursor.execute(query, (generarID(), fechaActual, datos['rrhh']['sisProg'], datos['rrhh']['biomedica'], datos['rrhh']['robElect'], datos['rrhh']['indProt'], datos['rrhh']['disPub'], (160/ultimaInfoAdmin['num_proyectos_activos']), p_id, ultimaInfoAdmin['id']))

        conexion.commit()
        return({'response': 'success'})
    elif(request.method == 'GET'):
        query = '''
                SELECT c_rrhh.id_costos_rrhh_proyectos, c_rrhh.fecha_registro, c_rrhh.horas_sistemas, infoAdm.salario_sis_prog,
                    c_rrhh.horas_biomedica, infoAdm.salario_biomedica, c_rrhh.horas_robotica, infoAdm.salario_rob_elect,
                    c_rrhh.horas_industrial, infoAdm.salario_ind_prot, c_rrhh.horas_diseno, infoAdm.salario_dis_pub, c_rrhh.horas_admin,
                    infoAdm.costo_administrativo
                FROM costos_rrhh_proyectos AS c_rrhh
                JOIN informacion_administrativa AS infoAdm ON c_rrhh.id_informacion_administrativa = infoAdm.id_informacion_administrativa
                WHERE c_rrhh.id_proyecto = %s
                ORDER BY c_rrhh.fecha_registro;
            '''
        cursor.execute(query, (p_id))
        costosMensuales_rrhh_datos = cursor.fetchall()
        costosMensuales_rrhh = []

        for data in costosMensuales_rrhh_datos:
            costosMensuales_rrhh.append({
                'id_costos_rrhh_proyectos': data[0],
                'fecha_registro': data[1],
                'horas_sistemas': data[2],
                'salario_sis_prog': data[3],
                'horas_biomedica': data[4],
                'salario_biomedica': data[5],
                'horas_robotica': data[6],
                'salario_rob_elect': data[7],
                'horas_industrial': data[8],
                'salario_ind_prot': data[9],
                'horas_diseno': data[10],
                'salario_dis_pub': data[11],
                'horas_admin': data[12],
                'costo_administrativo': data[13]
            })

        return({'costos_rrhh': costosMensuales_rrhh})
    return redirect('/')

@app.route('/registroCostos/mat/<string:p_id>', methods=['POST', 'GET'])
def registroCosto_mat(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if (request.method == 'POST'):
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
        ultimaInfoAdmin['num_proyectos_activos'] = cursor.fetchone()[0]
        # cursor.execute("SELECT num_mes FROM proyectos WHERE id_proyecto = %s;", ((p_id)))
        # mesActual = cursor.fetchone()
        # if mesActual is None:
        #     mesActual = 1
        # else:
        #     mesActual = mesActual[0] + 1

        # cursor.execute("UPDATE proyectos SET num_mes = %s WHERE id_proyecto = %s;", ((mesActual, p_id)))

        fechaActual = fecha_actualCO()
        datos = request.json
        query = "INSERT INTO costos_mat_proyectos (id_costos_mat_proyectos, fecha_registro, materiales_prototipos, maquila_terceros, software_adicional, tecnologia_adicional, num_proyectos_activos, id_proyecto, id_informacion_administrativa) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (generarID(), fechaActual, datos['materiales']['matProt'], datos['materiales']['maqTerc'], datos['materiales']['softAd'], datos['materiales']['tec'], ultimaInfoAdmin['num_proyectos_activos'], p_id, ultimaInfoAdmin['id']))
        conexion.commit()
        return({'response': 'success'})
    elif(request.method == 'GET'):
        query = '''
            SELECT c_mat.id_costos_mat_proyectos, c_mat.materiales_prototipos, c_mat.maquila_terceros,
                c_mat.software_adicional, c_mat.tecnologia_adicional,
                (infoAdm.costo_locativos * 20)/c_mat.num_proyectos_activos AS c_loc,
                (infoAdm.costo_maquinaria * 20)/c_mat.num_proyectos_activos AS c_maq,
                c_mat.fecha_registro
            FROM costos_mat_proyectos AS c_mat
            JOIN informacion_administrativa AS infoAdm ON c_mat.id_informacion_administrativa = infoAdm.id_informacion_administrativa
            WHERE c_mat.id_proyecto = %s
            ORDER BY c_mat.fecha_registro;
        '''
        cursor.execute(query, (p_id))
        costosMensuales_mat_datos = cursor.fetchall()
        costosMensuales_mat = []
        
        for data in costosMensuales_mat_datos:
            costosMensuales_mat.append({
                'id_costos_mat_proyectos': data[0],
                'materiales_prototipos': data[1],
                'maquila_terceros': data[2],
                'software_adicional': data[3],
                'tecnologia_adicional': data[4],
                'c_loc': data[5],
                'c_maq': data[6],
                'fecha_registro': data[7]
            })
        return({'costos_mat': costosMensuales_mat})
    return redirect('/')



    

@app.route('/registroCostos/<string:p_id>', methods=['GET'])
def registroCostos(p_id):
    if not 'login' in session:
        return redirect('/')
    if session['cargo'] != 1 and session['cargo'] != 0 :
        return redirect('/inicio')
    
    queryProyecto = '''
        SELECT
            p.*, SUM(8 * pad.duracion * pad.num_colaboradores *
                CASE(dept.nombre)
                    WHEN 'Sistemas y Programación' THEN infoAdm.salario_sis_prog
                    WHEN 'Biomédica' THEN infoAdm.salario_biomedica
                    WHEN 'Robótica y Electrónica' THEN infoAdm.salario_rob_elect
                    WHEN 'Industrial y Prototipado' THEN infoAdm.salario_ind_prot
                    WHEN 'Diseño y Publicidad' THEN infoAdm.salario_dis_pub
                    ELSE 0
                END
            )
            + (infoAdm.costo_administrativo * p.proyecto_duracion * 8 / (p.num_proyectos_activos + 1))
            AS costo_rrhh,
            (infoAdm.costo_locativos * p.proyecto_duracion / (p.num_proyectos_activos + 1)) AS costo_loc,
            (infoAdm.costo_maquinaria * p.proyecto_duracion / (p.num_proyectos_activos + 1))  AS costo_maq
        FROM proyectos AS p
        JOIN proyecto_actividad AS pa ON p.id_proyecto = pa.id_proyecto
        JOIN proyecto_actividad_detalles as pad ON pa.id_proyecto_actividad = pad.id_proyecto_actividad
        JOIN informacion_administrativa as infoAdm ON p.id_informacion_administrativa = infoAdm.id_informacion_administrativa
        JOIN departamentos as dept on pad.id_departamento = dept.id_departamento
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
        ((infoAdm.costo_locativos * 20) / (SELECT
                            CASE
                                WHEN COUNT(*) = 0 THEN  1
                                ELSE COUNT(*)
                            END
                    FROM proyectos AS pActivos WHERE pActivos.activo = 1)) AS costo_locativo_mensual,
        ((infoAdm.costo_maquinaria * 20) / (SELECT
                            CASE
                                WHEN COUNT(*) = 0 THEN  1
                                ELSE COUNT(*)
                            END
                    FROM proyectos AS pActivos WHERE pActivos.activo = 1)) AS costo_maquinaria_mensual
    FROM informacion_administrativa AS infoAdm
    ORDER BY fecha_registro DESC LIMIT 1;
    '''
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(queryProyecto, (p_id))
    datosProyecto = cursor.fetchone();

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
        'costo_rrhh': datosProyecto[16],
        'costo_loc': datosProyecto[17],
        'costo_maq': datosProyecto[18]
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

    return render_template('calculadora_proyectos/templates/registroCostos.html', datosProyecto=proyectoDic, datosCostos_fijos=costosFijosDic, datosCostos_fijosUltimo = costosFijosUltimoDic)

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
    cursor.execute("SELECT COUNT(*) FROM proyectos AS p WHERE p.activo = 1;")
    numProyectosActivos = cursor.fetchone()[0]
    queryUpdate = '''
        UPDATE proyectos
        SET activo = 1, num_proyectos_activos = %s
        WHERE id_proyecto = %s;
    '''
    cursor.execute(queryUpdate, (numProyectosActivos, p_id))
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
            p.*, SUM(8 * pad.duracion * pad.num_colaboradores *
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
                	CASE
                		WHEN p.fecha_inicio IS NULL THEN (
                            SELECT
                        		CASE
                            		WHEN COUNT(*) = 0 THEN  1
                            		ELSE (COUNT(*) + 1)
                        		END
                			FROM proyectos AS pActivos WHERE pActivos.activo = 1
                        	)
                		ELSE (
							CASE
                            	WHEN p.num_proyectos_activos > 0 THEN p.num_proyectos_activos
                            	ELSE 1
                            END
                        )
                	END
			))
            AS costo_rrhh,
            ((infoAdm.costo_locativos * p.proyecto_duracion)/(
                CASE
                    WHEN p.fecha_inicio IS NULL THEN (
                        SELECT
                            CASE
                                WHEN COUNT(*) = 0 THEN  1
                                ELSE (COUNT(*) + 1)
                            END
                        FROM proyectos AS pActivos WHERE pActivos.activo = 1
                        )
                    ELSE (
                        CASE
                            WHEN p.num_proyectos_activos > 0 THEN p.num_proyectos_activos
                            ELSE 1
                        END
                    )
                END
            )) AS costo_loc,
            ((infoAdm.costo_maquinaria * p.proyecto_duracion)/(
                CASE
                    WHEN p.fecha_inicio IS NULL THEN (
                        SELECT
                            CASE
                                WHEN COUNT(*) = 0 THEN  1
                                ELSE (COUNT(*) + 1)
                            END
                        FROM proyectos AS pActivos WHERE pActivos.activo = 1
                        )
                    ELSE (
                        CASE
                            WHEN p.num_proyectos_activos > 0 THEN p.num_proyectos_activos
                            ELSE 1
                        END
                    )
                END            
            ))  AS costo_maq
        FROM proyectos AS p
        JOIN proyecto_actividad AS pa ON p.id_proyecto = pa.id_proyecto
        JOIN proyecto_actividad_detalles AS pad ON pa.id_proyecto_actividad = pad.id_proyecto_actividad
        JOIN informacion_administrativa as infoAdm ON p.id_informacion_administrativa = infoAdm.id_informacion_administrativa
        JOIN departamentos as dept on pad.id_departamento = dept.id_departamento
        WHERE p.activo = 0
        GROUP BY p.id_proyecto;
    '''
    queryProyectosActivos = '''
		SELECT
            p.*, SUM(8 * pad.duracion * pad.num_colaboradores *
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
                CASE
                    WHEN p.num_proyectos_activos > 0 THEN (p.num_proyectos_activos + 1)
                    ELSE 1
                END)
            )
            AS costo_rrhh,
            (infoAdm.costo_locativos * p.proyecto_duracion /(
                CASE
                    WHEN p.num_proyectos_activos > 0 THEN (p.num_proyectos_activos + 1)
                    ELSE 1
                END
            )) AS costo_loc,
            (infoAdm.costo_maquinaria * p.proyecto_duracion /(
                CASE
                    WHEN p.num_proyectos_activos > 0 THEN (p.num_proyectos_activos + 1)
                    ELSE 1
                END            
            ))  AS costo_maq,
            (
                SELECT SUM(
                    c_rrhh.horas_sistemas * infoAdm.salario_sis_prog + c_rrhh.horas_biomedica * infoAdm.salario_biomedica
                    + c_rrhh.horas_robotica * infoAdm.salario_rob_elect + c_rrhh.horas_industrial * infoAdm.salario_ind_prot
                    + c_rrhh.horas_diseno * infoAdm.salario_dis_pub + c_rrhh.horas_admin * infoAdm.costo_administrativo
                )
                FROM costos_rrhh_proyectos AS c_rrhh
                JOIN informacion_administrativa AS infoAdm ON c_rrhh.id_informacion_administrativa = infoAdm.id_informacion_administrativa
                WHERE c_rrhh.id_proyecto = p.id_proyecto
            ) AS costo_rrhh_ejecutado,
            (
                SELECT SUM(
                    c_mat.materiales_prototipos + c_mat.maquila_terceros + c_mat.software_adicional
                    + c_mat.tecnologia_adicional + 20*(infoAdm.costo_locativos / c_mat.num_proyectos_activos)
                    + 20*(infoAdm.costo_maquinaria / c_mat.num_proyectos_activos)
                )
                FROM costos_mat_proyectos AS c_mat
                JOIN informacion_administrativa AS infoAdm ON infoAdm.id_informacion_administrativa = c_mat.id_informacion_administrativa
                WHERE c_mat.id_proyecto = p.id_proyecto
            ) AS costo_mat_ejecutado
        FROM proyectos AS p
        JOIN proyecto_actividad AS pa ON p.id_proyecto = pa.id_proyecto
        JOIN proyecto_actividad_detalles AS pad ON pa.id_proyecto_actividad = pad.id_proyecto_actividad
        JOIN informacion_administrativa AS infoAdm ON p.id_informacion_administrativa = infoAdm.id_informacion_administrativa
        JOIN departamentos as dept on pad.id_departamento = dept.id_departamento
        WHERE p.activo = 1
        GROUP BY p.id_proyecto;
    '''
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(queryProyectosInactivos)
    listaProyectosInactivos = cursor.fetchall()
    cursor.execute(queryProyectosActivos)
    listaProyectosActivos = cursor.fetchall()
    #return render_template('calculadora_proyectos/templates/listaProyectos.html', pInactivos=listaProyectosInactivos)
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
