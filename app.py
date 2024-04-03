#Alex Rogers22018703
import string
import mysql.connector
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
from mysql.connector import Error , errorcode
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'Horizon' 


""" ROOTING PLEASE ADD COMMENT WHEN COMMITING - OSCAR """

@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('isLoggedIn'):
        session['isLoggedIn'] = False
    if not session.get('menu_items'):
        session['menu_items'] = []
    print(session['menu_items'])
    menuitemslength =  len(session['menu_items'])
    menulist = [
    {"id": 1, "name": "Teriyaki Chicken", "price": 9.99, "description": "Indulge in our Teriyaki Chicken – succulent grilled chicken in a rich, aromatic sauce. Savour tender bites, expertly spiced.", "category": "mains"},
    {"id": 2, "name": "Chicken Tikka Curry", "price": 8.99, "description": "Indulge in our Chicken Tikka Curry – succulent grilled chicken in a rich, aromatic curry. Savour tender bites, expertly spiced.", "category": "mains"},
    {"id": 3, "name": "Tiramisu", "price": 5.99, "description": "Delight in our Tiramisu – layers of creamy mascarpone cheese, coffee-soaked ladyfingers, and cocoa powder.", "category": "desserts"},
    {"id": 4, "name": "Mojito", "price": 6.99, "description": "Refresh yourself with our classic Mojito – a zesty mix of fresh mint, lime juice, sugar, and rum.", "category": "drinks"},
    {"id": 5, "name": "Caprese Salad", "price": 7.99, "description": "Enjoy our Caprese Salad – a vibrant mix of fresh tomatoes, creamy mozzarella, fragrant basil, and balsamic glaze.", "category": "starters"},
    {"id": 6, "name": "Spaghetti Bolognese", "price": 10.99, "description": "Savour our Spaghetti Bolognese – al dente pasta tossed in a rich, meaty sauce, topped with grated Parmesan cheese.", "category": "mains"},
    {"id": 7, "name": "Chocolate Cake", "price": 4.99, "description": "Indulge in our decadent Chocolate Cake – moist layers of chocolate sponge, filled and frosted with rich chocolate ganache.", "category": "desserts"},
    {"id": 8, "name": "Martini", "price": 8.99, "description": "Sip on our Martini – a classic cocktail made with gin and vermouth, garnished with an olive or a lemon twist.", "category": "drinks"},
    {"id": 9, "name": "Bruschetta", "price": 6.49, "description": "Enjoy our Bruschetta – toasted bread topped with ripe tomatoes, fresh basil, garlic, and olive oil.", "category": "starters"},
    {"id": 10, "name": "Grilled Salmon", "price": 12.99, "description": "Relish our Grilled Salmon – perfectly cooked salmon fillet served with lemon wedges and dill sauce.", "category": "mains"},
    {"id": 11, "name": "Cheesecake", "price": 5.49, "description": "Indulge in our creamy Cheesecake – a smooth and velvety dessert with a buttery biscuit base.", "category": "desserts"},
    {"id": 12, "name": "Cosmopolitan", "price": 7.49, "description": "Enjoy our Cosmopolitan – a refreshing cocktail made with vodka, triple sec, cranberry juice, and freshly squeezed lime juice.", "category": "drinks"},
    {"id": 13, "name": "Garlic Bread", "price": 4.49, "description": "Savour our Garlic Bread – slices of crusty bread brushed with garlic-infused butter, toasted to perfection.", "category": "starters"},
    {"id": 14, "name": "Beef Burger", "price": 11.99, "description": "Indulge in our Beef Burger – a juicy beef patty topped with lettuce, tomato, onion, and melted cheese, served in a sesame seed bun.", "category": "mains"},
    {"id": 15, "name": "Apple Pie", "price": 6.49, "description": "Enjoy our classic Apple Pie – sweet, tender apples baked in a flaky, buttery pastry, served warm with a scoop of vanilla ice cream.", "category": "desserts"},
    {"id": 16, "name": "Margarita", "price": 7.99, "description": "Sip on our Margarita – a refreshing cocktail made with tequila, lime juice, triple sec, and simple syrup, served with a salted rim.", "category": "drinks"},
    {"id": 17, "name": "Caesar Salad", "price": 8.49, "description": "Relish our Caesar Salad – crisp romaine lettuce tossed in Caesar dressing, topped with croutons and Parmesan cheese.", "category": "starters"},
    {"id": 18, "name": "Steak", "price": 14.99, "description": "Savour our Steak – tender, juicy steak cooked to your liking, served with your choice of sides and sauce.", "category": "mains"},
    {"id": 19, "name": "Panna Cotta", "price": 5.99, "description": "Delight in our creamy Panna Cotta – a silky-smooth dessert topped with fresh berries and a drizzle of raspberry coulis.", "category": "desserts"},
    {"id": 20, "name": "Sangria", "price": 8.49, "description": "Enjoy our Sangria – a refreshing drink made with red wine, mixed fruits, orange juice, and brandy, served over ice.", "category": "drinks"}
    ]   
    return render_template('userFrontPage.html',menutable=menulist, menuitems=session['menu_items'], menuitemslength=menuitemslength, isLoggedIn=session['isLoggedIn'])

