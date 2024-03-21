#Alex Rogers22018703
import string
import mysql.connector
from flask import Flask, render_template, request, session, redirect, url_for
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
import mysql.connector, dbfunc
from mysql.connector import Error, errorcode

from datetime import datetime, timedelta
import datetime
app = Flask(__name__)
app.secret_key = 'Horizon' 

@app.route('/')
def Horizon_Front():
    if not session.get('logged_in'):
        session['logged_in'] = False
    return render_template('HorizonFrontPage.html', logged_in=session['logged_in'])

@app.route('/Login', methods=["GET","POST"])
def Login():
    form={}
    error = ''
    try:	
        if request.method == "POST":            
            email = request.form['email']
            password = request.form['password']            
            form = request.form
            print('login start 1.1')
            
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
                            error = "Email / password does not exist, login again"
                            return render_template("Login.html", error=error, logged_in=session['logged_in'])
                        else:                            
                            #data = dbcursor.fetchone()[0] #extracting password   
                            # verify passowrd hash and password received from user                                                             
                            if sha256_crypt.verify(request.form['password'], str(data[0])):
                                dbcursor.close()
                                conn.close()
                                gc.collect()   
                                session['userid'] = int(data[3])
                                print(session['userid'])                             
                                session['logged_in'] = True     #set session variables
                                session['username'] = str(data[2])
                                session['usertype'] = str(data[1])                          
                                print("You are now logged in")                                
                                return redirect(url_for('Horizon_Front'))
                            else:
                                error = "Invalid credentials username/password, try again."
                                dbcursor.close()
                                conn.close()
                                gc.collect()                               
                    gc.collect()
                    print('login start 1.10')
                    return render_template("Login.html", form=form, error=error, logged_in=session['logged_in'])
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("Login.html", form=form, error = error, logged_in=session['logged_in'])   
    
    return render_template("Login.html", form=form, error = error, logged_in=session['logged_in'])

@app.route('/SignUp', methods=['POST', 'GET'])
def SignUp():
    error = ''
    print('Register start')
    try:
        if request.method == "POST":
            email = request.form['email']         
            Firstname = request.form['Firstname']
            Seccondname = request.form['Seccondname']
            password = request.form['password']   
            print(password,Seccondname,Firstname,email)                 
            if Firstname != None and Seccondname != None and password != None and email != None:
                print("sent request")
                conn = dbfunc.getConnection()           
                if conn != None:    #Checking if connection is None           
                    if conn.is_connected(): #Checking if connection is established
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #here we should check if username / email already exists                                                           
                        password = sha256_crypt.hash((str(password)))           
                        Verify_Query = "SELECT * FROM user_data WHERE User_Email = %s;"
                        dbcursor.execute(Verify_Query,(email,))
                        rows = dbcursor.fetchall()           
                        if dbcursor.rowcount > 0:   #this means there is a user with same name
                            print('Email already in-use, please use another or log in')
                            error = "Email already in-use, please use another or log in"
                            return render_template("SignUp.html", error=error, logged_in=session['logged_in'])    
                        else:   #this means we can add new user             
                            dbcursor.execute("INSERT INTO user_data (User_FirstName, User_LastName, User_Password, \
                                 User_Email) VALUES (%s, %s, %s, %s)", (Firstname, Seccondname, password, email))                
                            conn.commit()  #saves data in database              
                            print("Thanks for registering!")
                            dbcursor.execute('SELECT User_ID FROM USER_DATA WHERE User_FirstName = %s AND User_LastName = %s AND User_Email = %s;', (Firstname, Seccondname, email))
                            data = dbcursor.fetchone()
                            session['userid'] = data[0]
                            print(session['userid'])
                            dbcursor.close()
                            conn.close()
                            gc.collect()                        
                            session['logged_in'] = True     #session variables
                            session['username'] = Firstname
                            session['usertype'] = 'standard'   #default all users are standard
                            return redirect(url_for('Horizon_Front'))
                    else:                        
                        print('Connection error')
                        return 'DB Connection Error'
                else:                    
                    print('Connection error')
                    return 'DB Connection Error'
            else:                
                print('empty parameters')
                return render_template("SignUp.html", error=error, logged_in=session['logged_in'])
        else:            
            return render_template("SignUp.html", error=error, logged_in=session['logged_in'])        
    except Exception as e:                
        return render_template("SignUp.html", error=e, logged_in=session['logged_in'])    
    return render_template("SignUp.html", error=error, logged_in=session['logged_in'])

@app.route('/Changepass', methods=["GET","POST"])
def ChangePass():
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
                            return render_template("ChangePass.html", error=error, logged_in=session['logged_in'])
                        else:                            
                            #data = dbcursor.fetchone()[0] #extracting password   
                            # verify passowrd hash and password received from user                                                             
                            password = sha256_crypt.hash((str(password)))
                            dbcursor.execute("UPDATE user_data SET User_Password = %s WHERE User_Email = %s;", (password,email,)) 
                            conn.commit()
                            dbcursor.close()
                            conn.close()                                
                            return redirect(url_for('Horizon_Front'))
                                                          
                    gc.collect()
                    print('login start 1.10')
                    return render_template("ChangePass.html", form=form, error=error, logged_in=session['logged_in'])
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("ChangePass.html", form=form, error = error, logged_in=session['logged_in'])   
    
    return render_template("ChangePass.html", form=form, error = error, logged_in=session['logged_in'])


@app.route('/Policies')
def Policies():
    return render_template('Policies.html', logged_in=session['logged_in'])

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            if(session["logged_in"] == True):
                return f(*args, **kwargs)
            else:
                print("You need to login first")
                return redirect(url_for('Login', error='You need to login first')) 
        else:            
            print("You need to login first")
            return redirect(url_for('Login', error='You need to login first'))   
    return wrap

@app.route('/Account')
@login_required
def Account():
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
            return redirect(url_for('Horizon_Front'))
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
            return render_template('Account.html', logged_in=session['logged_in'], userinfo=userdata, bookingdata=datarows,userid=userid)
        else:
            print('DB connection Error')
            return redirect(url_for('Horizon_Front'))

 


@app.route("/logout")
@login_required
def logout():    
    session.clear() #clears session variables
    print("You have been logged out!")
    gc.collect()
    return redirect(url_for('Horizon_Front'))


app.run(debug=True)