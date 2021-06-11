def notCommonBothLists(lst1, lst2):
    """Return elements not in common in both lists"""
    if lst1 == None or type(lst1) != list:
        raise ValueError("lst1 must be a list.")    
    if lst2 == None or type(lst2) != list:
        raise ValueError("lst2 must be a list.")
    return list(set(lst1) ^ set(lst2))

def inCommon(lst1, lst2):
    """Return elements in common between both lists"""
    if lst1 == None or type(lst1) != list:
        raise ValueError("lst1 must be a list.")    
    if lst2 == None or type(lst2) != list:
        raise ValueError("lst2 must be a list.")
    return list(set(lst1) & set(lst2))

def notCommonFirstList(lst1, lst2):
    """Return elements not in common in first lists"""
    if lst1 == None or type(lst) != list:
        raise ValueError("lst1 must be a list.")    
    if lst2 == None or type(lst) != list:
        raise ValueError("lst2 must be a list.")
    return list(set(lst1).difference(lst2))

def notCommonSecondList(lst1, lst2):
    """Return elements not in common in second lists"""
    if lst1 == None or type(lst1) != list:
        raise ValueError("lst1 must be a list.")    
    if lst2 == None or type(lst2) != list:
        raise ValueError("lst2 must be a list.")
    return list(set(lst2).difference(lst1))

def convertListOfListsToFlat(lst):
    """Convert Multidimensional matrix into a 1-Dimension Python list"""
    if lst == None or type(lst) != list:
        raise ValueError("lst must be a list.")    
    if len(lst) == 0:
        return lst
    if isinstance(lst[0], list):
        return ConvertListOfListsToFlat(lst[0]) + ConvertListOfListsToFlat(lst[1:])
    return lst[:1] + ConvertListOfListsToFlat(lst[1:])

def getDuplicateElements(lst):
    """ Return the elements that are duplicated in list """
    if lst == None or type(lst) != list:
        raise ValueError("lst must be a list.") 
    return list(set([x for x in lst if lst.count(x) > 1]))

def getUniqueInList(lst):
    """ Return the unique values in list """
    if lst == None or type(lst) != list:
        raise ValueError("lst must be a list.") 
    return list(set(lst))

def countList(lst):
    """ Return a dict with the element and the number of ocurrences in list"""
    if lst == None or type(lst) != list:
        raise ValueError("lst must be a list.") 
    elements = GetUniqueInList(lst)
    dictionary = {}
    for e in elements:
        dictionary[e] = lst.count(e) 
    return dictionary

def countElementInList(lst,x):
    """ Return the number of ocurrences of an element in list"""
    return lst.count(x) 

def listToString(s,separator=';'):  
    
    str1 = " " 
    for i in range(0,len(s)): 
        if i != len(s)-1:
            str1 += str(s[i]) + separator 
        else:
            str1 += str(s[i])
    return str1[1:len(str1)]  

def commonMember(a, b): 
    """ Return True if two list have at least an element in common, False otherwise """
    a_set = set(a) 
    b_set = set(b) 
    if (a_set & b_set): 
        return True 
    else: 
        return False