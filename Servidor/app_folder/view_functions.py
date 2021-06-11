import csv
import os
import pickle
import traceback
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app import *
from data_structs import bases, aminoacids, chrs, color_code

##################################################################################################################################
#                                          FUNCIONES UTILIZADAS POR LAS VISTAS DE LA APP                                         #
##################################################################################################################################

"""
View Functions: incluye funciones que son usadas por las vistas
"""

def get_time_stamp():
    
    """
    Devuelve un string con la fecha y la hora de llamada de la función en formato "%d/%m/%Y %H:%M:%S".

    :return: String con el formato indicado.
    :rtype: String.
    """
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def update_visits():

    """
    Incrementa uno a la variable global y la variable de la base de datos del número de visitas.
    """
    myquery = client.app_data.app_data.find()[0]
    globals()["n_visitors"] += 1
    newvalues = { "$set": { "n_visitors": globals()["n_visitors"], "n_jobs": globals()["n_jobs"]} }
    client.app_data.app_data.update_one(myquery, newvalues)

def update_jobs():

    """
    Incrementa uno a la variable global y la variable de la base de datos del número de trabajos.
    """
    myquery = client.app_data.app_data.find()[0]
    globals()["n_jobs"] = globals()["n_jobs"] + 1
    newvalues = { "$set": { "n_visitors": globals()["n_visitors"], "n_jobs": globals()["n_jobs"]} }
    client.app_data.app_data.update_one(myquery, newvalues)

def allowed_filesize(filesize):
    
    """
    Indica si un fichero tiene un tamaño menor o igual al tamaño máximo permitido.
    Devuelve True si el tamaño está permitido, False en caso contrario.

    :param filesize: Tamaño del fichero.
    :type filesize: String.

    :return: True en caso de que esté permitido el tamaño, False en caso contrario.
    :rtype: Boolean.
    """
    if int(filesize) <= app.config["MAX_CONTENT_LENGTH"]:
        return True
    else:
        return False

def allowed_file(filename):

    """
    Indica si un fichero es de un formato permitido.
    Devuelve True si es de un formato permitido, False en caso contrario.

    :param filename: Nombre del fichero a comprobar (Ej. datos.csv).
    :type filename: String .

    :return: Extensión del archivo en caso de éxito, False en caso contrario.
    :rtype: String en caso de éxito, Boolean en caso contrario.
    """
    if not "." in filename:
        return False
    ext = filename.rsplit(".",1)[1]
    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return ext
    else:
        return False

def read_vcf_file(filename):

    """
    Función que se encarga de leer los ficheros de tipo vcf.

    :param filename: Nombre del fichero a leer.
    :type filename: String (Path del fichero).

    :return: Pandas DataFrame con los datos formateados, None en caso de error.
    :rtype: Pandas DataFrame en caso de éxito, None en caso de error.
    """
    try:
        eliminados = {}

        with open(filename, mode='r') as vcf:
            line = vcf.readline()
            while line[0:2] == '##':
                line = vcf.readline()
                if line[1] != '#':
                    text = vcf.read()
                    header = line.replace("\n","").split("\t")
            vcf.close()

        lines = [x.split("\t") for x in text.split("\n")][:-1]
        df = pd.DataFrame(lines,columns=header)[['#CHROM','POS','REF','ALT']]
        df = df.rename(columns={'#CHROM': 'hg19_chr', 'POS': 'hg19_pos(1-based)','REF': 'ref', 'ALT': 'alt'})
        df = df.replace(".",np.nan)
        df['hg19_chr'] = df['hg19_chr'].apply(lambda x: x.replace("chr",""))
        df.dropna(axis=0,how='any')
        for index, row in df.iterrows():
            if len(row['ref']) > 1 or len(row['alt']) > 1 :
                eliminados[index] = row.to_dict()
                df = df.drop(index)
        return df
    except:
        return None

