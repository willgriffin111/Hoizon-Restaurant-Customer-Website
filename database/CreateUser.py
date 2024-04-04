import mysql.connector, dbfunc
from mysql.connector import errorcode
from passlib.hash import sha256_crypt

  #connection to DB
# DB_NAME = 'horizon_resturant'    #DB Name
# DB_NAME = 'horizonResturant'    #DB Name  MISPELLED
DB_NAME = 'Horizon_Restaurant'
staffId = 3
restrantid = 1
staffName = 'Will'
staffType = 'FRONT'
staffPassword = sha256_crypt.hash('password')  #password goes in brackets default password

restId = 1
restloc = "MARS"
restname = 'its joe mamas restaurant'
restcap = 6



# Create restaurant
def create_restaurant(restId, restloc, restname, restcap):
    conn = dbfunc.getConnection() 
    if conn != None:    # Checking if connection is None
        if conn.is_connected(): # Checking if connection is established
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    # Creating cursor object
            dbcursor.execute('USE {};'.format(DB_NAME)) # Use database
            dbcursor.execute("INSERT INTO restaurant (restaurant_id, restaurant_location, restaurant_name, restaurant_capacity) VALUES (%s, %s, %s, %s)", (restId, restloc, restname, restcap))     
            conn.commit() 
            print("Restaurant created successfully")
            dbcursor.close()       
            conn.close() # Connection must be closed
        else:
            print('DB connection error')
    else:
        print('DBFunc error')

#Create USER
def create_user(staffId, restrantid, staffName, staffType, staffPassword):
    conn = dbfunc.getConnection() 
    if conn != None:    # Checking if connection is None
        if conn.is_connected(): # Checking if connection is established
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    # Creating cursor object
            dbcursor.execute('USE {};'.format(DB_NAME)) # Use database
            dbcursor.execute("INSERT INTO employee (employee_id, restaurant_id, employee_name, employee_account_type, employee_password) VALUES (%s, %s, %s, %s, %s)", (staffId, restrantid, staffName, staffType, staffPassword))     
            conn.commit() 
            print("User created successfully")
            dbcursor.close()       
            conn.close() # Connection must be closed
        else:
            print('DB connection error')
    else:
        print('DBFunc error')
    
# Create TABLE
def create_table(table_number, table_capacity, restaurant_id):
    conn = dbfunc.getConnection() 
    if conn != None:    # Checking if connection is None
        if conn.is_connected(): # Checking if connection is established
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    # Creating cursor object
            dbcursor.execute('USE {};'.format(DB_NAME)) # Use database
            dbcursor.execute("INSERT INTO tables (table_number, table_capacity, restaurant_id) VALUES (%s, %s, %s)", (table_number, table_capacity, restaurant_id))    
            conn.commit() 
            print("Table created successfully")
            dbcursor.close()       
            conn.close() # Connection must be closed
        else:
            print('DB connection error')
    else:
        print('DBFunc error')
        
#Create CUSTOMER
def create_customer(userEmail, firstName, lastName, phoneNumber, userPassword):
    conn = dbfunc.getConnection() 
    if conn != None:    # Checking if connection is None
        if conn.is_connected(): # Checking if connection is established
            print('MySQL Connection is established')                          
            dbcursor = conn.cursor()    # Creating cursor object
            dbcursor.execute('USE {};'.format(DB_NAME)) # Use database
            dbcursor.execute("INSERT INTO customer (customer_email, customer_first_name, customer_last_name, customer_password, customer_phone_details) VALUES (%s, %s, %s, %s, %s)", (userEmail, firstName, lastName, userPassword, phoneNumber))     
            conn.commit() 
            print("User created successfully")
            dbcursor.close()       
            conn.close() # Connection must be closed
        else:
            print('DB connection error')
    else:
        print('DBFunc error')
       
       
email = 'exsample@email.com'
firstname = "John"
lastname = "Doe"
phonenumber = "889788987"
create_customer(email, firstname, lastname, phonenumber, staffPassword)