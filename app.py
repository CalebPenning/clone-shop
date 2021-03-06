import os
from flask import Flask, redirect, request, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import random
from helpers import check_birthday, do_signup, get_user_from_session, compare_users, confirm_passwords, add_item, adjust_quantity, remove_items, get_user_cart, test_search
from keys import DATABASE_URI, SECRET_KEY

from models import db, connect_db, Order, Item, User
from forms import SignUpForm, LoginForm, ItemQuantityForm, AgeVerificationForm

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

# Homepage of the application
## On hitting this route, check the session data
### If User has either a user_id: id or of_age: True in session
### Redirect to store homepage
### Otherwise, send them to the age verification form

@app.route('/')
def go_home():
    if 'of_age' not in session and 'user_id' not in session:
        return redirect('/verify-age')
    
    elif 'of_age' in session or 'user_id' in session:
        return redirect('/home')

### On a GET request,
### this route renders an html form for the current user to 
### enter their birthday, and if they are over 21, enter the store

### on POST, 
@app.route('/verify-age', methods=["GET", "POST"])
def check_user_age():
    if 'of_age' and 'user_id' not in session:
        form = AgeVerificationForm()
        if request.method == "POST":
            print(form)
            if form.validate_on_submit():
                verified = check_birthday(form.birthday.data)

                if verified == True:
                    session['of_age'] = True
                    flash('Age verified. Feel free to browse. Please sign up before placing an order.', 'success')
                    return redirect('/home')
                
                elif not form.birthday or not verified or verified == False:
                    flash("We're sorry. You are not of age. If you input your age incorrectly, try again.", "danger")
                    return redirect('/sorry')
            else:
                flash("Please enter a valid birthday", "warning")
                return redirect('/')
            
        else:
            return render_template('verify_age.html', form=form)
    
    elif 'of_age' or 'user_id' in session:
        flash('Age already verified.', 'danger')
        return redirect('/home')
    
    else:
        flash("Something went wrong. Please try again")
        return redirect('/')
    
@app.route('/sorry')
def apologize():
    return redirect('/verify-age')

@app.route('/home')
def homepage():
    items = Item.query.order_by(random()).limit(21).all()
    
    if 'user_id' in session:
        user = get_user_from_session(session['user_id'])
        return render_template('user_home.html', items=items, user=user)
    
    elif "of_age" in session:
        return render_template('anon_home.html', items=items)
    
    else:
        return redirect('/')

@app.route('/users/signup', methods=["GET", "POST"])
def user_signup():
    form = SignUpForm()
    
    if 'user_id' in session:
        flash("You are already signed up. You've been redirected.", 'warning')
        return redirect('/')
    
    # check for valid form data, then check the two password fields
    if form.validate_on_submit():
        if confirm_passwords(form):
            if 'of_age' in session:
                session.pop('of_age')
            new_user = do_signup(form)
            session['user_id'] = new_user.username
            flash("Account created successfully. Welcome!", 'success')
            return redirect('/home')
        else:
            flash("The passwords you entered did not match. Try again.", "warning")
    elif request.method == "POST" and not form.validate_on_submit():
        flash("There was an issue signing you up. Double check all fields and try again", "warning")

    return render_template('users/signup.html', form=form)

@app.route('/users/login', methods=["GET", "POST"])
def login_user():
    form = LoginForm()
    if request.method == "POST":
        user = User.authenticate(form)
        if user:
            if 'of_age' in session:
                session.pop('of_age')
                session['user_id'] = user.username
                flash(f"Welcome back, {user.username}!", 'success')
                return redirect('/home')
            else:               
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
        if 'of_age' in session:
            session.pop('of_age')
            flash('Successfully logged out.', 'success')
            return redirect('/')
        else:
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
            return render_template("users/profile.html", user=user)
        
        else:
            flash("You do not have permission to view that page.", 'warning')
            return redirect('/users/login')
        
