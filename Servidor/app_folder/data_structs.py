##################################################################################################################################

"""
Estructuras de datos de la aplicación.

- **bases**: diccionario con la codificación de los alelos.
- **aminoacids**: diccionario con la codificación de los aminoácidos.
- **chrs**: lista con los cromosomas.
- **code_class**: diccionario con los códigos de color según sea benigno o patógeno (Utilizado en la tabla de la página de resultados).
- **prediction**: diccionario con la variable categórica para el resultado de prediction (0 Benigno, 1 Patógeno).
- **color_code**: diccionario código de color para los transcript_consequences.
- **states**: diccionario con la traducción del estado y el código de color para la etiqueta (Página de carga).
"""

# Diccionario de bases y sus códigos numéricos
bases = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

# Diccionario de aminoácidos y sus códigos numéricos
aminoacids = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4, 'G': 5,
                'H': 6, 'I': 7, 'K': 8, 'L': 9, 'M': 10, 
                'N': 11, 'P': 12, 'Q': 13, 'R': 14, 'S': 15,
                'T': 16, 'V': 17, 'W': 18, 'X': 19, 'Y': 20}

# Listado de cromosomas        
chrs = ["1","2","3","4","5","6","7","8","9","10","11","12",
        "13","14","15","16","17","18","19","20","21","22","X"]

# Diccionario de color de tabla respecto a si es Benigno o patógeno       
code_class = {
    '1':'table-danger', # Rojo
    '0':'table-success', # verde
    '1.0':'table-danger', # Rojo
    '0.0':'table-success' # verde
}

# Diccionario de términos respecto a si es un 0 (Benigno) o un 1 (Patógeno)   
prediction = {
    0:'Benigno',
    1:'Patógeno'
}

color_code = {
    'transcript ablation':'#ff0000',
    'splice acceptor variant':'#FF581A',
    'splice donor variant':'#FF581A',
    'stop gained':'#ff0000',
    'frameshift variant':'#9400D3',
    'stop lost':'#ff0000',
    'start lost':'#ffd700',
    'transcript amplification':'#ff69b4',
    'inframe insertion':'#ff69b4',
    'inframe deletion':'#ff69b4',
    'missense variant':'#ffd700',
    'protein altering variant':'#FF0080',
    'splice region variant':'#ff7f50',
    'incomplete terminal codon variant':'#ff00ff',
    'start retained variant':'#76ee00',
    'stop retained variant':'#76ee00',
    'synonymous variant':'#76ee00',
    'coding sequence variant':'#458b00',
    'mature miRNA variant':'#458b00',
    '5 prime UTR variant':'#7ac5cd',
    '3 prime UTR variant':'#7ac5cd',
    'non coding transcript exon variant':'#32cd32',
    'intron variant':'#02599c',
    'NMD transcript variant':'#ff4500',
    'non coding transcript variant':'#32cd32',
    'upstream gene variant':'#a2b5cd',
    'downstream gene variant':'#a2b5cd',
    'TFBS ablation':'#a52a2a',
    'TFBS amplification':'#a52a2a',
    'TF binding site variant':'#a52a2a',
    'regulatory region ablation':'#a52a2a',
    'regulatory region amplification':'#a52a2a',
    'feature elongation':'#7f7f7f',
    'regulatory region variant':'#a52a2a',
    'feature truncation':'#7f7f7f',
    'intergenic variant':'#636363',
    'Sin datos':'#eeeeee'
}

states = {
    'FAILURE': ["Fallido",'badge badge-danger'],
    'PENDING': ["Pendiente",'badge badge-info'],
    'RECEIVED':["Recibido",'badge badge-info'],
    'RETRY':   ["Reiniciado",'badge badge-warning'],
    'REVOKED': ["Rechazado",'badge badge-warning'],
    'STARTED': ["Comenzado",'badge badge-info'],
    'SUCCESS': ["Finalizado",'badge badge-success'],
}

##################################################################################################################################
