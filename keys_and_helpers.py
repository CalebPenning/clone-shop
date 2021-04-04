import datetime
from flask import flash, session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from models import User, Order, db, bcrypt, OrderItem

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

def confirm_passwords(form):
    b = bcrypt
    
    true_pw = b.generate_password_hash(form.password.data)
    hashed_pw = true_pw.decode("UTF-8")
    confirm_pw = form.confirm_password.data
    
    if b.check_password_hash(hashed_pw, confirm_pw):
        return True
    
    return False

def get_user_cart(username):
    user = get_user_from_session(username)
    
    if user:
        user_cart = Order.query.filter_by(
            user_id=user.id
        ).filter_by(
            order_status='active'
        ).first_or_404()
        
        if user_cart:
            return user_cart
        
        elif user and not user_cart:
            new_cart = Order(user_id=user.id)
            db.session.add(new_cart)
            
            try:
                db.session.commit()
                return new_cart
            
            except IntegrityError:
                db.session.rollback()
                return False
        else:
            return False
        
def check_orders(item_id, order_id):
    items_in_cart = Order.query.filter(
        OrderItem.order_id == order_id
    ).filter(
        OrderItem.item_id == item_id
    ).first()
    
    if items_in_cart:
        return items_in_cart
    
    else:
        return False
    
def add_item(item_id, form, username):
    cart = get_user_cart(username)
    if cart:
        quantity = int(form.quantity.data)
        items_in_cart = check_orders(item_id, cart.id)
        
        if items_in_cart:
            items_in_cart.quantity += quantity
            db.session.commit()
            return True
        
        else:
            item_to_add = OrderItem(
                item_id=item_id,
                order_id=cart.id,
                quantity=quantity
            )
            db.session.add(item_to_add)
            db.session.commit()
            return True
    
    else:
        return False

def adjust_quantity(item_id, form, username):
    cart = get_user_cart(username)
    
    if cart:
        quantity = int(form.quantity.data)
        items_in_cart = check_orders(item_id, cart.id)
        
        if items_in_cart:
            items_in_cart.quantity = quantity
            db.session.commit()
            return True
        
        else:
            item_to_add = OrderItem(
                item_id=item_id,
                order_id=cart.id,
                quantity=quantity
            )
            db.session.add(item_to_add)
            db.session.commit()
            return True
    else:
        return False