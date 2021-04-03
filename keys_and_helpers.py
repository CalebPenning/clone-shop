import datetime
from flask import flash, session
from sqlalchemy.exc import IntegrityError
from models import User, Order, db

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
    
def check_birthday(date):
    now = datetime.datetime.now()
    curr_age = now.year - date.year - ((now.month, now.day) < (date.month, date.day))
    
    if curr_age >= 21:
        return True
    
    return False
    
def do_signup(form):
    new_user = User.register(form)
    db.session.add(new_user)
        
    try:
        db.session.commit()
    except IntegrityError:
        flash('There was an error signing you up. Check the inputs and try again.', 'warning')
            
    reg_user = User.query.get_or_404(new_user.id)
    cart = Order(user_id=new_user.id)
            
    try:
        db.session.add(cart)
        db.session.commit()
    except IntegrityError:
        flash('You might need to make a new account.', 'error')
    
    return new_user

def do_login(form):
    return User.authenticate(form)

def get_user_from_session(username):
    if 'user_id' in session:
        curr_user = User.query.filter_by(username=username).first_or_404()
        return curr_user
    
    else:
        return False
    
def compare_users(curr_user, target_user_id):
    session_user = User.query.filter_by(username=curr_user).first_or_404()
    if session_user:
        target_user = User.query.get_or_404(target_user_id)
        
        if target_user == session_user:
            return True
        
    return False