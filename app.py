#Alex Rogers22018703
import string
import mysql.connector
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
from mysql.connector import Error , errorcode
import datetime
import json
from database import dbfunc
import re
from Functions import orderfunctions
import ast

app = Flask(__name__)
app.secret_key = 'Horizon' 


#sessionsVarriables
@app.route('/', methods=['GET', 'POST'])
def sessionsVarriables():
    if not session.get('isLoggedIn'):
        session['isLoggedIn'] = False
    if not session.get('menu_items'):
        session['menu_items'] = []
    return redirect(url_for('home'))

#root for front page
@app.route('/horizon', methods=['GET', 'POST'])
def home():
    session['resturantid'] = 1
    print(session['menu_items'])
    session['menuitemslength'] =  len(session['menu_items'])
    menulist = [] #blank data in case sql fails
    print('Collecting Menu') #sql to get the menu items from the menu
    try:
        conn = dbfunc.getConnection()           
        if conn != None:    #Checking if connection is None           
            if conn.is_connected(): #Checking if connection is established
                print('MySQL Connection is established')                          
                dbcursor = conn.cursor()    #Creating cursor object          
                dbcursor.execute('SELECT * FROM menu WHERE restaurant_id = %s;', (session['resturantid'],))      #Executing
                menulist = dbcursor.fetchall()
                tempmenu = []   #Temporary list used to store menu
                for menuitem in menulist:
                    # Check stock availability
                    dbcursor.execute("SELECT inventory_item_stock FROM inventory WHERE restaurant_id = %s AND inventory_item_name = %s",
                                    (session['resturantid'], menuitem[2]))
                    current_stock = dbcursor.fetchone()

                    menuitem = list(menuitem)
                    if(current_stock[0] > 0):
                        menuitem.append(True)
                    else:
                        menuitem.append(False)
                    
                    tempmenu.append(menuitem)#Adding each item
                
                menulist = tempmenu 
                dbcursor.close()
                conn.close()
                gc.collect()  
                print(menulist)                     
                return render_template('userFrontPage.html',menutable=menulist, menuitems=session['menu_items'], menuitemslength=session['menuitemslength'], isLoggedIn=session['isLoggedIn'])
            else:                        
                print('Connection error')
                return render_template('userFrontPage.html',menutable=menulist, menuitems=session['menu_items'], menuitemslength=session['menuitemslength'], isLoggedIn=session['isLoggedIn'])
        else:                    
            print('Connection error')
            return render_template('userFrontPage.html',menutable=menulist, menuitems=session['menu_items'], menuitemslength=session['menuitemslength'], isLoggedIn=session['isLoggedIn'])
                    
    except Exception as e: 
        print(e)               
        return render_template('userFrontPage.html',menutable=menulist, menuitems=session['menu_items'], menuitemslength=session['menuitemslength'], isLoggedIn=session['isLoggedIn'])
    

#root for getting the data when someone add something to order 
#this code will add the menu items slected by the user into their cart with quantity
@app.route('/addtocart', methods=['POST'])
def add_to_cart():
    data_string = request.data.decode('utf-8')
    # Convert the string to a Python object (list of dictionaries)
    session['menu_items'] = json.loads(data_string)
    #this combined any orders with the same id so if you want to add more on it auto combines
    combined_items = []
    for item in session['menu_items']:
        found = False
        for combined_item in combined_items:
            if item['id'] == combined_item['id']:
                combined_item['quantity'] = str(int(combined_item['quantity']) + int(item['quantity']))
                combined_item['price'] += item['price']
                found = True
                break
        if not found:
            combined_items.append(item)

    #adds the order list to the session verriable same as one stored on page
    session['menu_items'] = combined_items
    print(session['menu_items'])
    
    #returns length of menu array so that it can update cart counter
    session['menuitemslength'] =  len(session['menu_items'])
    return jsonify(session['menuitemslength'])



