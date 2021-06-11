from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from joblib import load
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import ds_functions as ds
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='SNP Tool',
    description='Una API sencilla para la predicción de la patogeinicidad de un SNP',
)

ns = api.namespace('SNP Tool', description='Modelo para la predicción de la patogeinicidad de un SNP.')

modelo = api.model('Argumentos', {
    'aaref':             fields.String(required=True, description='Aminoácido de referencia.'),
    'aaalt':             fields.String(required=True, description='Aminoácido alternativo'),
    'hg19_chr':          fields.String(required=True, description='Cromosoma del SNP del hg19'),
    'hg19_pos(1-based)': fields.Integer(required=True, description='Posición del SNP en notación pos(1-based) del hg19'),
    'ref':               fields.String(required=True, description='Base inicial del SNP'),
    'alt':               fields.String(required=True, description='Base alternativa del SNP'),
})

answer = api.model('Respuesta',{
    'aaref':                                fields.String(description='Aminoácido de referencia.'),
    'aaalt':                                fields.String(description='Aminoácido alternativo'),
    'hg19_chr':                             fields.String(description='Cromosoma del SNP del hg19'),
    'hg19_pos(1-based)':                    fields.String(description='Posición del SNP en notación pos(1-based) del hg19'),
    'ref':                                  fields.String(description='Base inicial del SNP'),
    'alt':                                  fields.String(description='Base alternativa del SNP'),
    'pd_of_MetaLR_score':                   fields.Float(description='Predicción de MetaLR_score'),
    'pd_of_M-CAP_score':                    fields.Float(description='Predicción de M-CAP_score'),
    'pd_of_REVEL_score':                    fields.Float(description='Predicción de REVEL_score'),
    'pd_of_DEOGEN2_score':                  fields.Float(description='Predicción de DEOGEN2_score'),
    'pd_of_ClinPred_score':                 fields.Float(description='Predicción de ClinPred_score'),
    'pd_of_integrated_fitCons_score':       fields.Float(description='Predicción de integrated_fitCons_score'),
    'pd_of_GM12878_fitCons_score':          fields.Float(description='Predicción de GM12878_fitCons_score'),
    'pd_of_PROVEAN_score_normalized':       fields.Float(description='Predicción de PROVEAN_score (normalizado a 0-1)'),
    'pd_of_FATHMM_score_normalized':        fields.Float(description='Predicción de FATHMM_score (normalizado a 0-1)'),
    'pd_of_LRT_Omega_normalized':           fields.Float(description='Predicción de LRT_Omega (normalizado a 0-1)'),
    'pd_of_MetaSVM_score_normalized':       fields.Float(description='Predicción de MetaSVM_score (normalizado a 0-1)'),
    'pd_of_MPC_score_normalized':           fields.Float(description='Predicción de MPC_score (normalizado a 0-1)'),
    'pd_of_bStatistic_normalized':          fields.Float(description='Predicción de bStatistic (normalizado a 0-1)'),
    'pd_of_BayesDel_addAF_score_normalized':fields.Float(description='Predicción de BayesDel_addAF_score (normalizado a 0-1)'),
    'pd_of_BayesDel_noAF_score_normalized': fields.Float(description='Predicción de BayesDel_noAF_score (normalizado a 0-1)'),
    'prediction':                           fields.String(description='Categorización (0 si benigno, 1 si patógeno)')
})

bases = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
aminoacids = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4, 'G': 5,
                'H': 6, 'I': 7, 'K': 8, 'L': 9, 'M': 10, 
                'N': 11, 'P': 12, 'Q': 13, 'R': 14, 'S': 15,
                'T': 16, 'V': 17, 'W': 18, 'X': 19, 'Y': 20}

# Creamos la clase con la que se cargarán los modelos
class model:

    def __init__(self,name,model,score,params,target): 
        self.name = name
        self.model = model
        self.score = score
        self.params = params
        self.target = target

def preprocess(x):
    x['ref'] = bases[x['ref']] 
    x['alt'] = bases[x['alt']] 
    x['aaref'] = aminoacids[x['aaref']] 
    x['aaalt'] = aminoacids[x['aaalt']] 
    if x['hg19_chr'] == 'X':
        x['hg19_chr'] = 23
    return x

def postprocess(x):
    x['aaref'] = list(aminoacids.keys())[list(aminoacids.values()).index(int(x['aaref_code']))]
    x['aaalt'] = list(aminoacids.keys())[list(aminoacids.values()).index(int(x['aaalt_code']))]
    x['ref'] = list(aminoacids.keys())[list(bases.values()).index(int(x['ref_code']))]
    x['alt'] = list(aminoacids.keys())[list(bases.values()).index(int(x['alt_code']))]
    x['pd_of_PROVEAN_score_normalized'] = ds.denormalizeValues(x['pd_of_PROVEAN_score_normalized'], -14, 14)
    x['pd_of_FATHMM_score_normalized'] = ds.denormalizeValues(x['pd_of_FATHMM_score_normalized'], -16.13, 10.64)
    x['pd_of_LRT_Omega_normalized'] = ds.denormalizeValues(x['pd_of_LRT_Omega_normalized'], 0, 7780.54)
    x['pd_of_MetaSVM_score_normalized'] = ds.denormalizeValues(x['pd_of_MetaSVM_score_normalized'], -2, 3)
    x['pd_of_bStatistic_normalized'] = ds.denormalizeValues(x['pd_of_bStatistic_normalized'], 0, 1000)
    x['pd_of_BayesDel_addAF_score_normalized'] = ds.denormalizeValues(x['pd_of_BayesDel_addAF_score_normalized'], -1.11707, 0.750927)
    x['pd_of_BayesDel_noAF_score_normalized'] = ds.denormalizeValues(x['pd_of_BayesDel_noAF_score_normalized'], -1.31914, 0.840878)
    return x

def predict(x):
   
    # Importamos los modelos que usará la función
    try:
        models_for_pred = load('models/models_for_pipeline1.joblib')
        clf_4 = load('models/model_4.joblib')
    
    except Exception as e:
        print(e)
        print("Error: Modelos no encontrados.")
        return
        
    cols = ['aaref_code', 'aaalt_code', 'hg19_chr', 'hg19_pos(1-based)', 'ref_code','alt_code']
    df = pd.DataFrame(np.array(x).reshape(-1,len(x)),columns=cols)
    result_df = df.copy()
    for model in models_for_pred:
        result_df['pd_of_'+model.name] = model.model.predict(df).reshape(-1,1)
    tmp_df = result_df.dropna()
    tmp_df['prediction'] = clf_4.model.predict(tmp_df)
    return tmp_df

@api.route('/predictor')
class predictor(Resource):
    @ns.marshal_with(answer)
    @ns.expect(modelo)
    def put(self):
        args = list(preprocess(api.payload).values())
        result = predict(args).to_dict()
        print(result)
        new_dic = {}
        for e in result:
            new_dic[e] = result[e].get(0)
        return postprocess(new_dic)

if __name__ == '__main__':
    app.run(debug=True)