@app.route('/api/data', methods=['POST'])
def receive_data():
    data_string = request.data.decode('utf-8')
    # Convert the string to a Python object (list of dictionaries)
    session['menu_items'] = json.loads(data_string)
    # Process the data as needed
    combined_items = []
    for item in session['menu_items']:
        found = False
        for combined_item in combined_items:
            if item['id'] == combined_item['id']:
                combined_item['ammount'] = str(int(combined_item['ammount']) + int(item['ammount']))
                combined_item['price'] += item['price']
                found = True
                break
        if not found:
            combined_items.append(item)

    session['menu_items'] = combined_items
    print(session['menu_items'])
    menuitemslength =  len(session['menu_items'])
    return jsonify(menuitemslength)

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    menuitemslength = len(session['menu_items'])
    ordertotal = 0
    for item in session['menu_items']:
        ordertotal += item['price']
    
    return render_template('userOrder.html', ordertotal=ordertotal, menuitems=session['menu_items'],menuitemslength=menuitemslength, isLoggedIn=session['isLoggedIn'])

@app.route('/remove_item', methods=['POST'])
def remove_item():
    item_id = request.json['id']
    filtered_data = [item for item in session['menu_items'] if int(item['id']) != item_id]
    session['menu_items'] = filtered_data
    # Remove the item with the specified ID from the array or perform any other necessary actions
    # Return a response to the client if needed
    return 'Item removed successfully'

@app.route('/reservations', methods=['GET', 'POST'])
def reservationspage():
    return render_template('userReservations.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    form = {}
    error = ''
    try:
        if request.method == "POST":
            email = request.form.get('email')
            password = request.form.get('password')
            if email and password:  # Simplified the condition
                conn = dbfunc.getConnection()
                if conn:
                    with conn.cursor() as dbcursor:
                        dbcursor.execute("SELECT User_Password, user_type, User_Firstname, User_ID FROM user_data WHERE User_Email = %s;", (email,))
                        data = dbcursor.fetchone()
                        if data:
                            if sha256_crypt.verify(password, data[0]):
                                session['userid'] = int(data[3])
                                session['logged_in'] = True
                                session['username'] = str(data[2])
                                session['usertype'] = str(data[1])
                                return redirect(url_for('Horizon_Front'))
                            else:
                                error = "Invalid credentials username/password, try again."
                        else:
                            error = "Email / password does not exist, login again"
                else:
                    error = "Database connection error"
    except Exception as e:
        error = str(e) + " <br/> Invalid credentials, try again."

    return render_template("userLogin.html", form=form, error=error, logged_in=session.get('logged_in'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = ''
    try:
        if request.method == "POST":
            email = request.form.get('email')
            firstname = request.form.get('firstname')  # corrected variable names
            email = request.form.get('email')  # corrected variable names
            password = request.form.get('password')
            if email and firstname and password:  # Simplified the condition
                conn = dbfunc.getConnection()
                if conn:
                    with conn.cursor() as dbcursor:
                        dbcursor.execute("SELECT * FROM user_data WHERE User_Email = %s;", (email,))
                        rows = dbcursor.fetchall()
                        if rows:
                            error = "Email already in-use, please use another or log in"
                        else:
                            password_hash = sha256_crypt.hash(password)
                            dbcursor.execute("INSERT INTO user_data (User_FirstName, User_LastName, User_Password, User_Email) VALUES (%s, %s, %s, %s)", (firstname, secondname, password_hash, email))
                            conn.commit()
                            session['logged_in'] = True
                            session['username'] = firstname
                            session['usertype'] = 'standard'
                            return redirect(url_for('Horizon_Front'))
                else:
                    error = "Database connection error"
            else:
                error = "Incomplete parameters"
    except Exception as e:
        error = str(e)

    return render_template("userRegister.html", error=error, logged_in=session.get('logged_in'))


@app.route('/resetpassword', methods=["GET","POST"])
def resetpassword():
    form={}
    error = ''
    try:	
        if request.method == "POST":            
            email = request.form['email']
            password = request.form['password']            
            form = request.form
            print('Password change start 1.1')
            
            if email != None and password != None:  #check if em or pw is none          
                conn = dbfunc.getConnection() 
                if conn != None:    #Checking if connection is None                    
                    if conn.is_connected(): #Checking if connection is established                        
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object                                                 
                        dbcursor.execute("SELECT User_Password, user_type, User_Firstname, User_ID \
                            FROM user_data WHERE User_Email = %s;", (email,))                                                
                        data = dbcursor.fetchone()
                        #print(data[0])
                        if dbcursor.rowcount < 1: #this mean no user exists                         
                            error = "Email does not exist, login again"
                            return render_template("userResetPassword.html", error=error, logged_in=session['logged_in'])
                        else:                            
                            #data = dbcursor.fetchone()[0] #extracting password   
                            # verify passowrd hash and password received from user                                                             
                            password = sha256_crypt.hash((str(password)))
                            dbcursor.execute("UPDATE user_data SET User_Password = %s WHERE User_Email = %s;", (password,email,)) 
                            conn.commit()
                            dbcursor.close()
                            conn.close()                                
                            return redirect(url_for('home'))
                                                          
                    gc.collect()
                    print('login start 1.10')
                    return render_template("userResetPassword.html", form=form, error=error, logged_in=session['logged_in'])
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("userResetPassword.html", form=form, error = error, logged_in=session['logged_in'])   
    
    return render_template("userResetPassword.html", form=form, error = error, logged_in=session['logged_in'])


@app.route('/privacy')
def privacy():
    return render_template('userPolicyPage.html', logged_in=session['logged_in'])




def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            if session["logged_in"]:
                return f(*args, **kwargs)
            else:
                flash('You need to login first', 'error')
                return redirect(url_for('login'))
        else:
            flash('You need to login first', 'error')
            return redirect(url_for('login'))
    return wrap

@app.route('/account')
@login_required
def account():
    return render_template('userAccount.html',  isLoggedIn=session['isLoggedIn'])

 


@app.route("/logout")
@login_required
def logout():    
    session.clear() #clears session variables
    print("You have been logged out!")
    gc.collect()
    return redirect(url_for('home'))

app.run(debug=True)