#for USER MESSAGES SUCCESS/MESSSAGE/ERROR
@app.route('/message/<string:message_type>/<string:message>')
def display_message(message_type, message):
    session['message'] = {'type': message_type, 'text': message}
    return '', 204


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
                        dbcursor.execute("SELECT customer_password, customer_first_name, customer_last_name FROM customer WHERE customer_email = %s;", (email,))
                        data = dbcursor.fetchone()
                        if data:
                            if sha256_crypt.verify(password, data[0]):
                                session['isLoggedIn'] = True
                                session['username'] = str(data[1]) + ' ' + str(data[2])
                                session['email'] = email
                                return redirect(url_for('sessionsVarriables'))
                            else:
                                error = "Invalid credentials username/password, try again."
                        else:
                            error = "Email / password does not exist, login again"
                else:
                    error = "Database connection error"
                
    except Exception as e:
        error = str(e) + " <br/> Invalid credentials, try again."

    print(error)
    return render_template("userLogin.html", form=form, error=error, menuitemslength=session['menuitemslength'], isLoggedIn=session['isLoggedIn'])

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = ''
    if request.method == "POST":
        firstname = request.form.get('firstname')  # corrected variable names
        lastname = request.form.get('lastname')  # corrected variable names
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')  # corrected variable names
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if not (firstname and lastname and email and phonenumber and password and password2):
            error = "Please fill in all fields"
        elif password != password2:
            error = "Passwords do not match"
        elif len(password) < 8:
            error = "Password should be at least 8 characters long"
        else:# Simplified the condition
            conn = dbfunc.getConnection()
            if conn:
                with conn.cursor() as dbcursor:
                    dbcursor.execute("SELECT * FROM customer WHERE customer_email = %s;", (email,))
                    rows = dbcursor.fetchall()
                    if rows:
                        error = "Email already in-use, please use another or log in"
                    else:
                        password_hash = sha256_crypt.hash(password)
                        print(phonenumber)
                        dbcursor.execute("INSERT INTO customer (customer_first_name, customer_last_name, customer_password, customer_email, customer_phone_details) VALUES (%s, %s, %s, %s, %s)", (firstname, lastname, password_hash, email, phonenumber))
                        conn.commit()
                        session['isLoggedIn'] = True
                        session['username'] = firstname + ' ' + lastname
                        session['email'] = email
                        print('register success')
                        flash('Registration successful', 'success')
                        return redirect(url_for('account'))
            else:
                error = "Database connection error"
    else:
        flash(error, 'error')
        print('register fail 1')
    return render_template("userRegister.html", error_message=error, logged_in=session.get('isLoggedIn'))



@app.route('/privacy')
def privacy():
    return render_template('userPolicyPage.html', isLoggedIn=session['isLoggedIn'])


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'isLoggedIn' in session:
            if session["isLoggedIn"]:
                return f(*args, **kwargs)
            else:
                
                flash('You need to login first', 'error')
                return redirect(url_for('login'))
        else:
            flash('You need to login first', 'error')
            return redirect(url_for('login'))
    return wrap



""" Orders systems """

