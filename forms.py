from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, IntegerField, DateTimeField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, email_validator, InputRequired

class SignUpForm(FlaskForm):
    """Form used for user sign up."""
    
    username = StringField(
        'Username', 
        validators=[
            DataRequired(message="Please enter a username."), 
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
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            Length(min=6, max=40),
            DataRequired(message="Please confirm your password.")
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
    
    birthday = DateTimeField(
        'Birthday MM/DD/YYYY',
        validators=[
            DataRequired()
        ],
        format="%m/%d/%Y"
    )
    
class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Please enter your username.")
        ])
    
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Please enter your password.")
        ]
    )

class ItemQuantityForm(FlaskForm):
    quantity = SelectField(
        'Quantity',
        validators=[InputRequired()],
        coerce=int,
        choices=[(num, num) for num in range(0, 13)]
    )
    

class AgeVerificationForm(FlaskForm):
    birthday = DateTimeField(
        "Your Birthday",
        validators=[
            DataRequired()
            ],
        format="%m/%d/%Y"
    )