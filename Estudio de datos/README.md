# SNPTool

  Estudio de datos para la creación de una herramienta para la predicción de la patogenidad de los Polimofirmos de Nucleótido Único.
  
  Estos ficheros son el tratamiento que se ha realizado de un conjunto de datasets a través de Jupyter Notebooks para buscar un modelo de predicción.

## Carpetas

  - files: ficheros usados en los diferentes notebooks para apoyo
    - columnas.txt: contiene las columnas iniciales que vamos a utilizar para comenzar el proyecto
    - aminoacids.txt: contiene información de aminoácidos para crear un diccionario
    
    
  - datasets: datasets utilizados y generados en los diferentes notebooks
    - bening.out: dataset original de datos benignos
    - pathogenic.out: dataset original de datos patógenos
    - clean_bening.csv: dataset de datos benignos limpiado, extraido del notebook 'Extraccion y limpieza de los datos'
    - clean_patho.csv: dataset de datos patógenos limpiado, extraido del notebook 'Extraccion y limpieza de los datos'
    - studied_benign.csv: dataset con pequeñas modificaciones extraído del notebook 'Estudio de los datasets'
    - studied_patho.csv:  dataset con pequeñas modificaciones extraído del notebook 'Estudio de los datasets'
    - model_dataset.csv: dataset con los datos preparados para obtener los modelos, extraido del notebook 'Preparación de los datos para los modelos'
    
  - papers: papers de referencia para el desarrollo
  
  - imgs: imágenes y gráficas extraídas a lo largo del proyecto
    - for_notebooks: imágenes que añadiré a los diferentes notebooks
    - histograms: histogramas extraídos a lo largo del proyecto
      - benign: del dataset 'clean_benign.csv'
      - pathogenic: del dataset 'clean_patho.csv'

  - pickles: contiene elementos de Python creados para su uso directo
  
  - utils: contiene ficheros de Python con algunas utilidades:
    - list_functions.py: funciones de listas
    - ds_functions.py funciones para datasets
  
## Notebooks
  
  - Extracción y limpieza de datos.ipynb: notebook de limpieza de datos de los datasets
  - Estudio de los datasets.ipynb: notebook para estudiar los datos de los datasets
  - Preparación de los datos para los modelos.ipynb: notebook para la preparación de los datos para la extracción de los modelos
  - Pruebas de Modelos con One Hot Encoding.ipynb: contiene pruebas de modelos utilizando OHE
  - Pruebas de Modelos sin One Hot Encoding.ipynb: contiene pruebas de modelos utilizando Label Encoding
  - Modelos finales.ipynb: contiene el desarrollo de los modelos finales
