
from celery import Celery

##################################################################################################################################
#                                          FUNCIONES DEL INICIO DE LA APLICACIÓN                                                 #
##################################################################################################################################

"""
Funciones utilizadas en __init__.py para la inicialización de la aplicación.
"""

def make_celery(app):

    """
    Sirve para la creación de la cola de peticiones de celery.

    :param app: Aplicación Flask.
    :type app: Flask Application.

    :return: cola de tareas Celery.
    :rtype: Celery Object.
    """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

##################################################################################################################################