"""
Views: se guardan las funciones que se encargan de todas las llamadas a URLs de la aplicación.
"""

import json
import os
import traceback
import uuid
from datetime import datetime, timedelta

from celery.result import AsyncResult
from flask import render_template, request, redirect, make_response, session, url_for, flash

import tasks as tk
import view_functions as fc
from app import app, client, queue, active
from data_structs import states
from messages import msg


##################################################################################################################################
#                                          VISTAS DE LA BARRA DE NAVEGACIÓN                                                      #
##################################################################################################################################

@app.route("/", methods=["GET", "POST"])
def index():

    """
    Vista inicial de la aplicación. Muestra la página inicial, y se encarga de recoger las peticiones de los usuarios.
    """
    # En caso de que no se haya establecido un UID de sesión, le asignamos uno
    # Esto servirá para cuando se guarden las tareas en la base de datos, poder identificar
    # quien las ha realizado, y así mostrárselas en la pantalla inicial
    if active:
        
        if 'uid' not in request.cookies:
            uid = str(uuid.uuid4())
            session['uid'] = uid

            # Incrementamos las visitas de la página
            fc.update_visits()

        else:
            session['uid'] = request.cookies['uid']
            
        # Acciones del método POST
        if request.method == "POST":

            try:

                # Recogemos los valores de entrada
                title = request.values['inputJobTitle']
                ext = None
                data = None
                filename = None
                path = None
                timestamp = fc.get_time_stamp()

                # Si se ha subido un fichero
                if 'file' in request.files:

                    file = request.files['file']

                    # Si el nombre del fichero está vacío, intentamos recoger los valores del cuadro de texto
                    if file.filename == '':

                        data = request.values['data_input1']
                        
                        # Si el cuadro de texto está vacío
                        if data == '':

                            # Mostramos un mensaje de que no se han introducido datos
                            flash(msg['EMPTY_REQUEST'], "warning")
                            
                            # Preparamos los argumentos para la página de inicio
                            args=fc.prepare_index_args(session['uid'])

                            # Preparamos la respuesta
                            res = make_response(render_template("public/index.html",args=args), 400)
                            if 'uid' not in request.cookies:
                                res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
                            return res
                            
                    # Si no, comprobamos si el tipo de fichero y su tamaño son correctos
                    else:
                        
                        ext = fc.allowed_file(request.files['file'].filename)
                        if ext != False:

                            if fc.allowed_filesize(request.cookies["filesize"]):
                                
                                # En caso de que lo sean, lo guardamos con un fichero temporal
                                filename = str(uuid.uuid4()) + "." + ext
                                path = os.path.join(app.config['TMP_FILES'], filename)
                                file.save(path)

                            # Si el tamaño del fichero es muy grande
                            else:

                                # Imprimimos un mensaje de que el fichero es demasiado grande
                                flash(msg['FILE_TOO_BIG'],"warning")

                                # Preparamos los argumentos para la página de inicio
                                args=fc.prepare_index_args(session['uid'])

                                # Preparamos la respuesta
                                res = make_response( render_template("public/index.html",args=args), 413 )
                                if 'uid' not in request.cookies:
                                    res.set_cookie("uid", uid, secure=False,expires=fc.return_one_day_expire())
                                return res

                        # Si el tipo de fichero no es el permitido
                        else:
                            flash(msg['NOT_ALLOWED_FILE'], "warning")
                            args=fc.prepare_index_args(session['uid'])

                            res = make_response( render_template("public/index.html",args=args), 400 )
                            if 'uid' not in request.cookies:
                                res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
                            return res

                # Si es texto
                else:

                    data = request.values['data_input1']

                    # Si los datos están vacíos
                    if data == '':

                        # Mostramos un mensaje de que no se han introducido datos
                        flash(msg['EMPTY_REQUEST'], "warning")
                        
                        # Preparamos los argumentos para la página de inicio
                        args=fc.prepare_index_args(session['uid'])

                        # Preparamos la respuesta
                        res = make_response(render_template("public/index.html",args=args), 400)
                        if 'uid' not in request.cookies:
                            res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
                        return res

            # En caso de que ocurra un error
            except Exception:

                # Imprimimos un mensaje de que ha ocurrido un error
                traceback.print_exc() 
                flash(msg['INTERNAL_ERROR'], "warning")

                # Preparamos los argumentos para la página de inicio
                args=fc.prepare_index_args(session['uid'])

                # Preparamos la respuesta
                res = make_response( render_template("public/index.html",args=args), 500)
                if 'uid' not in request.cookies:
                    res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
                return res

            # Comprobamos si los datos introducidos contienen un formato válido
            # En caso de que si, devolverá los datos formateados
            # En caso contrario, devolverá un None
            answer = fc.is_valid_format_v2(data,path)
            if answer != None:
                data = answer['resultado']
                try:
                    # Encolamos el trabajo en la cola de celery
                    job = tk.request_task.delay(data)

                    # Incrementamos el contador de trabajos realizados
                    fc.update_jobs()

                    # Guardamos la tarea en la base de datos
                    fc.save_task_on_db(job.id,title,timestamp,session['uid'],fc.cast_register_to_text(answer['registro']),answer['duplicados'])

                    # Añadimos a la cola una tarea para que se elimine 24h después, así como
                    # el archivo .csv que se genera para el usuario
                    tk.delete_task_db.apply_async([job.id], eta=datetime.utcnow() + timedelta(days=1))

                    # Preparamos la respuesta
                    res = make_response(redirect(url_for("loading", job_id=job.id)) )
                    if 'uid' not in request.cookies:
                        res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
                    return res

                # En caso de que ocurra un error
                except Exception:

                    # Mostramos el mensaje de error
                    traceback.print_exc() 
                    flash(msg['INTERNAL_ERROR'], "warning")

                    # Preparamos los argumentos para la página de inicio
                    args=fc.prepare_index_args(session['uid'])

                    # Preparamos la respuesta
                    res = make_response( render_template("public/index.html",args=args), 500 )
                    if 'uid' not in request.cookies:
                        res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
                    return res

            # Significa que ha habido un error de formato.
            else:
                traceback.print_exc() 

                # Mostramos el mensaje de formato incorrecto
                flash(msg['FORMAT_ERROR'], "warning")

                # Preparamos los argumentos para la página de inicio
                args=fc.prepare_index_args(session['uid'])

                # Preparamos la respuesta
                res = make_response( render_template("public/index.html",args=args), 400 )
                if 'uid' not in request.cookies:
                    res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
                return res

        # Acciones del método GET
        if request.method == "GET":
            
            # Preparamos los argumentos para la página de inicio
            args=fc.prepare_index_args(session['uid'])

            # Preparamos la respuesta
            res = make_response( render_template("public/index.html",args=args), 200 )
            if 'uid' not in request.cookies:
                res.set_cookie("uid",uid, secure=False,expires=fc.return_one_day_expire())
            return res

    else:
        traceback.print_exc() 
        # En caso de que el servidor no esté disponible, renderizamos la página de servidor caído
        return render_template("public/down_server.html"), 500


