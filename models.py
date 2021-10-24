from datetime import datetime
from random import randint, choice

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    """User instance. testing..."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer,
                   primary_key=True,
                   unique=True,
                   nullable=False)
    
    username = db.Column(db.Text,
                         unique=True,
                         nullable=False)
    
    password = db.Column(db.Text,
                         nullable=False)

    email = db.Column(db.Text,
                      nullable=False,
                      unique=True)
    
    first_name = db.Column(db.Text,
                           nullable=False,
                           default="New")
    
    last_name = db.Column(db.Text,
                          nullable=False,
                          default="User")
    
    birthday = db.Column(db.DateTime,
                         nullable=False)
    
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.now())
    
    orders = db.relationship('Order',
                             backref='user')
    
    def __repr__(self):
        u = self
        return f"<User: {u.username}, Email: {u.email}, Name: {u.first_name} {u.last_name}>"

    @classmethod
    def register(cls, form):
        username = form.username.data
        password = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        birthday = form.birthday.data
        
        hashed = bcrypt.generate_password_hash(password)
        
        hashed_utf8 = hashed.decode("utf8")
        
        return cls(username=username,
                   password=hashed_utf8,
                   email=email,
                   first_name=first_name,
                   last_name=last_name,
                   birthday=birthday,
                   created_at=datetime.now())
        
    @classmethod
    def authenticate(cls, form):
        u = User.query.filter_by(username=form.username.data).first_or_404()
        pwd = form.password.data
        
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        elif u and bcrypt.check_password_hash(u.password, pwd) == False:
            form.password.errors = ["Invalid password"]
            return False
        
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    order_status = db.Column(
        db.String(20),
        nullable=False,
        default="active"
    )
    
    items = db.relationship(
        'OrderItem',
        backref='order'
    )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )
    
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    item_id = db.Column(
        db.Integer,
        db.ForeignKey('items.id'),
        primary_key=True
    )
    
    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id'),
        primary_key=True
    )
    
    quantity = db.Column(
        db.Integer,
        nullable=False
    )
    
class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    name = db.Column(
        db.String(100),
        nullable=False
    )
    
    description = db.Column(
        db.Text,
        unique=False,
        nullable=False,
        default="No description yet!"
    )
    
    race = db.Column(
        db.String(10),
        unique=False,
        nullable=False,
        default="hybrid"
    )
    
    price = db.Column(
        db.Integer,
        nullable=False,
        default=randint(0, 60)
    )
    
    # effects = db.relationship(
    #     'Effect',
    #     secondary="item_effects",
    #     backref="items"
    # )
    
    # flavors = db.relationship(
    #     'Flavor',
    #     secondary="item_flavors",
    #     backref="items"
    # )
    
    cart_additions = db.relationship(
        'OrderItem',
        backref='cart_items'
    )
    
class ItemEffect(db.Model):
    """Maps effects to strains."""
    __tablename__ = 'item_effects'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey('items.id')
    )

    effect_id = db.Column(
        db.Integer,
        db.ForeignKey('effects.id')
    )


class Effect(db.Model):
    """Effects that our strains can have."""

    __tablename__ = 'effects'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    effect_type = db.Column(
        db.Text,
        nullable=False
    )
    
    name = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )
    
    items = db.relationship(
        'Item',
        secondary='item_effects',
        backref='effects'
    )
    
class ItemFlavor(db.Model):
    __tablename__ = 'item_flavors'
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    item_id = db.Column(
        db.Integer,
        db.ForeignKey('items.id')
    )
    
    flavor_id = db.Column(
        db.Integer,
        db.ForeignKey('flavors.id')
    )
    
class Flavor(db.Model):
    """Flavors and smells that the plants can have"""
    
    __tablename__ = 'flavors'
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    name = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )
    
    items = db.relationship(
        'Item',
        secondary='item_flavors',
        backref='flavors'
    )