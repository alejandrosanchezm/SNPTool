"""
Task Functions: incluye funciones que son usadas por las tareas.
"""

import requests

from data_structs import bases, aminoacids, code_class, prediction


##################################################################################################################################
#                                          FUNCIONES UTILIZADAS POR LA COLA DE TAREAS                                            #
##################################################################################################################################

def posprocess(x):

    """
    Transforma los datos que han sido utilizados en los modelos para que puedan ser mostrados por pantalla.
    Devuelve los datos transformados.

    :param x: Pandas DataFrame con los datos para ser procesados
    :type x: Pandas DataFrame.

    :return: Devuelve el DataFrame procesado.
    :rtype: Pandas DataFrame.
    """
    invalid = ["nan","None",""] # Caracteres inválidos

    x['hg19_chr'] = x['hg19_chr'].replace(23,"X") # Remplazamos el número 23 por la X
    bases_inv = {v: k for k, v in bases.items()}  # Creamos un diccionario inverso para las bases
    x['ref'] = x['ref'].replace(bases_inv)        # Sustituimos el código de las bases por las bases de referencia
    x['alt'] = x['alt'].replace(bases_inv)        # Sustituimos el código de las bases por las bases alternativas
    if 'aaref' in x.keys() and 'aaalt' in x.keys():
        amino_inv = {v: k for k, v in aminoacids.items()}
        x['aaref'] = x['aaref'].replace(amino_inv)
        x['aaalt'] = x['aaalt'].replace(amino_inv)
    for e in invalid:
        if 'aaref' in x.keys() and 'aaalt' in x.keys():
            x['aaref'] = x['aaref'].replace(e,"Sin datos")
            x['aaalt'] = x['aaalt'].replace(e,"Sin datos")
        x.fillna("Sin datos")
    x['code'] = x['prediction'].apply(lambda y: code_class[str(y)])
    x['prediction'] = x['prediction'].apply(lambda y: prediction[y])
    x = x.rename(columns={"hg19_pos(1-based)":"hg19_pos"})
    x['ClinPred_Score'] = x['ClinPred_Score'].round(6)
    x['BayesDel_addAF_score'] = x['BayesDel_addAF_score'].round(6)
    x['BayesDel_noAF_score'] = x['BayesDel_noAF_score'].round(6)
    return x


def requestToVest(x):

    """
    Realiza una llamada a la API de VEST del siguiente enlace:
    https://rest.ensembl.org/documentation/info/vep_region_get
    y extrae la información 'transcript_consequences' y 'most_severe_consequence'
    para cada una de las filas de los resultados.
    Devuelve None en caso de que la llamada no devuelva un valor correcto.

    :param x: Pandas Series (fila) del dataframe con datos para hacer la petición a VEP.
    :type x: Pandas Series.

    :return: Devuelve un diccionario con los campos transcript_consequences y most_severe_consequence en caso de que consiga respuesta; en caso contrario, devuelve None.
    :rtype: Dictionary en caso de éxito, None en caso contrario.
    """
    try:

        # Buscamos el Cromosoma, posición y base alternativa
        server = "https://rest.ensembl.org"
        ext = "/vep/human/region/"+str(x.to_dict()['hg19_chr'])+":"+str(x.to_dict()['hg19_pos'])+"/"+str(x.to_dict()['alt'])+"/?"
        r = requests.get(server+ext, headers={ "Content-Type" : "application/json"} , timeout=20)
        
        # Si el resultado no ha salido bien devolvemos None
        if not r.ok:
            return None
        
        # En caso contrario, devolvemos un diccionario con los valores que necesitamos
        else:
            decoded = r.json()[0]
            
            return {
                'transcript_consequences':decoded['transcript_consequences'],
                'most_severe_consequence':decoded['most_severe_consequence'].replace("_"," ")
            }

    except:
        return None
    
##################################################################################################################################