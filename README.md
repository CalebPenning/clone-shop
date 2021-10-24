# **Flask Clone Shop**

[This project is hosted here](http://clone-shop.herokuapp.com/home)

## **Description**

This is a Flask application that I built for Springboard's Software Engineering Track.
It is an end-to-end project that mimics an online shopping experience, using cannabis as a theme. 
I built it for a few reasons:
- Cannabis is one of my passions. It's my current industry, it's helped me a ton in the past with pain and other ailments, and it's very interesting.
- eCommerce is becoming a thing for recreational and medical markets. Though it is not currently possible to PAY for a lot of products online, federal legalization and/or alternate payment solutions will make it possible. And fulfillment services are still vital to the industry. So it's never too early to start thinking about products that make these things possible.
- I wanted to have an app with real information! There is actual strain information on each page. Everything is pulled from Evan Busse's Strain API (which is now offline unfortunately), and displays a description, as well as positive, negative, and medical effects that come along with use.


## **Running The App On Your Machine**

- Download or clone this code
- Have Python 3.7.7+ installed as well as pip
- Have postgres or another compatible db installed. 
- Create a database and update keys.py to include your URI
- `pip install requirements.txt`
- `python seed.py`
- Change your FLASK_ENV to development
- `flask run`

That should get you going on your local machine.

## **Routes**
- GET => "/"
> The "home directory" for the app. If you have a user_id, or an of_age=True attribute on your session object, you will be redirected to /home to begin browsing. Otherwise, you will be directed to /verify-age to attest that you are over the age of 21. 

- GET => "/verify-age"
> This route acts as the gateway for anonymous users (not logged in/registered) to browse the storefront. If you aren't already logged in, or don't have an of_age=True attribute in your session, it renders the age verification form. Users must enter their date of birth in an MM/DD/YYYY format. If successful, users can browse the store, but cannot make an order. If they try, they will be redirected to /login.

- POST => "/verify-age"
> When the user submits the age verification form, it sends a POST request to this route. 

### Warning
The app.py file is very long. Routes need to be condensed and broken up. I plan on updating this to Flask 2.0 soon to make use of proper HTTP verbs. 
