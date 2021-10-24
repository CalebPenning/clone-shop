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
> When the user submits the age verification form, it sends a POST request to this route. If the value of the input is a correctly formatted MM/DD/YYYY date, 
and it's the birthday of someone 21 or older, user will be redirected to /home with an of_age = True attribute on the session object. Otherwise, they will get an error message and be redirected to the form. Same goes for if the date entered is valid, but is the birthday of someone under 21.

- GET => "/sorry"
> Catch-all error page. If someone enters an incorrect url, or hits a broken link, they will be directed here. 

- GET => "/home"
> The first protected route in this application. If the user is logged in, i.e. has a user_id on their session, a User-centric homepage is rendered. If no user_id is present, but an of_age is, an anonymous homepage is rendered. This includes a warning to users that they cannot make orders. Otherwise, if neither are present, they will be redirected to /

- GET => "/users/signup"
> If a GET request is sent to this endpoint, and there is no user_id on the session, the signup form is rendered. Unregistered users can use this form to create an account.

- POST => "/users/signup" 
> If form data is successfully validated, a new user instance is created, that user is assigned a cart, and they are automatically signed up and redirected to the user home page. If form data is not validated, the form is rendered again, and a message describing the error is flashed at the top of the form.

- GET => "/users/login"
> Much like the sign up form, a user without a user_id on their session sending a GET request to this endpoint will get back a login form. Existing users can submit a correct username/password combination and be logged in again via session.

- GET => "/users/logout"
> If there's a user_id on the session, pop it off and redirect to the home directory. Same for if an of_age manages to stick on the session. Otherwise, redirect and tell the user that they are already not logged in, and there's not much we can do to log them out again.

- GET => "/users/:id/profile"
> Given a valid user id, return a page with information about them and their past orders.

- GET => "/users/:id/orders/:order_id/details"
> Given a valid user id, and a valid order id from that same user, return a table with information about the order, including contents of the order, item prices, grand total, and order number.

- GET => "/users/:id/orders/cart"
> Given a valid user id, return a page with information about the current user's cart. Users can modify and delete the contents of their cart here. 

- GET => "/users/:id/orders/cart/checkout"
> Given a valid user id, display a page with the current users cart information, including a grand total and all contents. Users can still edit orders on this page, or click "Place Order" to finalize.

- GET => "/shop/search"
> A route that uses query string params to search for items within the db. Users can search by either name or description of product. Only logged in users and users with an of_age attr on their session will get results back. Otherwise, they will be redirected to the home directory.

- GET => "/shop/items/:id/details"
> Given a valid item id, returns a page with information about a product. This includes the name, the variety, the pricing, a description, positive, negative, and medical effects. Users can also add products to their cart on this page, using a simple dropdown form. 

- POST => "/shop/items/:id/add"
> A route used to add items to the current user's cart. Takes an item ID. Only valid with a user_id on the session.

- POST => "/shop/items/:id/adjust"
> Used to adjust quantities in the existing user's cart. Takes an item ID. Only valid for logged in users.

- POST => "/shop/items/:id/delete"
> Deletes item from cart based on id. Only valid for logged in users.


### Warning
The app.py file is very long. Routes need to be condensed and broken up. I plan on updating this to Flask 2.0 soon to make use of proper HTTP verbs. 