def is_valid_format_v2(data=None,filename=None):

    """
    Indica si unos datos o un fichero tienen un formato correcto.
    En caso de ser correcto, devuelve un Pandas Dataframe con los datos formateados corrrectamente y preprocesados 
    (es decir, transformadas aquellas variables que lo requieran); devolverá False en caso contrario.

    :param data: Cadena que contiene los datos a procesar. Proviene del formulario de entrada, o de la API.
    :type data: String.

    :param filename: Nombre del fichero a revisar.
    :type filename: String (Path del fichero).

    :return: Devuelve un diccionario con los siguientes campos:
        -'resultado':diccionario con los datos formateados.
        -'registro':diccionario con las líneas erróneas y el error encontrado.
        -'duplicados':booleano que indica True si contiene líneas duplicadas, False en caso contrario.
    En caso de error, devolverá None.
    :rtype: Dictionary en caso de éxito, None en caso de error.
    """

    registro = {}
    
    # Si no pasamos ni el nombre de un fichero ni datos, devolvemos False
    if data == None and filename == None:

        return None

    else:

        columns = ['hg19_chr','hg19_pos(1-based)','ref','alt','aaref','aaalt']

        try:

            # Si hay un fichero, leemos los datos de éste
            if filename != None:

                # Si es un CSV o Texto, los leemos con read_csv
                if ".csv" in filename or ".txt" in filename:
                    df = pd.read_csv(filename, header=None, names=columns)

                # Si es un excel, lo leemos con read_excel
                elif ".xlsx" in filename:
                    df = pd.read_excel(filename,names=columns,engine='openpyxl')
                    
                # En caso contrario, se ha producido un error y devolvemos False
                elif ".vcf" in filename:
                    df = read_vcf_file(filename)
                else:
                    return None

                #os.remove(os.path.join(app.config['TMP_FILES'], filename))

            # En caso contrario, leemos los datos
            else:

                # Separamos los datos por líneas y por comas; eliminamos posibles líneas vacías
                # y los convertimos a dataframe
                data = [x.replace("\r","").replace(" ","").split(",") for x in data.split("\n")]
                [data.remove(line) for line in data if line == ['']] 

                # Esta línea sirve por si no se introduce ningún aminoácido, para no haya problemas de formato
                data.append('.'*6)
                df = pd.DataFrame(data,columns=['hg19_chr','hg19_pos(1-based)','ref','alt','aaref','aaalt'])    

            # Sustituimos los puntos por nulos
            df = df.replace(".",np.nan)

            # Eliminamos las filas que tengan todo nulo (la última al menos)
            df = df.dropna(axis=0,how="all")
            
            # Comprobamos si hay filas duplicadas
            has_duplicates = len([x for x in df.duplicated() if x == True]) >= 1

            # y las eliminamos
            df = df.drop_duplicates()

            # Comprobamos la validez de los datos
            for index, row in df.iterrows():

                # Para cada fila

                # Si las bases no están en el diccionario
                if row['ref'] not in bases.keys() or row['alt'] not in bases.keys():

                    # Añadimos el error al registro
                    registro[index] = list(row), "La/s bases son incorrectas."

                    # Eliminamos esta fila, y pasamos a comprobar la siguiente
                    df = df.drop(index)
                    continue

                # Comprobamos si hay aminoácidos en las columnas
                if 'aaref' in df.columns and 'aaalt' in df.columns:

                    # Si los aminoácidos de referencia no son válidos
                    if row['aaref'] not in aminoacids.keys() and str(row['aaref'])!='nan' and str(row['aaref'])!='':

                        # Añadimos el error al registro
                        registro[index] = list(row), "El/los aminoácidos son incorrectos."

                        # Eliminamos esta fila, y pasamos a comprobar la siguiente
                        df = df.drop(index)
                        continue

                    # Si los aminoácidos alternativos no son válidos
                    elif row['aaalt'] not in aminoacids.keys() and str(row['aaalt'])!='nan' and str(row['aaalt'])!='':
                        
                        # Añadimos el error al registro
                        registro[index] = list(row), "El/los aminoácidos son incorrectos."

                        # Eliminamos esta fila, y pasamos a comprobar la siguiente
                        df = df.drop(index)

                        continue

                # Si los cromosomas no están en la lista de cromosomas
                if str(row['hg19_chr']) not in chrs:

                    # Añadimos el error al registro
                    registro[index] = list(row), "El cromosoma es incorrecto."

                    # Eliminamos esta fila, y pasamos a comprobar la siguiente
                    df = df.drop(index)
                    continue

                # Si las posiciones no son válidas
                if search_if_in_range(row['hg19_pos(1-based)'],row['hg19_chr']) == False:

                    # Añadimos el error al registro
                    registro[index] = list(row), "La posición no es válida."

                    # Eliminamos esta fila, y pasamos a comprobar la siguiente
                    df = df.drop(index)
                    continue
            
            # Convertimos los cromosomas X al valor 23
            df['hg19_chr'] = df['hg19_chr'].replace(["X","x"],23)

            # Creamos las columnas de One Hot Encoding necesarias para los modelos
            df = create_OHE(df)

            # Transformamos las bases a formato numérico para que puedan ser interpretables
            df['ref'] = df['ref'].replace(bases)
            df['alt'] = df['alt'].replace(bases)
            df[['hg19_chr','hg19_pos(1-based)','ref','alt']] = df[['hg19_chr','hg19_pos(1-based)','ref','alt']].astype(int)

            # En caso de que todas las columnas tengan algún fallo
            if df.empty:
                return None

            else:
                # Devolvemos el dataframe
                return {'resultado':df.to_dict(orient='records'), 'registro':registro, 'duplicados':has_duplicates}

        except Exception:

            # En caso de error
            traceback.print_exc() 
            return None

