from datetime import date

def get_date():
    d = str(date.today().year) + '-' + str(date.today().month) + '-' + str(date.today().day)
    return(d)