#root for orders page
@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    #find length of menu items for cart counter
    session['menuitemslength'] = len(session['menu_items'])
    ordertotal = 0
    #figures out total price for cart total display
    for item in session['menu_items']:
        ordertotal += item['price']
    ordertotal  = round(ordertotal,2)
        
    #get all the table numbers of restaurant
    conn = dbfunc.getConnection()           
    if conn != None:    #Checking if connection is None           
        if conn.is_connected(): #Checking if connection is established
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object          
            dbcursor.execute('SELECT table_number FROM tables WHERE restaurant_id = %s;', (session['resturantid'],))      #Executing
            tablenumbers = dbcursor.fetchall()
            dbcursor.close()
            conn.close()
            gc.collect()   
            
    #makeing an order
    if request.method == "POST":
        if (session['menu_items'] != []):
            table_num = request.form['tableNumber']  
            #i stole this from someone in the tkinter system so if it break blame will or shabaz? 
            # I have to create this cause i need the bill_id for the order table when im inserting
            discount_applied = 0 #defulting cuz no user can have a discount applied
            bill_id = orderfunctions.create_bill(ordertotal, discount_applied)


            try:
                # Convert to integer safely
                table_num = int(table_num)

                if bill_id is not None:
                    try:
                        # Create the connection and cursor object
                        conn = dbfunc.getConnection()
                        if conn is not None and conn.is_connected():
                            dbcursor = conn.cursor()

                            # Get the current date and time
                            date_time_created = datetime.datetime.now()
                            # Have to convert to a string and format it to MySQL's datetime format
                            date_time_created_str = date_time_created.strftime('%Y-%m-%d %H:%M:%S')

                            # stores item name, its quantity and price. If the stock is 0 (the menu item can't be ordered anymore duh..) it'll store the extra items ordered here so that they can be refunded
                            items_out_of_stock = {}
                            for details in session['menu_items']:
                                # Extracting details from the dictionary
                                name = details.get('name', '')
                                quantity = int(details.get('quantity', 0))
                                price = float(details.get('item_price', 0.0))
                                description = "" #had to default as costomers cant make notes on orders

                                # Check stock availability
                                dbcursor.execute("SELECT inventory_item_stock FROM inventory WHERE restaurant_id = %s AND inventory_item_name = %s",
                                                (session['resturantid'], name))
                                current_stock = dbcursor.fetchone()

                                if current_stock:
                                    current_stock = current_stock[0]

                                    # Deduct the maximum possible quantity from the inventory (quantity_to_deduct can go lower than 0)
                                    quantity_to_deduct = min(quantity, current_stock)

                                    # Update the inventory with the new stock quantity
                                    new_stock = current_stock - quantity_to_deduct
                                    dbcursor.execute("UPDATE inventory SET inventory_item_stock = %s WHERE restaurant_id = %s AND inventory_item_name = %s",
                                                    (new_stock, session['resturantid'], name))

                                    # some W print messages here
                                    print(f"Deducted {quantity_to_deduct} units of {name} from stock.")

                                    # Insert into the orders table with the deducted quantity
                                    dbcursor.execute("INSERT INTO orders (restaurant_id, bill_id, customer_email,order_table_num, order_status, order_menu_item, order_menu_item_qty, order_author, order_time_created, order_price, order_menu_item_desc) \
                                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                                    (session['resturantid'], bill_id, session['email'],table_num, orderfunctions.ORDER_STATUS[0], name, quantity_to_deduct, "Customer Order", date_time_created_str, price, description))

                                    # Check if there is remaining quantity (this is what will be refunded cause theres no more menu items)
                                    remaining_quantity = quantity - quantity_to_deduct
                                    if remaining_quantity > 0:
                                        # Append the item individually to items_out_of_stock
                                        items_out_of_stock[name] = {
                                            'quantity': remaining_quantity,
                                            'price': price,
                                            'description': description
                                        }

                                else:
                                    # Item is out of stock
                                    items_out_of_stock[name] = {
                                        'quantity': quantity,
                                        'price': price,
                                        'description': description
                                    }

                                    # Log a message (you can customize this based on your needs)
                                    print(f"Inventory item {name} not found or insufficient stock. Refunding {quantity} items.")


                            # Update the bill with the updated price, to account for the refund
                            remaining_price = sum(item['quantity'] * item['price'] for item in items_out_of_stock.values())
                            if discount_applied > 0:
                                discount_amount = remaining_price * discount_applied
                                remaining_price -= discount_amount
                            billUpdatePrice = round((ordertotal - remaining_price), 2)
                            dbcursor.execute("UPDATE bill SET bill_sub_total = %s WHERE bill_id = %s",
                                            (billUpdatePrice, bill_id))


                            conn.commit()
                            dbcursor.close()
                            conn.close()
                            
                            if items_out_of_stock:
                                # Handle remaining quantity as needed
                                # You can customize this part based on your requirements
                                print("Items out of stock:", items_out_of_stock)

                            print("Order created")
                            session['menu_items'] = []
                            session['menuitemslength'] = 0
                            #redirects to the confirmed order page
                            return render_template('userOrderConfirm.html', isLoggedIn=session['isLoggedIn'], menuitemslength=session['menuitemslength'], ordertotal=billUpdatePrice, outOfStockItems=items_out_of_stock)
                        
                    except mysql.connector.Error as err:
                        print(f"Error: {err}")
                        print('DB Error')

            except ValueError:
                # Letting staff know about erroneous value
                print('Table value selected has no number')
        else:
            return redirect(url_for('orders'))
    else:
        return render_template('userOrder.html',tablenumbers=tablenumbers, ordertotal=ordertotal, menuitems=session['menu_items'],menuitemslength=session['menuitemslength'], isLoggedIn=session['isLoggedIn'])

#as it says it removes an item that has been slected from the cart
@app.route('/remove_item', methods=['POST'])
@login_required
def remove_item():
    item_id = request.json['id']
    filtered_data = [item for item in session['menu_items'] if int(item['id']) != item_id]
    session['menu_items'] = filtered_data
    # Remove the item with the specified ID from the array or perform any other necessary actions
    # Return a response to the client if needed
    return 'Item removed successfully'


""" Reservations Systems """

@app.route('/reservations', methods=['GET', 'POST'])
@login_required
def reservationspage():
    restaurantNames = orderfunctions.getRestaurantNames() #gets all the resturants for the reservation to choose from
    
    #generates all times
    times = []
    for hour in range(10, 22):
        for minute in range(0, 60, 60):
            formatted_hour = f'0{hour}' if hour < 10 else str(hour)
            formatted_minute = f'0{minute}' if minute < 10 else str(minute)
            times.append(f'{formatted_hour}:{formatted_minute}')
    
    #this form checks to see what tables are not booked in the timeslot and redirects them so they can choose what table 
    if request.method == "POST":
        print("Reservation checking for available tables")
        Restaurant = ast.literal_eval(request.form['Restaurant'])
        Restaurantid = Restaurant[1]
        name = request.form['firstName'] +  " " + request.form['lastName']
        Email = request.form['Email']           
        Phonenum = request.form['Phonenum']   
        date = request.form['date']  
        time_str = request.form['time']
        time = datetime.datetime.strptime(time_str, "%H:%M").time()
        numpeople = request.form['numpeople']
        
        #checking to make sure were not booking in the past
        combined_datetime = datetime.datetime.combine(datetime.datetime.strptime(date, '%Y-%m-%d').date(), datetime.datetime.strptime(time_str, "%H:%M").time())
        if combined_datetime >= datetime.datetime.now():

            #compileing all the form data so it can be used after table has been selected
            session['reservationdata'] = {"name": name, "email": Email, "phonenum": Phonenum, "numpeople": numpeople, "date": date, "time": time_str, "restaurant": Restaurantid, "restaurantname": Restaurant[0]}
            conn = dbfunc.getConnection()           
            if conn != None:    #Checking if connection is None           
                if conn.is_connected(): #Checking if connection is established
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()    #Creating cursor object
                    
                    #grabbing all booked table ids for that time slot          
                    dbcursor.execute('SELECT table_id FROM reservation WHERE restaurant_id = %s AND reservation_date = %s AND reservation_time = %s;', (Restaurantid, date, time,))     #Executing
                    tableids = dbcursor.fetchall()
                    
                    #getting all tables that the resturant has so it can be check what tables are free
                    dbcursor.execute('SELECT table_number, table_capacity, table_id FROM tables WHERE restaurant_id = %s;', (Restaurantid,))
                    alltables = dbcursor.fetchall()
                    
                    # Extract booked table IDs into a set for faster lookup
                    booked_table_ids = set(table_id for table_id, in tableids)

                    # Initialize a list to store available table information
                    available_tables = []

                    # Iterate through all tables to check availability
                    for table_number, table_capacity, table_id in alltables:
                        # Check if the table is not already booked and has enough capacity
                        if table_id not in booked_table_ids and table_capacity >= int(numpeople):
                            available_tables.append((table_number, table_capacity, table_id))

                    print("Available Tables:", available_tables)
                    dbcursor.close()
                    conn.close()
                    gc.collect() 
                    print(session['reservationdata'])
                    return render_template('userReservationsTables.html', available_tables=available_tables, menuitemslength=session['menuitemslength'], isLoggedIn=session['isLoggedIn'])
        else:
            #need to display an error here saying "the date or time your trying to book has passed"
            return render_template('userReservations.html', times=times,menuitemslength=session['menuitemslength'], Restaurants=restaurantNames, isLoggedIn=session['isLoggedIn'],)
    else:
        return render_template('userReservations.html', times=times,menuitemslength=session['menuitemslength'], Restaurants=restaurantNames, isLoggedIn=session['isLoggedIn'],)

#this is just the confirm after the table is chosen and then inserts into reservations
@app.route('/confirmbooking', methods=['GET', 'POST'])
@login_required
def confirmBooking():
    if request.method == "POST":
        table = ast.literal_eval(request.form['table'])
        print(table)
        conn = dbfunc.getConnection()           
        if conn != None:    #Checking if connection is None           
            if conn.is_connected(): #Checking if connection is established
                print('MySQL Connection is established')                          
                dbcursor = conn.cursor()    #Creating cursor object          
                dbcursor.execute("INSERT INTO reservation (restaurant_id, reservation_customer_name, reservation_customer_email, reservation_customer_phone, \
                                        table_id, reservation_party_size, reservation_author, reservation_creation_time, reservation_date,\
                                            reservation_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (session['reservationdata']['restaurant'], session['reservationdata']['name'], session['reservationdata']['email'], session['reservationdata']['phonenum'], table[2],
                                                                                                        session['reservationdata']['numpeople'], "Costomer Reservation",datetime.datetime.now(), session['reservationdata']['date'], datetime.datetime.strptime(session['reservationdata']['time'], "%H:%M").time())) 
                conn.commit()
                dbcursor.close()
                conn.close()
                gc.collect() 
                print("Reservation created sucsessfully")
                return render_template('userReservationsConfirm.html', reservationdata=session['reservationdata'], tablenum=table[0], menuitemslength=session['menuitemslength'],isLoggedIn=session['isLoggedIn'])
    else:
        return redirect(url_for('home'))



