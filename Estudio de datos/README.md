# TFG

  Creación de una herramienta para la predicción de la patogenidad de los SNP que se dan en la creación del ARN mensajero a partir del preARN mensajero.
  
  Resumen:
  
  Un polimorfismo puntual, también denominado de un solo nucleótido o SNP (Single Nucleotide Polymorphism, pronunciado snip), es una variación en la secuencia de ADN que afecta 
  a una sola base (adenina (A), timina (T), citosina (C) o guanina (G)) de una secuencia del genoma; estos cambios se traducen en una modificación de los aminoácidos que se secuencian de una proteína (cada aminoácido se secuencia mediante tres bases, aunque estas no son únicas; es decir, un aminoácido puede ser secuenciado por varias combinaciones de bases), y estas modificaciones pueden producir (o no) una codificación errónea de las proteínas que se forman, pudiendo dar lugar a posibles enfermedades.
  Estos cambios se producen durante el proceso del splicing de ARN o empalme de ARN, el cual es un proceso post-transcripcional de maduración del ARN del cual eliminan ciertos fragmentos secuenciales.

## Carpetas

  - files: ficheros usados en los diferentes notebooks para apoyo
    - columnas.txt: contiene las columnas iniciales que vamos a utilizar para comenzar el proyecto
    - aminoacids.txt: contiene información de aminoácidos para crear un diccionario
    
    
  - datasets: datasets utilizados y generados en los diferentes notebooks
    - bening.out: dataset original de datos benignos
    - pathogenic.out: dataset original de datos patógenos
    - clean_bening.csv: dataset de datos benignos limpiado
    - clean_patho.csv: dataset de datos patógenos limpiado
    - studied_benign.csv: dataset con pequeñas modificaciones extraído del notebook 'study datasets'
    - studied_patho.csv:  dataset con pequeñas modificaciones extraído del notebook 'study datasets'
    
  - papers: papers de referencia para el desarrollo
 
  
  - word: diferentes ficheros word que iré utilizando a lo largo del proyecto
  
  - imgs: imágenes y gráficas extraídas a lo largo del proyecto
    - for_notebooks: imágenes que añadiré a los diferentes notebooks
    - histograms: histogramas extraídos a lo largo del proyecto
      - benign: del dataset 'clean_benign.csv'
      - pathogenic: del dataset 'clean_patho.csv'

  - pickles: contiene elementos de Python creados para su uso directo
  
## Notebooks
  
  - clean Datasets (Final).ipynb: notebook de limpieza de datos de los datasets
  - Study Datasets.ipynb: notebook para estudiar los datos de los datasets
  - First Models.ipynb: notebook para la realización de modelos de prueba
  - test.ipynb: notebook para la prueba de funciones

## Otros archivos (o librerías)

  - list_functions.py: funciones de listas
  - ds_functions.py funciones para datasets
