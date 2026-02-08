CURRENT_MADHAB = "شافعي"

def select_madhab(name):
    global CURRENT_MADHAB
    CURRENT_MADHAB = name

def get_madhab():
    return CURRENT_MADHAB
