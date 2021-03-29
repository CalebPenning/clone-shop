import datetime

SECRET_KEY = '3UsZBW6qU3'
DATABASE_URI = "postgresql:///clone_shop"
SEARCH_API_KEY = "AIzaSyC77NKlE2t1A8CvUIhjTfnlykApxLiR00I"

def calculate_age(date):
    now = datetime.datetime.now()
    calculated = now.year - date.year - ((now.month, now.day) < (date.month, date.day))
    
    if calculated >= 21:
        return True
    
    else:
        return False