@app.route("/about_models",methods=["GET"])
def about_models():

    """
    Endpoint para la vista de la página sobre los modelos.
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:
        return render_template("public/about.html"), 200

    # En caso contrario, mostramos la página de servidor caído
    else:
        return render_template("public/down_server.html"), 500


@app.route("/api/", methods=['GET'])
def api():

    """
    Endpoint para la vista de la página de la documentación de la API.
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        return render_template("public/api.html"), 200

    # En caso contrario, mostramos la página de servidor caído
    else:
        return render_template("public/down_server.html"), 500


@app.route("/load_example", methods=['GET'])
def load_example():

    """
    Endpoint para la vista de la página de resultados de ejemplo.
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        return render_template("public/result_example.html"), 200

    # En caso contrario, mostramos la página de servidor caído
    else:

        return render_template("public/down_server.html"), 500


@app.route("/search_job",methods=['GET'])
def search_job():

    """
    Endpoint para la búsqueda de una petición mediante su ID.
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        try:

            # Intentamos recoger el job_id y provamos a redirigirlo
            job_id = request.values['search_input']
            
            # Eliminamos tabuladores y espacios que puedan haberse infiltrado en la cadena
            job_id = job_id.replace(" ","").replace("\t","")
            myquery = { "id": job_id }
            answer = client.app_data.tasks.find_one(myquery)

            # Si lo ha encontrador, lo redirigimos a mostrar los resultsados
            if answer != None:
                return redirect(url_for("loading",job_id=job_id))

            # En caso contrario, mostramos un error
            else:
                flash(msg['JOB_NOT_FOUND_ERROR'], "warning")
                return redirect(url_for("index"))
        except:

            # En caso de que no exista en la base de datos
            traceback.print_exc() 
            flash(msg['JOB_NOT_FOUND_ERROR'], "warning")
            return redirect(request.url), 404

    # En caso contrario, mostramos la página de servidor caído
    else:
        return render_template("public/down_server.html"), 500


