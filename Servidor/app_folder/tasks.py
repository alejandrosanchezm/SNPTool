"""
TASKS: Contiene las tareas que ejecutará la cola de tareas de la aplicación.
"""
##################################################################################################################################
import pandas as pd
import os
from flask import render_template, request, redirect, jsonify, make_response, send_from_directory, abort, session, url_for, flash, send_file, send_from_directory, safe_join, abort
from celery.signals import task_success

from app import app, queue, client, clinPred, bayesAdd, bayesNo, modeloFinal
from task_functions import *

##################################################################################################################################
#                                                     TAREAS DE LA COLA                                                          #
##################################################################################################################################

@queue.task
def request_task(x):

    """
    Request es la función que se encarga de procesar los datos de entrada y obtener las predicciones
    e información útil para la página web y la API.
    Recibe a través de x una lista con múltiples diccionarios (o un único diccionario), 
    obtiene la información de los modelos y devuelve un diccionario con los resultados.

    :param x: Pandas DataFrame con los datos para ser procesados por los modelos.
    :type x: Pandas DataFrame.

    :return: Devuelve un diccionario con los resultados de la petición en caso de éxito, None en caso contrario.
    :rtype: Dictionary en caso de éxito, None en caso contrario.
    """

    try:
        print("INICIADO")
        # Convertimos los datos en DataFrame para manejarlos mejor
        if type(x) == list:
            x = pd.DataFrame(x,columns=list(x[0].keys()))
        else:
            x = pd.DataFrame([x],columns=list(x.keys()))   

        # Realizamos la predicción de los tres scores necesarios

        cols = ['hg19_chr_1','hg19_chr_2','hg19_chr_3','hg19_chr_4','hg19_chr_5',
        'hg19_chr_6','hg19_chr_7','hg19_chr_8','hg19_chr_9','hg19_chr_10',
        'hg19_chr_11','hg19_chr_12','hg19_chr_13','hg19_chr_14','hg19_chr_15',
        'hg19_chr_16','hg19_chr_17','hg19_chr_18','hg19_chr_19','hg19_chr_20',
        'hg19_chr_21','hg19_chr_22','hg19_chr_23','hg19_pos(1-based)','ref_A',
        'ref_C','ref_G','ref_T','alt_A','alt_C','alt_G','alt_T']

        x['ClinPred_Score'] = clinPred.predict(x[cols])
        x['BayesDel_addAF_score'] = bayesAdd.predict(x[cols])
        x['BayesDel_noAF_score'] = bayesNo.predict(x[cols])

        # Realizamos la predicción final

        x['prediction'] = modeloFinal.predict(x[cols + ['ClinPred_Score','BayesDel_addAF_score','BayesDel_noAF_score']])

        # Posprocesamos los datos para retornarlos al formato original

        x = posprocess(x)

        # Intentamos extraer información extra a través de la API de Vest

        transcript_consequences = []
        most_severe_consequence = []

        for index, row in x.iterrows():        
            res = requestToVest(row)
            if res != None:
                transcript_consequences.append(res['transcript_consequences'])
                most_severe_consequence.append(res['most_severe_consequence'])
            else:
                transcript_consequences.append("Sin datos")
                most_severe_consequence.append("Sin datos")

        x['transcript_consequences'] = transcript_consequences
        x['most_severe_consequence'] = most_severe_consequence

        # Devolvemos los resultados en formato de diccionario
        print("FINALIZADO")

        return x.to_dict(orient='records')

    except Exception as e:
        
        return None

@queue.task
def delete_task_db(job_id): 

    """
    Borra una tarea de la base de datos, así como el fichero csv creado.

    :param job_id: Identificador de la petición a borrar (Se obtiene al añadir la tarea a la cola).
    :type job_id: String (UID de la petición).
    """

    client.app_data.tasks.delete_one({'id':job_id})
    try:
        os.remove(app.config["TMP_FILE"] + job_id + ".csv")
    except:
        pass

##################################################################################################################################