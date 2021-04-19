import os
import re
from flask import Flask, redirect, request, render_template, session, url_for, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.functions import random
from helpers import check_birthday, do_signup, get_user_from_session, compare_users, confirm_passwords, add_item, adjust_quantity, remove_items, get_user_cart, do_search
from keys import DATABASE_URI, SECRET_KEY

from models import db, connect_db, Order, OrderItem, Item, ItemEffect, Effect, ItemFlavor, Flavor, User
from forms import SignUpForm, LoginForm, DateField, DateTimeField, ItemQuantityForm, AgeVerificationForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get(
    'DATABASE_URL',
    DATABASE_URI
))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = (os.environ.get(
    'SECRET_KEY', 
    SECRET_KEY
))

debug = DebugToolbarExtension(app)

connect_db(app)


def test_search(param, keyword, limit=21):
    if param == 'Name':
        return (Item
                .query
                .filter(
                    Item.name.ilike(f"%{keyword}%")
                )
                .limit(limit)).all()
    
    elif param == 'Description':
        return (Item
                .query
                .filter(
                    Item.description.ilike(f"%{keyword}%")
                )).all()

@app.route('/')
def go_home():
    if 'of_age' not in session and 'user_id' not in session:
        return redirect('/verify-age')
    
    elif 'of_age' in session or 'user_id' in session:
        return redirect('/home')
    
@app.route('/verify-age', methods=["GET", "POST"])
def check_user_age():
    if 'of_age' and 'user_id' not in session:
        form = AgeVerificationForm()
        
        if form.validate_on_submit():
            verified = check_birthday(form.birthday.data)
            
            if verified == True:
                session['of_age'] = True
                flash('Age verified. Feel free to browse. Please sign up before placing an order.', 'success')
                return redirect('/home')
            
            else:
                return redirect('/sorry')
        
        else:
            return render_template('verify_age.html', form=form)
    
    elif 'of_age' or 'user_id' in session:
        flash('Age already verified.', 'danger')
        return redirect('/home')
    
    else:
        flash("Something went wrong. Whatever that was, don't do that!")
    
@app.route('/sorry')
def apologize():
    flash("We're sorry. You are not of age. If you input your age incorrectly, try again.")

@app.route('/home')
def homepage():
    items = Item.query.order_by(random()).limit(21).all()
    
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
        if confirm_passwords(form):
            new_user = do_signup(form)
            session['user_id'] = new_user.username
            flash("Account created successfully. Welcome!", 'success')
            return redirect('/home')

    return render_template('users/signup.html', form=form)

@app.route('/users/login', methods=["GET", "POST"])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form)
        if user:
            if session['of_age'] == True:
                session.pop('of_age')
                           
            session['user_id'] = user.username
            flash(f"Welcome back, {user.username}!", 'success')
            return redirect('/home')
        
        else:
            form.username.errors.append('Incorrect username.')
            return redirect('/users/login')
    else: 
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
def show_user_profile(id: int):
    if 'user_id' not in session:
        flash("You do not have permission to view that page.", 'danger')
        return redirect('/home')
    else:
        if compare_users(session['user_id'], id) == True:
            user = get_user_from_session(session['user_id'])
            return render_template('users/profile.html', user=user)
        
        else:
            flash("You do not have permission to view that page.", 'warning')
            return redirect('/users/login')

@app.route('/users/<int:id>/cart')
def show_user_cart(id):
    if 'user_id' not in session:
        flash("You do not have permission to view this page.", 'warning')
        return redirect('/users/login')
    else:
        if compare_users(session['user_id'], id) == True:
            user = get_user_from_session(session['user_id'])
            cart = get_user_cart(session['user_id'])
            form = ItemQuantityForm()
            total = sum([i.quantity * i.cart_items.price for i in cart.items])
            return render_template('users/cart.html', user=user, order=cart, form=form, total=total)
        else:
            flash("You cannot view or edit another user's orders. You have been redirected.", 'danger')
            return redirect('/home')

