from flask import Flask, Blueprint, render_template, session, request, flash, redirect, url_for, jsonify
import json

app = Flask(__name__)
app.secret_key = 'Horizon' 


@app.route('/', methods=['GET', 'POST'])
def frontpage():
    if not session.get('isLoggedIn'):
        session['isLoggedIn'] = False
    if not session.get('menu_items'):
        session['menu_items'] = []
    print(session['menu_items'])
    menuitemslength =  len(session['menu_items'])
    return render_template('userFrontPage.html', menuitems=session['menu_items'], menuitemslength=menuitemslength, isLoggedIn=session['isLoggedIn'])

@app.route('/account', methods=['GET', 'POST'])
def accountpage():
    return render_template('userAccount.html')


@app.route('/orders', methods=['GET', 'POST'])
def orderspage():
    return render_template('userOrder.html', menuitems=session['menu_items'],menuitemslength=menuitemslength, isLoggedIn=session['isLoggedIn'])

@app.route('/api/data', methods=['POST'])
def receive_data():
    data_string = request.data.decode('utf-8')
    # Convert the string to a Python object (list of dictionaries)
    session['menu_items'] = json.loads(data_string)
    # Process the data as needed
    print(session['menu_items'])
    menuitemslength =  len(session['menu_items'])
    return jsonify(menuitemslength)


@app.route('/reservations', methods=['GET', 'POST'])
def reservationspage():
    return render_template('userReservations.html')


@app.route('/privicy-policy', methods=['GET', 'POST'])
def privicypolpage():
    return render_template('userPriicyPage.html')

#page list: front page, account, login, sign up, reset password, orders, reservations, privacy policy

@app.route('/login', methods=['GET', 'POST'])
def loginpage():
    if request.method == "POST":  
        session['isLoggedIn'] = True
        return render_template('userFrontPage.html', isLoggedIn=session['isLoggedIn'])
    return render_template('userLogin.html')


@app.route('/register', methods=['GET', 'POST'])
def registerpage():
    if request.method == "POST":  
        session['isLoggedIn'] = True
        return render_template('userFrontPage.html', isLoggedIn=session['isLoggedIn'])
    return render_template('userRegister.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def resetpasswordpage():
    return render_template('userResetPass.html')


@app.route("/logout")
def logout():    
    session.clear() #clears session variables
    return redirect(url_for('frontpage'))

app.run(debug=True)