@app.route("/cookie_policy",methods=['GET'])  
def policies():

    """
    Vista de la página de la política de Cookies.
    Mostrará dicha página si el servidor está activo, en caso contrario,
    mostrará la página correspondiente.
    """

    # Si el servidor está activo, mostramos la página correspondiente
    if active:
        return render_template("public/cookie_policies.html"), 200

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500

    
@app.route("/user_terms",methods=['GET'])  
def user_terms():

    """
    Vista de la página de la política de Cookies.
    Mostrará dicha página si el servidor está activo, en caso contrario,
    mostrará la página correspondiente.
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:
        return render_template("public/terms.html"), 200

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500
 
 
##################################################################################################################################
#                                               ACCIONES DE LA PÁGINA DE INICIO                                                  #
##################################################################################################################################

@app.route("/delete/<job_id>",methods=['GET'])
def delete(job_id):
    
    """
    Borra algún trabajo de la base de datos.

    :param job_id: Identificador de la petición a borrar (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        # Buscamos si el trabajo está dentro de mis trabajos
        session['uid'] = request.cookies['uid']
        myquery = { "uid": session['uid'] , "id":job_id}
        my_jobs = list(client.app_data.tasks.find(myquery))

        # Solo se pueden borrar aquellos trabajos creados por el propio usuario
        if len(my_jobs) == 0:
            flash(msg['FORBIDDEN_DELETE'], "warning")
            return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

        # En caso de que sea del usuario, lo borramos
        else:  
            try:
                tk.delete_task_db(job_id)
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
            
            # Si se produce un error
            except:
                traceback.print_exc() 
                flash(msg['INTERNAL_ERROR'], "warning")
                return "error", json.dumps({'success':False}), 404, {'ContentType':'application/json'} 

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500


@app.route("/error_notification",methods=["POST"])
def error_notification():

    """
    Recoge los datos de la notificación de errores y los escribe en un fichero.
    """
    data = {}

    # EMAIL (OPCIONAL)
    if 'email_error' in request.values:
        data['email'] = request.values['email_error']

    # EMAIL (OPCIONAL)
    if 'job_id_error' in request.values:
        data['job_id'] = request.values['job_id_error']

    # Devolvemos la respuesta como un String porque, si faltan, es que esta petición se
    # ha realizado a través de otro medio fuera de la página web

    # PROBLEMA (OBLIGATORIO)
    if 'issue_error' in request.values:
        data['issue'] = request.values['issue_error']
    else:
        return "Error, faltan datos.", 400

    # DESCRIPCIÓN (OBLIGATORIO)
    if 'description_error' in request.values:
        data['description'] = request.values['description_error']
    else:
        return "Error, faltan datos.", 400

    # Escribimos el mensaje en logs/mensajes.log
    fc.write_on_notification_log(data)

    return redirect(url_for("index"))


##################################################################################################################################
#                                 VISTAS PARA LA PÁGINA DE CARGA Y DE VISUALIZACIÓN DE LOS DATOS                                 #
##################################################################################################################################

@app.route("/loading/<job_id>",methods=['GET'])
def loading(job_id):

    """
    Vista de la página de carga de una petición.
    Si se intenta buscar una pagina de carga de un id que no exista, se mostrará un error
    y se redirigirá al usuario a la página principal.

    :param job_id: Identificador de la petición (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        try:
            # Se busca el id en la base de datos
            myquery = { "id": job_id }
            client.app_data.tasks.find(myquery)[0]

            # Si existe, se espera
            job = AsyncResult(job_id, app=queue)

            # Si el estado de la petición es success, se redirige a los resultados; si no, a la página de carga
            if "SUCCESS" not in job.status:
                return render_template("public/loading_page.html",job_id=job_id)
            else:
                return redirect(url_for("results",job_id=job_id))

        except:

            # En caso de que la petición no exista
            traceback.print_exc() 
            flash(msg['JOB_NOT_FOUND_ERROR'], "warning")
            return redirect(url_for("index")), 404         

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500


@app.route('/progress/<job_id>',methods=['GET'])
def progress(job_id):

    """
    Sirve para obtener a través de Jquery en la página de carga el estado de la tarea
    dentro de la cola de peticiones.

    :param job_id: Identificador de la petición (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        try:

            # Si el job_id es distinto de una cadena vacía
            if job_id != "":

                # Se espera hasta que el resultado de la petición es SUCCESS
                job = AsyncResult(job_id, app=queue)
                if "SUCCESS" not in job.status:
                    job.wait(timeout=None, interval=0.5)

                # Se devuelve que ha terminado SUCCESS
                return json.dumps(dict(
                    state=job.state
                ))      
            return '{}'

        except:

            # En caso de que se produzca algún tipo de error
            flash(msg['INTERNAL_ERROR'], "warning")
            return redirect(url_for("index")), 500         

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500


@app.route("/status/<job_id>",methods=['GET'])
def status(job_id):
    
    """
    Sirve para obtener a través de Jquery en la página de carga el estado de la tarea
    dentro de la cola de peticiones.

    :param job_id: Identificador de la petición (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        try:
            # Si el job_id no es una cadena vacía
            if job_id != "":

                # Esperamos a por los resultados (Se presupone que se llama a esta función tras realizar una petición, y existe)
                job = AsyncResult(job_id, app=queue)

                # Se devuelve el estado
                return json.dumps(dict(
                    state=states[job.state][0],
                    color_class=states[job.state][1] # Se devuelve el color del panel del estado
                )) 
            return '{}'

        # En caso de que ocurra algún tipo de fallo
        except:
            return "Server disconnected", 500         

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500


@app.route("/results/<job_id>",methods=['GET'])
def results(job_id):

    """
    Vista de la página de resultados. 
    Devuelve la página de resultados de un job_id específico si existe.
    Si no existe o se produce otro error, redirigirá al usuario a la página inicial y mostrará un mensaje flash.
    En caso de que el servidor esté marcado como inactivo, se le redirigirá a la página de correspondiente.

    :param job_id: Identificador de la petición (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:

        try:
            # Busca el id del trabajo en la base de datos
            myquery = { "id": job_id }
            answer = client.app_data.tasks.find_one(myquery)

            # Si lo encuentra
            if answer != None:

                # Espera que la cola le devuelva los resultados
                res = AsyncResult(job_id,app=queue)

                # Los guardamos como csv
                fc.save_as_csv(res.get(),job_id)

                # Si la respuesta de los datos es un diccionario
                if type(answer) == dict:
                    args = fc.prepare_result_args(answer,res.get())

                # En caso contrario (será una lista)
                else:
                    args = fc.prepare_result_args(answer[0],res.get())

                # En caso de que haya habido filas duplicadas, lo indicamos
                if args['duplicados'] == True:
                    flash('Se han eliminado de los resultados algunas filas duplicadas.', "warning")

                # Renderizamos la página
                return render_template("public/results.html", args=args), 200

            else:

                # En caso de que no se haya encontrado en BBDD
                traceback.print_exc() 
                flash(msg['JOB_NOT_FOUND_ERROR'], "warning")
                return redirect(url_for("index")), 404    
        except:

            # En caso de que no se haya encontrado en BBDD
            traceback.print_exc() 
            flash(msg['JOB_NOT_FOUND_ERROR'], "warning")
            return redirect(request.url), 404    

    # En caso contrario, mostramos la página de servidor caído                   
    else:
        return render_template("public/down_server.html"), 500


##################################################################################################################################