@app.route('/users/<int:id>/cart/checkout', methods=["GET", "POST"])
def confirm_order(id):
    if 'user_id' not in session:
        flash("You do not have permission to view this page.", 'warning')
        return redirect('/')
    
    else:
        if compare_users(session['user_id'], id) == True:
            user = get_user_from_session(session['user_id'])
            cart = get_user_cart(session['user_id'])
            total = sum([i.quantity * i.cart_items.price for i in cart.items])
            return render_template('confirm_order.html', user=user, cart=cart, total=total)    
        

@app.route('/shop/search')
def get_search_results():
    param = request.args.get('search-param').title()
    keyword = request.args.get('keyword')
    print(param, keyword)
    search_results = test_search(param, keyword)
    print(search_results)
    
    if len(search_results) > 1:
        try:        
            check_age = session['of_age']
            if check_age == True:
                return render_template('shop/search.html', results=search_results)
        except KeyError:
            try:
                curr_user = get_user_from_session(session['user_id'])
                return render_template('shop/search.html', results=search_results, user=curr_user)
            except KeyError:
                flash("Something went wrong on our end. Sorry about that.", 'danger')
                return redirect('/')
    
    elif len(search_results) < 1:
        flash('No results found for that keyword. Try shortening your keyword for more broad results.', 'warning')
        return redirect('/home')
    
    else:
        flash("There was an issue with your search. Check your search paramater and try again.", 'danger')
        return redirect('/home')
    
@app.route('/shop/items/<int:id>/details')
def get_item_details(id: int):
    form = ItemQuantityForm()
    req_item = Item.query.get_or_404(id)
    try:
        curr_user = User.query.filter_by(username=session['user_id']).first_or_404()
    except KeyError:
        try:
            check_age = session['of_age']
            return render_template('items/details.html', item=req_item, form=form)
        except KeyError:
            flash("Something went wrong on our end. You've been redirected.", 'danger')
            return redirect('/')
        
    return render_template('items/details.html', item=req_item, user=curr_user, form=form)


@app.route('/shop/items/<int:id>/add', methods=["POST"])
def add_item_to_cart(id: int):
    if 'user_id' in session:
        print("OK")
        add_to_cart = add_item(id, request, session['user_id'])
        if add_to_cart:
            flash("Item added successfully. Access your cart <a href='#'>here</a>", 'success')
            return redirect(f"/shop/items/{id}/details")
        else:
            flash("FAILURE", 'danger')
            return redirect(f"/shop/items/{id}/details")
    else:
        flash("You do not have permission to make an order. Login to do so.", 'danger')
        return redirect('/users/login')
    

@app.route('/shop/items/<int:id>/adjust', methods=["POST"])
def adjust_item_quantity(id):
    if 'user_id' in session:
        adjusted_items = adjust_quantity(id, request, session['user_id'])
        if adjusted_items:
            flash("Item quantity adjusted. Access your cart <a href='#'>here</a>", 'success')
            return redirect(f"/shop/items/{id}/details")
        else:
            flash("Failure")
            return redirect(f"/shop/items/{id}/details")
        
    else:
        flash("Please login to place an order.", 'warning')
        return redirect('/users/login')
    
@app.route('/shop/items/<int:id>/delete', methods=["POST"])
def remove_order_item(id):
    if 'user_id' in session:
        user = get_user_from_session(session['user_id'])
        items_to_delete = remove_items(id, session['user_id'])
        if items_to_delete:
            flash("Item(s) removed successfully.")
            return redirect(f"/users/{user.id}/cart")
        
        else:
            flash("Error deleting items.")
            return redirect("/home")
        
    else:
        flash("Please login to edit an order.", 'warning')
        return redirect('/users/login')


@app.route('/random-items')
def get_rando():
    items = Item.query.order_by(random()).limit(10).all()
    return render_template('random.html', items=items)

@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404
