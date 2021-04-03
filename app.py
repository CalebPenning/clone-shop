import os
from flask import Flask, redirect, request, render_template, session, url_for, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from keys_and_helpers import DATABASE_URI, SECRET_KEY, calculate_age, do_signup, do_login, get_user_from_session, compare_users

from models import db, connect_db, Order, OrderItem, Item, ItemEffect, Effect, ItemFlavor, Flavor, User
from forms import SignUpForm, TestForm, LoginForm, DateField, DateTimeField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get(
    'DATABASE_URL',
    DATABASE_URI
))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = (os.environ.get(
    'SECRET_KEY', 
    'secret'
))

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def go_home():
    return redirect('/home')

@app.route('/home', methods=["GET", "POST"])
def homepage():
    items = Item.query.limit(20).all()
    
    if 'user_id' in session:
        user = get_user_from_session(session['user_id'])
        return render_template('user_home.html', items=items, user=user)
    else:
        return render_template('anon_home.html', items=items)

@app.route('/users/signup', methods=["GET", "POST"])
def user_signup():
    form = SignUpForm()
    
    if 'user_id' in session:
        flash("You are already signed up. You've been redirected.", 'warning')
        return redirect('/')
    
    if form.validate_on_submit():
        new_user = do_signup(form)
        session['user_id'] = new_user.username
        flash("Account created successfully. Welcome!", 'success')
        return redirect('/home')

    return render_template('users/signup.html', form=form)

@app.route('/users/login', methods=["GET", "POST"])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        user = do_login(form)
        if user:
            session['user_id'] = user.username
            flash(f"Welcome back, {user.username}!", 'success')
            return redirect('/home')
        
        else:
            form.username.errors.append('Incorrect username.')
            return redirect('/users/login')
        
    return render_template('users/login.html', form=form)

@app.route('/users/logout')
def log_user_out():
    if 'user_id' in session:
        session.pop('user_id')
        flash('Successfully logged out.', 'success')
        return redirect('/home')
    
    else:
        flash('You cannot logout because you are not logged in.', 'danger')
        return redirect('/home')
    
@app.route('/users/<int:id>/profile')
def show_user_profile(id):
    if 'user_id' not in session:
        flash("You do not have permission to view that page.", 'danger')
        return redirect('/')
    else:
        curr_user = get_user_from_session(session['user_id'])
        req_user = User.query.get_or_404(id)
        
        
@app.route('/shop')
def shop_homepage():
    curr_user = get_user_from_session(session['user_id'])
    if curr_user:
        return render_template('shop/home.html', user=curr_user)
    
@app.route('/items/<int:id>/details')
def get_item_details(id: int):
    req_item = Item.query.get_or_404(id)
    curr_user = User.query.filter_by(username=session['user_id']).first_or_404()
    return render_template('items/details.html', item=req_item, user=curr_user)

