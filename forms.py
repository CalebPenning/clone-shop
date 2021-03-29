from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, Length

class SignUpForm(FlaskForm):
    """Form used for user sign up."""
    
    username = StringField(
        'Username', 
        validators=[
            DataRequired, 
            Length(min=1, max=50)
            ]
        )
    
    email = StringField(
        'E-mail',
        validators=[
            DataRequired(message="Please enter an email address."),
            Email(message="Please enter a valid email address.")
        ]
    )
    
    password = PasswordField(
        'Password',
        validators=[
            Length(min=6, max=40),
            DataRequired(message="Please enter a password.")
        ]
    )
    
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(message="Please enter your first name.")
        ]
    )
    
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(message="Please enter your last name.")
        ]
    )