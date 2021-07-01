# **Flask Clone Shop**

[This project is hosted here](http://clone-shop.herokuapp.com/home)

## **Description**

This is a Flask application that I built for Springboard's Software Engineering Track.
It is an end-to-end project that mimics an online shopping experience, using cannabis as a theme. 
I built it for a few reasons:
- Cannabis is one of my passions. It's my current industry, it's helped me a ton in the past with pain and other ailments, and it's very interesting.
- eCommerce is becoming a thing for recreational and medical markets. Though it is not currently possible to PAY for a lot of products online, federal legalization and/or alternate payment solutions will make it possible. And fulfillment services are still vital to the industry. So it's never too early to start thinking about products that make these things possible.
- I wanted to have an app with real information! There is actual strain information on each page. Everything is pulled from Evan Busse's Strain API (which is now offline unfortunately), and displays a description, as well as positive, negative, and medical effects that come along with use.


## **Getting Setup**

- Download or clone this code
- Have Python 3.7.7+ installed as well as pip
- Have postgres or another compatible db installed. 
- Create a database and update keys.py to include your URI
- `pip install requirements.txt`
- `python seed.py`
- Change your FLASK_ENV to development
- `flask run`

That should get you going on your local machine.

