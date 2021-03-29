import os
from flask import Flask, redirect, request, render_template, session, url_for, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from keys_and_helpers import DATABASE_URI, SECRET_KEY

from models import db, connect_db, Order, OrderItem, Item, ItemEffect, Effect, ItemFlavor, Flavor, User

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

@app.route('/', methods=["GET", "POST"])
def homepage():
    items = Item.query.limit(20).all()
    
    if 'user_id' in session:
        return render_template('user_home.html', items=items)
    
    return render_template('anon_home.html', items=items)