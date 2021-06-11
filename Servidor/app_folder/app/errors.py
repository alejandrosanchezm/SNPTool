"""
Errors: Guarda las vistas de las páginas de error de la aplicación.
"""

from flask import render_template

from app import app


##################################################################################################################################
#                                                     MANEJO DE ERRORES                                                          #
##################################################################################################################################


@app.errorhandler(500)
def down_server(error):

    #Muestra la vista para el manejo de errores 500
    return render_template("error_pages/down_server.html"), 500



@app.errorhandler(404)
def not_found(error):

    """
    Muestra la vista para el manejo de errores 404
    """
    return render_template("error_pages/not_found.html"), 404

##################################################################################################################################