# @app.route('/users/<int:id>/orders')
# def show_prev_orders(id: int):
#     if 'user_id' in session:
#         if compare_users(session['user_id'], id):    
#             curr_user = get_user_from_session(session['user_id'])
#             orders = Order.query.filter_by(user_id=id).filter(Order.order_status == 'complete').all()
#             return render_template('users/orders.html', user=curr_user, orders=orders)
#         else:
#             flash("You do not have permission to view that page.", 'danger')
#             return redirect('/')
    
#     else:
#         flash("Please login to access your past orders", 'warning')
#         return redirect('/users/login')
    
@app.route('/users/<int:u_id>/orders/<int:o_id>/details')
def show_order_details(u_id: int, o_id: int):
    if compare_users(session['user_id'], u_id):
        order = (Order
                 .query
                 .filter_by(user_id=u_id)
                 .filter(Order.id == o_id)
                 .first())
        total = sum([i.quantity * i.cart_items.price for i in order.items])
        user = get_user_from_session(session['user_id'])
        return render_template('users/orders/details.html', user=user, order=order, total=total)
    
    else:
        flash('You do not have permission to view that page', 'danger')
        return redirect('/')

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
            if request.method == 'POST':
                cart.order_status = 'complete'
                new_cart = Order(user_id=user.id)
                db.session.add(new_cart)
                
                try:
                    db.session.commit()
                    flash("Order complete. You've been redirected home.", 'success')
                    return redirect('/')
                
                except IntegrityError:
                    flash("There was an issue completing your order. Please try again.", 'warning')
                    return redirect(f"/users/{user.id}/cart")
                
            else:
                total = sum([i.quantity * i.cart_items.price for i in cart.items])
                return render_template('users/checkout/confirm_order.html', user=user, cart=cart, total=total)
        
        

@app.route('/shop/search')
def get_search_results():
    if 'user_id' in session:
        param = request.args.get('search-param')
        keyword = request.args.get('keyword')
        # if user tries to submit blank search, redirect and warn them
        if not param or not keyword:
            flash("Please enter a search parameter", 'warning')
            return redirect('/')
        # Title case the param as it  is in our DB
        param = param.title()
        print(param, keyword)
        search_results = test_search(param, keyword)
        print(search_results)
        curr_user = get_user_from_session(session['user_id'])
        return render_template('shop/search.html', results=search_results, user=curr_user)
    # same functionality but for guest users 
    elif 'of_age' in session:
        param = request.args.get('search-param')
        keyword = request.args.get('keyword')
        if not param or not keyword:
            flash("Please enter a search parameter", 'warning')
            return redirect('/')
        param = param.title()
        search_results = test_search(param, keyword)
        print(search_results)
        return render_template('shop/search.html', results=search_results)
    # Otherwise NO 
    else:
        flash('Please verify your age, login, or create an account to browse the shop.', 'danger')
        return redirect('/')
    
        
    
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
            flash("Item added successfully.", 'success')
            return redirect(f"/shop/items/{id}/details")
        else:
            flash("We had an issue adding the item to your cart. Please try again.", 'danger')
            return redirect(f"/shop/items/{id}/details")
    else:
        flash("You do not have permission to make an order. Login to do so.", 'danger')
        return redirect('/users/login')
    

@app.route('/shop/items/<int:id>/adjust', methods=["POST"])
def adjust_item_quantity(id):
    if 'user_id' in session:
        adjusted_items = adjust_quantity(id, request, session['user_id'])
        user = get_user_from_session(session['user_id'])
        if adjusted_items:
            flash("Item quantity adjusted.", 'success')
            return redirect(f"/users/{user.id}/cart")
        else:
            flash("Could not adjust items. Please try again.", 'danger')
            return redirect(f"/users/{user.id}/cart")
        
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


# @app.route('/random-items')
# def get_rando():
#     items = Item.query.order_by(random()).limit(10).all()
#     return render_template('random.html', items=items)

@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404