#idk where this came from it may be oscar but it may also be some acsidentially included code
@app.route('/error', methods=['GET', 'POST'])
def error():
    return render_template('errorPage.html')


""" Account Views mainly to see things like orders and reservations """

@app.route('/account')
@login_required  # Add this decorator to exempt the account route from login check
def account():
    return render_template("userAccount.html", username=session['username'], email=session.get('email'))

#this will get all the times created and subtotals for orders and the send them to the page
@app.route('/accountorders')
@login_required
def accountOrders():
    #get all the bill ids for the orders
    userOrders = []
    conn = dbfunc.getConnection()           
    if conn != None:    #Checking if connection is None           
        if conn.is_connected(): #Checking if connection is established
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object          
            dbcursor.execute('SELECT bill_id, order_time_created FROM orders WHERE customer_email = %s ORDER BY order_time_created DESC;', (session['email'],))    #Executing
            billiIdOrders = dbcursor.fetchall()
            unique_bill_ids = set()  # Set to store unique bill IDs
            compiled_bill = []   # List to store compiled bill IDs

            #when the orders come in there are multiple per bill as its made per menu item
            #so we need to get rid of any repeats of bill id's
            for bill_id, time in billiIdOrders:
                if bill_id not in unique_bill_ids:
                    unique_bill_ids.add(bill_id)
                    compiled_bill.append([bill_id, time.date()]) #all times should be the same for the bill id
            
            print(compiled_bill)
            #this gets the subtotal for each bill to compile with the time
            for billid in compiled_bill:   
                print(billid)
                dbcursor.execute('SELECT bill_sub_total FROM bill WHERE bill_id = %s;', (billid[0],))
                billTotal = dbcursor.fetchone()
                userOrders.append([billTotal[0], billid[1]])
                
            #now we have a collection of dates of orders and the ammount spent
            print(userOrders)
            dbcursor.close()
            conn.close()
            gc.collect()  
    return render_template('userAccountOrder.html', orders=userOrders, isLoggedIn=session['isLoggedIn'])

