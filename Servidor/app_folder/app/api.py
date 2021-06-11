"""
API: Guarda las vistas de la API de la aplicación.
"""

from datetime import datetime, timedelta

from celery.result import AsyncResult
from flask import request, jsonify

import tasks as tk
import view_functions as fc
from app import app, active, client, queue


##################################################################################################################################
#                                                   FUNCIONES DE LA API                                                          #
##################################################################################################################################

@app.route("/api/request")  
def api_request():

    """
    Endpoint de la API para la realización de las predicciones.
    Tiene que recibir el parámetro 'data' a través de request.args, el cuál será una cadena con los datos de la petición.

    
    """

    # Si el servidor está activo
    if active:

        # Si contiene el argumento 'data' 
        if 'data' in request.args:

            # Lo guardamos
            data = request.args['data']

            # Recogemos el timestamp de la petición
            timestamp = fc.get_time_stamp()

            # Comprobamos que el formato de los datos es válido
            result = fc.is_valid_format_v2(data=data,filename=None)

            # Si el resultado es válido
            if result != None:

                # Lo añadimos a la cola de peticiones
                job = tk.request_task.delay(result['resultado'])

                # Incrementamos el número de trabajos recibido
                fc.update_jobs()

                # Guardamos la tarea en la base de datos
                fc.save_task_on_db(job.id,None,timestamp,None,fc.cast_register_to_text(result['registro']),result['duplicados'])

                # Añadimos a la cola una tarea para que se elimine 24h después, así como
                # el archivo .csv que se genera para el usuario
                tk.delete_task_db.apply_async([job.id], eta=datetime.utcnow() + timedelta(days=1))

                # Esperamos a que la cola nos devuelva los resultados
                res = job.wait(timeout=None, interval=0.5)
                
                # Devolvemos los resultados de la petición
                return jsonify({'job_id':job.id,'res': res}), 200 

            else:

                # En caso de que el formato de los datos sea inválido
                return jsonify({'res': "Error: el formato de los datos es inválido"}), 400
        else:

            # En caso de que no se reciba el argumento data
            return jsonify({'res': "Error: No ha recibido ningún argumento data"}), 400
    else:

        # En caso de que el servidor no esté marcado como activo
        return jsonify({'res': "Error: el servidor no está disponible"}), 500


@app.route("/api/request_job_result/<job_id>")
def request_job_result(job_id):

    """ 
    Endpoint de la API para recoger los resultados de una petición anterior.


    :param job_id: Identificador de la petición a borrar (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """
    # Si está activo
    if active:

        # Se comprueba que el job_id no esté vacío
        if job_id != '':
            try:

                # Buscamos la petición en la base de datos
                myquery = { "id": job_id }
                answer = client.app_data.tasks.find_one(myquery)

                # Si hemos encontrado alguna
                if answer != None:

                    # Recogemos los resultados del backend
                    res = AsyncResult(job_id,app=queue)

                    # Devolvemos los resultados
                    return jsonify({'job_id':job_id,'res':res.get()}), 200 

                # En caso de que no exista  
                else:
                    return "Error: El trabajo que buscas no existe.", 404

            # En caso de que no exista, o se produzca un error.
            except Exception as e:
                print(e)
                return "Error: ha habido un error interno.", 500
        else:
            # En caso de que no se haya introducido un job_id
            "Error: no se ha introducido un job_id", 400
   
    else:

        # En caso de que el servidor no esté marcado como activo
        return "Error: el servidor no está disponible", 500

##################################################################################################################################