def save_as_csv(data,job_id):

    """
    Guarda un fichero como .CSV en la carpeta static/client/.

    :param data: Resultados de la petición de predicción.
    :type data: Diccionario (Formato de respuesta de la función tasks.py/request_task).

    :param job_id: Identificador de la petición (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).
    """
    keys = data[0].keys()
    filename = os.path.join(app.config['CLIENT_FILES'],job_id +".csv")

    # En caso de que el fichero ya exista volvemos
    if os.path.isfile(filename):
        return

    # En caso contrario, guardamos el fichero
    with open(filename, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def search_if_in_range(position, chromosome):

    """
    Busca si una posición de un cromosoma está o no permitida por la aplicación.

    :param chromosome: Cromosoma.
    :type chromosome: String [1..22, X].

    :param position: Posición en el cromosoma.
    :type position: Integer (Positivo).

    :return: Devuelve True si está en el rango permitido, False en caso contrario.
    :rtype: Boolean (True o False).
    """
    with open(os.path.join(app.config['SERVER_FILES'], "list_of_positions_in_chr.pkl"), 'rb') as f:
        list_of_pos = pickle.load(f)
        f.close()
    if position != '' and chromosome != '':
        if chromosome == 'X':
            chro = 23
        else:
            chro = int(chromosome)
        pos = int(position)
        df = list_of_pos[chro-1]
        result = df[(df['pos1'] <= pos) & (df['pos2'] >= pos)]
        if result.empty:
            return False
        else:
            return True
        return False
    else:
        return False

def save_task_on_db(job_id,title,timestamp,uid,registro,duplicados):

    """
    Guarda una tarea en la base de datos.

    :param job_id: Identificador de la petición (Se obtiene al añadir la tarea a la cola.).
    :type job_id: String (UID de la petición).

    :param title: Título de la petición.
    :type title: String .

    :param timestamp: TimeStamp de la fecha y hora de la creación de la tarea.
    :type timestamp: String.

    :param uid: UID de la cookie del usuario.
    :type uid: String (UID).

    :param registro: Registro de todas las líneas con algún error de codificación.
    :type registro: String.

    :param duplicados: Indica si la petición contenía o no líneas duplicadas.
    :type duplicados: Booleano (True, False).
    """
    m = {'id':job_id,'title': title, 'timestamp':timestamp,'uid':uid,'registro':registro,'duplicados':duplicados}
    client.app_data.tasks.insert_one(m)              

def prepare_result_args(answer, copy_data):

    """
    Prepara los argumentos para la página de resultados

    :param answer: Datos desde la base de datos
    :type answer: Dictionary

    :param copy_data: Datos de los resultados de la predicción (desde la cola)
    :type copy_data: Dictionary

    :return: Diccionario con los datos necesarios para mostrar la página de resultados
    :rtype: Dictionary
    """

    # Formateamos los transcript_consequences a un formato de tabla (matriz)
    data = copy_data
    for i in range(0,len(data)):
        data[i]['transcript_consequences'] = return_dict_as_table(copy_data[i]['transcript_consequences'])

    args = {}

    # My_data contiene los datos de los resultados
    args['my_data'] = data

    # Job_id es el id de la petición
    args['job_id'] = answer['id']

    # Indica si se tienen que mostrar las gráficas (Solo si hay más de una línea de resultados)
    if len(data) > 1:
        args['show'] = True
    else:
        args['show'] = False
        
    # Título
    if answer['title'] == '':
        args['title'] = None
    else:
        args['title'] = answer['title']

    # Registro es el registro de errores
    if answer['registro'] != None:
        args['registro'] = answer['registro'].split("\n")[0:-1]
        
    # Duplicados indica si hay o no valores duplicados
    args['duplicados'] = answer['duplicados']

    # Timestamp de creación de la tarea
    args['timestamp'] = answer['timestamp']

    # Graph_1 contiene los valores para la gráfica 1 (Benignos / Patógenos)
    predictions = [x['prediction'] for x in copy_data]
    args['graph_1'] = str(predictions.count('Benigno')) + "," + str(predictions.count('Patógeno'))

    # Unique contiene los valores a mostrar en la segunda gráfica
    # Count contiene el número de ocurrencias para cada uno de dichos valores
    # Colours indica el color con el que se tiene que mostrar cada sección
    terms = [x['most_severe_consequence'] for x in copy_data]
    if len(terms) > 0:
        #terms = ["Sin datos" if x==None else x for x in terms]
        unique = list(set(terms))
        count = [str(terms.count(x)) for x in unique]
        colours = [color_code[x] for x in unique]

        args['unique'] = ','.join(unique)
        args['count'] = ','.join(count)
        args['colours'] = ','.join(colours)
    else:
        args['unique'] = None
        args['count'] = None
        args['colours']= None
    
    return args

def prepare_index_args(uid):

    """
    Prepara los argumentos para la página de inicio.

    :param uid: UID de la cookie de sesión del usuario.
    :type uid: String (UID).

    :return: Diccionario con los datos necesarios para mostrar la página de inicio.
    :rtype: Dictionary.
    """

    # Recuperamos los trabajos realizados por el usuario
    args = {}
    myquery = { "uid": uid }
    my_jobs = list(client.app_data.tasks.find(myquery))

    # Recogemos el número de visitantes
    args['n_visitors']=globals()["n_visitors"]

    # Recogemos el número de trabajos realizados
    args['n_jobs']=globals()["n_jobs"]        

    # Recogemos el email del administrador
    args['email']=app.config["ADMIN_EMAIL"]

    # Si no hay trabajos, indicamos my_jobs a cero
    if len(my_jobs) == 0:
        my_jobs = None

    # En caso contrario, invertimos la lista para que se muestren en orden cronológico (Más antiguos abajo)
    else:
        my_jobs.reverse()
    args['my_jobs']=my_jobs
    return args

def return_one_day_expire():

    """
    Devuelve la fecha del día siguiente al que se ejecuta.

    :return: DateTime que marca el día siguiente.
    :rtype: Datetime.
    """
    return datetime.now() + timedelta(days=1)

def cast_register_to_text(register):

    """
    Sirve para convertir el diccionario de errores en una cadena de texto.

    :param register: Diccionario con los errores de una petición.
    :type register: Dictionary.

    :return: String del diccionario; None en caso de error.
    :rtype: String en caso de éxito; None en caso contrario.
    """
    if register:
        text = ""
        for elem in register.keys():
            text += f"Línea {elem}: {register[elem][0]} {register[elem][1]} \n"
        return text
    else:
        return None

def create_OHE(df):

    """
    Codifica los Cromosomas y los Alelos en OHE.

    :param df: Pandas DataFrame con los datos de la petición.
    :type df: Pandas DataFrame.

    :return: Pandas DataFrame con los datos transformados.
    :rtype: Pandas DataFrame.
    """
    def isValue(x,i):
        if x == str(i):
            return 1
        else:
            return 0

    # Casteamos los cromosomas
    for i in range(0,24):
        df['hg19_chr_' + str(i)] = df['hg19_chr'].apply(lambda x: isValue(x,i))
        
    # Casteamos las bases
    for i in bases.keys():
        df['ref_' + str(i)] = df['ref'].apply(lambda x: isValue(x,i))
        df['alt_' + str(i)] = df['alt'].apply(lambda x: isValue(x,i))

    return df

def return_dict_as_table(input_data):

    """
    Esta función se encarga de transformar los datos de la línea de Transcript records a un formato de tabla
    de tal forma que pueda ser mostrado en la página de resultados de una manera más legible.

    :param input_data: Lista con los datos de transcript_consequeces de una predicción.
    :type input_data: List.

    :return: Diccionario con los resultados en forma de tabla; en caso de error o no haber datos se devolverá 'Sin datos'.
    :rtype: Dictionary en caso de éxito, o String en caso contrario.

    """
    try:
        if input_data == 'Sin datos':
            return 'Sin datos'
        if type(input_data) == dict and 'columns' in input_data:
            return input_data
        
        column_names = []
        data = []
        results = {}
        for row in input_data:
            column_names += row.keys()
            data.append(row)
        cols = list(set(column_names))
        transcript_consequences = pd.DataFrame(data=data, columns = cols)
        for col in transcript_consequences.columns:
            transcript_consequences[col] =transcript_consequences[col].fillna("Sin datos").astype(str).str.replace('_',' ')
        new_result = transcript_consequences.to_dict('index')
        results['columns'] = cols
        for key in new_result.keys():
            results[str(key)] = list(new_result[key].values())
        return results
    except:
        traceback.print_exc()
        return 'Sin datos'
    
def write_on_notification_log(data):

    """
    Escribe los mensajes de notificación de errores en el fichero de log.

    :param data: Diccionario con los campos de la notificación del error.
    :type data: Dictionary.
    """
    file = open(app.config['LOG_FILES'] + "mensajes.log", "w")
    file.write("[" + get_time_stamp() + "] El mensaje de error es el siguiente: \n")
    for key in data.keys():
        file.write(" -" + key + ": " + data[key] + "\n")
    file.close()

##################################################################################################################################