#this gets all the reservations made by the user and all returns all relevent data
@app.route('/accountreservations')
@login_required
def accountReservations():
    #get all the bill ids for the orders
    userReservations = []
    conn = dbfunc.getConnection()           
    if conn != None:    #Checking if connection is None           
        if conn.is_connected(): #Checking if connection is established
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    #Creating cursor object          
            dbcursor.execute('SELECT reservation_customer_name, reservation_date, reservation_time, table_id, restaurant_id FROM reservation WHERE reservation_customer_email = %s ORDER BY reservation_date ASC;', (session['email'],))    #Executing
            reservationList = dbcursor.fetchall()
            
            
            print(reservationList)
            #this code converts the ids to valid table numbers and restaurant names
            for reservation in reservationList:   
                print(reservation)
                dbcursor.execute('SELECT table_number FROM tables WHERE table_id = %s;', (reservation[3],))
                tableNumber = dbcursor.fetchone()
                dbcursor.execute('SELECT restaurant_name FROM restaurant WHERE restaurant_id = %s;', (reservation[4],))
                restaurantName = dbcursor.fetchone()
                if(reservation[1] >= datetime.date.today()): #check to make sure were not showing reservations that have already happened
                    userReservations.append({"name": reservation[0], "date": reservation[1], "time": reservation[2], "table": tableNumber[0], "location": restaurantName[0]})
                
            print(userReservations)
            dbcursor.close()
            conn.close()
            gc.collect()  
    return render_template('userAccountReservations.html', Reservations=userReservations, isLoggedIn=session['isLoggedIn'])

