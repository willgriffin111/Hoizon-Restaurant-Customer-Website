
from database import dbfunc
import mysql


ORDER_STATUS = ['PENDING', 'COMPLETED', 'CANCELLED']

def create_bill(sub_total, discount_applied):
        # Create the connection and cursor object
        try:
            # Create the connection and cursor object
            conn = dbfunc.getConnection()
            if conn is not None and conn.is_connected():
                dbcursor = conn.cursor()
                dbcursor.execute("INSERT INTO bill (bill_sub_total, bill_discount_applied) \
                                 VALUES (%s, %s)", (sub_total, discount_applied))
                conn.commit()

                # Get the last inserted bill_id
                dbcursor.execute("SELECT LAST_INSERT_ID()")
                bill_id = dbcursor.fetchone()[0]

                dbcursor.close()
                conn.close() 

                print(f"Bill created with ID: {bill_id}")
            return bill_id

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None