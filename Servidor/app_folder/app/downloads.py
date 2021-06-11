"""
Downloads: Guarda las vistas para la descarga de ficheros de la aplicación.
"""

from flask import render_template, request, redirect, flash, send_from_directory

from app import app, active
from messages import msg


##################################################################################################################################
#                                                   DESCARGA DE FICHEROS                                                        #
##################################################################################################################################

@app.route("/download_csv_file/<job_id>", methods=['GET'])
def download_csv_file(job_id):

    """
    Devuelve el fichero csv con los resultados de un trabajo.
    En caso de que el fichero no se encuentra u ocurra algún otro error, se mostrará un error 404.
    En caso de que el servidor esté marcado como inactivo, se le redirigirá a la página correspondiente.

    :param job_id: Identificador de la petición (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """

    # Si el servidor está activo, mostramos la página correspondiente
    if active:  

        # Si el id no es un valor None o una cadena vacía, intentamos enviar el fichero
        if job_id != None and job_id != "":

            # Si es el fichero de ejemplo
            if job_id == 'ejemplo':
                try:
                    return send_from_directory(app.config["SERVER_FILES"], filename="resultados_ejemplo.csv", as_attachment=True)
                except FileNotFoundError:
                    flash(msg['NON_EXISTENT_FILE'], "error")
                    return redirect(request.url) 

            # En caso contrario
            else:

                # Se intenta descargar el fichero correspondiente al job_id
                filename = f"{job_id}.csv"
                try:
                    return send_from_directory(app.config["CLIENT_FILES"], filename=filename, as_attachment=True)

                # En caso de que no se haya encontrado el fichero
                except FileNotFoundError:

                    # En caso de que no exista el fichero
                    flash(msg['NON_EXISTENT_FILE'], "error")
                    return redirect(request.url)           
        else:

            # En caso de que no exista el fichero
            flash(msg['NON_EXISTENT_FILE'], "error")
            return redirect(request.url)

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html")


@app.route("/download_pos_file",methods=['GET'])  
def download_pos_file():

    """
    Devuelve el fichero de posiciones. En caso de error, muestra un mensaje flash por pantalla.
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:  

        # Se intenta enviar el fichero de posiciones
        try:
            return send_from_directory(app.config["SERVER_FILES"], filename="pos.gtf", as_attachment=True), 200
        except FileNotFoundError:

            # En caso de que no exista el fichero
            flash(msg['NON_EXISTENT_FILE'], "error")
            return redirect(request.url), 404

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500


@app.route("/download_model/<id>", methods=['GET'])
def download_model(id):

    """
    Devuelve el fichero de posiciones. En caso de error, muestra un mensaje flash por pantalla.

    :param id: Identificador del modelo a descargar.
    :type id: String [1..4].
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:  

        # Se intenta enviar el fichero correspondiente en función del id indicado por el botón de descarga.
        try:
            if id == "1":
                return send_from_directory(app.config["SERVER_FILES"], filename="bayesAdd.zip", as_attachment=True), 200
            elif id == "2":
                return send_from_directory(app.config["SERVER_FILES"], filename="bayesNo.zip", as_attachment=True), 200
            elif id == "3":
                return send_from_directory(app.config["SERVER_FILES"], filename="clinPred.zip", as_attachment=True), 200
            elif id == "4":
                return send_from_directory(app.config["SERVER_FILES"], filename="SNPTool.zip", as_attachment=True), 200
            else:

                # En caso de que se indique un id inválido
                flash(msg['NON_EXISTENT_FILE'], "error")
                return redirect(request.url), 404

        # En caso de que no exista el fichero
        except FileNotFoundError:
            flash(msg['NON_EXISTENT_FILE'], "error")
            return redirect(request.url), 404       

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500    


@app.route("/download_example_file/<filetype>",methods=['GET'])
def download_example_file(filetype):

    """
    Devuelve el fichero de posiciones. En caso de error, muestra un mensaje flash por pantalla.

    :param filetype: Identificador del archivo a descargar.
    :type filetype: String [txt, csv, xlsx, vcf].
    """
    # Si el servidor está activo, mostramos la página correspondiente
    if active:  

        try:
            # Se selecciona el tipo de fichero de ejemplo a descargar
            if filetype == 'txt':
                return send_from_directory(app.config["SERVER_FILES"], filename="ejemplo.txt", as_attachment=True), 200                    
            elif filetype == 'csv':
                return send_from_directory(app.config["SERVER_FILES"], filename="ejemplo.csv", as_attachment=True), 200
            elif filetype == 'xlsx':
                return send_from_directory(app.config["SERVER_FILES"], filename="ejemplo.xlsx", as_attachment=True), 200
            elif filetype == 'vcf':
                return send_from_directory(app.config["SERVER_FILES"], filename="ejemplo.vcf", as_attachment=True), 200
            else:

                # En caso de que se indique un tipo de fichero inválido
                flash(msg['NON_EXISTENT_FILE'], "error")
                return redirect(request.url), 200

        # En caso de que no se encuentre el fichero requerido
        except FileNotFoundError:
            flash(msg['NON_EXISTENT_FILE'], "error")
            return redirect(request.url), 200      

    # En caso contrario, mostramos la página de servidor caído           
    else:
        return render_template("public/down_server.html"), 500   

##################################################################################################################################
