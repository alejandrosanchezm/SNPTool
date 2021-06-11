def equationBetweenTwoPoints(x1, x2, y1, y2, x):
    """
    Return the y value for an x value in the equation between two points
    """
    if (x2 - x1 != 0):
        return (((x - x1)/(x2-x1))*(y2-y1)) + y1

def reverseScale(x, xMin, xMax):
    """
    Return the y value for an x value in the equation between two points if we twist the values
    """
    return equationBetweenTwoPoints(xMin, xMax, xMax, xMin, x)

def normalizeValues(x, xMin, xMax):
    """
    Normalize a value to the range 0, 1 from another value range
    """
    return equationBetweenTwoPoints(xMin, xMax, 0, 1, x)

def denormalizeValues(x, xMin, xMax):
    """
    Return a normalize value converted to another scale
    """
    return equationBetweenTwoPoints( 0, 1, xMin, xMax, x)

def mediaValues(x):
    """
    return the media of a list 
    """
    return sum(x)/len(x)
    
def getMediaOfMultipleColumns(df,cols,new_col_name='media'):
    """
    Creates a column in the dataframe with the media of multiple columns.
    """
    df_copy = df.copy()
    df_copy[new_col_name] = df_copy[cols].T.apply(lambda x: mediaValues(x.tolist()))
    return df_copy

import networkx 
from networkx.algorithms.components.connected import connected_components
import numpy as np

def to_graph(l):
    G = networkx.Graph()
    for part in l:
        # each sublist is a bunch of nodes
        G.add_nodes_from(part)
        # it also imlies a number of edges:
        G.add_edges_from(to_edges(part))
    return G

def to_edges(l):
    """ 
        treat `l` as a Graph and returns it's edges 
        to_edges(['a','b','c','d']) -> [(a,b), (b,c),(c,d)]
    """
    it = iter(l)
    last = next(it)

    for current in it:
        yield last, current
        last = current    


def getDuplicatedCols(df):
    """
    Return group of columns with identical values
    """
    from tqdm.notebook import tqdm

    total = []

    for col in tqdm(df.columns):
        for col2 in df.columns:
            if df[col].dtypes == df[col2].dtypes:
                if np.where(df[col] == df[col2], True, False).all() and col != col2 and [col,col2] not in total and [col2,col] not in total:
                    total.append([col,col2])
    G = to_graph(total)
    return list(connected_components(G))