import datetime
import os
import traceback
import warnings

import redis
from flask import Flask
from joblib import load
from pymongo import MongoClient

from init_functions import *

##################################################################################################################################

"""
Inicialización de la aplicación web.
"""

#Intentamos configurar el servidor. En caso de que no lo consiga, lo marcamos como inactivo
global n_visitors 
global n_jobs

try:
    # Creamos la aplicación Flask
    app = Flask(__name__)

    # Establecemos la cookie de sesión para un día
    app.permanent_session_lifetime = datetime.timedelta(days=1)

    # Conectamos con la base de datos de mongo
    client = MongoClient('127.0.0.1', 27017)
    #client = pymongo.MongoClient("mongodb+srv://admin:R2JmtdkyDUz_ce8@cluster0.y9m2d.mongodb.net/app_data?retryWrites=true&w=majority")

    # Recogemos de la base de datos los valores del número de visitantes
    # y el número de trabajos y los asignamos a unas variables globales
    myquery = client.app_data.app_data.find()[0]
    n_visitors = myquery['n_visitors']
    n_jobs = myquery['n_jobs']

    # Establecemos los parámetros de configuración de la aplicación flask
    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
    elif app.config["ENV"] == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    # Conectamos con la Base de Redis y con Celery
    redis_server = redis.Redis()
    queue = make_celery(app)

    # Importamos los modelos necesarios
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        modeloFinal = load(os.path.join(app.config['PICKLE_FILES'], 'ModeloFinal.joblib'))
        bayesAdd = load(os.path.join(app.config['PICKLE_FILES'], 'BayesDel_addAF.joblib'))
        bayesNo = load(os.path.join(app.config['PICKLE_FILES'], 'BayesDel_noAF.joblib'))
        clinPred = load(os.path.join(app.config['PICKLE_FILES'], 'ClinPred.joblib'))

    # Marcamos el servidor como activo
    active = True

except Exception as e:

    # En caso de que se produzca un error
    print(e)
    traceback.print_exc() 
    active = False

"""
Importamos las vistas
"""
from app import views
from app import api
from app import downloads
from app import errors

##################################################################################################################################