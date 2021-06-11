def isFloat(a):
    """
    Return True if the string is float
    False in other case.
    """
    try:
        float(a)
        return True
    except ValueError:
        return False