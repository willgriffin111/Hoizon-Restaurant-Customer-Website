#Alex Rogers22018703
import string
import mysql.connector
from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
from mysql.connector import Error , errorcode
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'Horizon' 


""" ROOTING PLEASE ADD COMMENT WHEN COMMITING - OSCAR """

@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        session['logged_in'] = False
    isLoggedIn = session['logged_in'] 
    return render_template('userFrontPage.html', isLoggedIn=isLoggedIn)

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    return render_template('userFrontPage.html')


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
    if (session['usertype'] == 'admin'):
         userid = str(session['userid'])
         conn = dbfunc.getConnection()
         if conn != None:    #Checking if connection is None         
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object     
            dbcursor.execute('SELECT * FROM USER_DATA WHERE User_ID = %s;',(userid,))  
            data = dbcursor.fetchone()
            userdata = [data[1],data[2],data[4]]
            dbcursor.execute('SELECT * FROM BOOKING_INFO ORDER BY Booking_ID LIMIT 5;')   
		    #print('SELECT statement executed successfully.')             
            rows = dbcursor.fetchall()
            datarows=[]			
            for row in rows:
                data = list(row)                    
                print(data)
                booking_info = []
                booking_info.append(row[0])
                booking_info.append(row[2].strftime("%x"))
                booking_info.append(row[4])
                booking_info.append(row[5])
                dbcursor.execute('SELECT * FROM TRAVEL_INFO WHERE Travel_ID = %s;', (str(row[7]),))
                travel = dbcursor.fetchall()
                print(travel)
                booking_info.append(travel[0][1])
                booking_info.append(travel[0][2])
                booking_info.append(travel[0][3])
                booking_info.append(travel[0][4])
                print(booking_info)
                datarows.append(booking_info)
            dbcursor.execute('SELECT * FROM USER_DATA ORDER BY User_ID LIMIT 5;')   
		    #print('SELECT statement executed successfully.')             
            rows = dbcursor.fetchall()
            userrows=[]			
            for row in rows:
                data = list(row)                    
                print(data)
                user_info = []
                user_info.append(row[0])
                user_info.append(row[1])
                user_info.append(row[2])
                user_info.append(row[4])
                user_info.append(row[5])
                print(user_info)
                userrows.append(user_info)	
            dbcursor.close()              
            conn.close() #Connection must be closed
		    #print(datarows)
		    #print(len(datarows))	
            return render_template('Admin.html', logged_in=session['logged_in'], userinfo=userdata, bookingdata=datarows,userdata=userrows, userid=userid)
         else:
            print('DB connection Error')
            return redirect(url_for('home'))
    else:
        userid = str(session['userid'])
        
        conn = dbfunc.getConnection()
        if conn != None:    #Checking if connection is None         
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object     
            dbcursor.execute('SELECT * FROM USER_DATA WHERE User_ID = %s;', (userid,))  
            data = dbcursor.fetchone()
            userdata = [data[1],data[2],data[4]]
            dbcursor.execute('SELECT * FROM BOOKING_INFO WHERE User_ID = %s LIMIT 5;', (userid,))   
		    #print('SELECT statement executed successfully.')             
            rows = dbcursor.fetchall()
            datarows=[]			
            for row in rows:
                data = list(row)                    
                print(data)
                booking_info = []
                booking_info.append(row[0])
                booking_info.append(row[2].strftime("%x"))
                booking_info.append(row[4])
                booking_info.append(row[5])
                dbcursor.execute('SELECT * FROM TRAVEL_INFO WHERE Travel_ID = %s ;', (str(row[7]),))
                travel = dbcursor.fetchall()
                print(travel)
                booking_info.append(travel[0][1])
                booking_info.append(travel[0][2])
                booking_info.append(travel[0][3])
                booking_info.append(travel[0][4])
                print(booking_info)
                datarows.append(booking_info)			
            dbcursor.close()              
            conn.close() #Connection must be closed
		    #print(datarows)
		    #print(len(datarows))	
            return render_template('userAccount.html', logged_in=session['logged_in'], userinfo=userdata, bookingdata=datarows,userid=userid)
        else:
            print('DB connection Error')
            return redirect(url_for('home'))

 


@app.route("/logout")
@login_required
def logout():    
    session.clear() #clears session variables
    print("You have been logged out!")
    gc.collect()
    return redirect(url_for('home'))

app.run(debug=True)