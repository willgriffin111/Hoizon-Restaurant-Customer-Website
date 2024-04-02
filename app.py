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
    return render_template('userFrontPage.html', menuitems=session['menu_items'], menuitemslength=menuitemslength, isLoggedIn=session['isLoggedIn'])

@app.route('/api/data', methods=['POST'])
def receive_data():
    data_string = request.data.decode('utf-8')
    # Convert the string to a Python object (list of dictionaries)
    session['menu_items'] = json.loads(data_string)
    # Process the data as needed
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