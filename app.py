import os
from flask import Flask, redirect, request, render_template, session, url_for, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.functions import random
from helpers import check_birthday, do_signup, get_user_from_session, compare_users, confirm_passwords, add_item, adjust_quantity, remove_items, get_user_cart, do_search
from keys import DATABASE_URI, SECRET_KEY

from models import db, connect_db, Order, OrderItem, Item, ItemEffect, Effect, ItemFlavor, Flavor, User
from forms import SignUpForm, TestForm, LoginForm, DateField, DateTimeField, ItemQuantityForm

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
    return redirect('/home')

@app.route('/home', methods=["GET", "POST"])
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
            session['user_id'] = user.username
            flash(f"Welcome back, {user.username}!", 'success')
            return url_for(homepage())
        
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
            return redirect('/login')

@app.route('/users/<int:id>/cart')
def show_user_cart(id):
    if 'user_id' not in session:
        flash("You do not have permission to view this page.", 'warning')
        return redirect('/login')
    else:
        if compare_users(session['user_id'], id) == True:
            user = get_user_from_session(session['user_id'])
            cart = get_user_cart(session['user_id'])
            form = ItemQuantityForm()
            return render_template('users/cart.html', user=user, order=cart, form=form)
        else:
            flash("You cannot view or edit another user's orders. You have been redirected.", 'danger')
            return redirect('/home')

@app.route('/users/<int:id>/cart/checkout', methods=["GET", "POST"])
def confirm_order(id):
    pass

@app.route('/shop')
def shop_homepage():
    curr_user = get_user_from_session(session['user_id'])
    if curr_user:
        return render_template('shop/home.html', user=curr_user)

@app.route('/shop/search')
def get_search_results():
    param = request.args.get('search-param').title()
    keyword = request.args.get('keyword')
    print(param, keyword)
    search_results = test_search(param, keyword)
    print(search_results)
    if search_results and 'user_id' in session:        
        curr_user = get_user_from_session(session['user_id'])
        return render_template('shop/search.html', results=search_results, user=curr_user)
    
    else:
        return redirect(url_for(session[-1]))
    
@app.route('/shop/items/<int:id>/details')
def get_item_details(id: int):
    form = ItemQuantityForm()
    req_item = Item.query.get_or_404(id)
    curr_user = User.query.filter_by(username=session['user_id']).first_or_404()
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
        flash("You do not have permission to add")
        return redirect('/')
    

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
        return redirect('/login')
    
@app.route('/shop/items/<int:id>/delete', methods=["POST"])
def remove_order_item(id):
    if 'user_id' in session:
        items_to_delete = remove_items(id, session['user_id'])
        if items_to_delete:
            flash("Items removed. Access your cart <a href='#'>here</a>")
            return redirect("/home")
        
        else:
            flash("Error deleting items.")
            return redirect("/home")
        
    else:
        flash("Please login to edit an order.", 'warning')
        return redirect('/')


@app.route('/random-items')
def get_rando():
    items = Item.query.order_by(random()).limit(10).all()
    return render_template('random.html', items=items)