@app.route('/resetpassword', methods=["GET","POST"])
@login_required
def resetpassword():
    form={}
    error = ''
    try:	
        if request.method == "POST":    
            oldpass = request.form['oldpassword']        
            password = request.form['password']  
            confirmpass = request.form['confirmpassword']    
            print('Password change start 1.1')
            if session['email'] != None and password != None and confirmpass != None:  #check if em or pw is none    
                if password != confirmpass:
                    error = "Passwords do not match"
                    return render_template("userResetPassword.html", error = error, isLoggedIn=session['isLoggedIn'])
                else:
                    conn = dbfunc.getConnection() 
                    if conn != None:    #Checking if connection is None                    
                        if conn.is_connected(): #Checking if connection is established                        
                            print('MySQL Connection is established')                          
                            dbcursor = conn.cursor()    #Creating cursor object 
                            dbcursor.execute("SELECT customer_password FROM customer WHERE customer_email = %s;", (session['email'],))
                            data = dbcursor.fetchone()
                            if data:
                                if sha256_crypt.verify(oldpass, data[0]):                                                                        
                                    #data = dbcursor.fetchone()[0] #extracting password   
                                    # verify passowrd hash and password received from user                                                             
                                    password = sha256_crypt.hash((str(password)))
                                    dbcursor.execute("UPDATE customer SET customer_password = %s WHERE customer_email = %s;", (password,session['email'],)) 
                                    conn.commit()
                                    dbcursor.close()
                                    conn.close()                                
                                    return redirect(url_for('account'))
                                
                        dbcursor.close()
                        conn.close()                                                                   
                        gc.collect()
                        print('login start 1.10')
                        return render_template("userResetPassword.html", error=error, isLoggedIn=session['isLoggedIn'])
                    
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("userResetPassword.html",error = error, isLoggedIn=session['isLoggedIn'])   
    
    return render_template("userResetPassword.html", error = error, isLoggedIn=session['isLoggedIn'])
 
@app.route("/logout")
@login_required
def logout():    
    session.clear() #clears session variables
    print("You have been logged out!")
    gc.collect()
    return redirect(url_for('sessionsVarriables'))


app.run(debug=True)
