from flask import Flask, Blueprint, render_template, session, request, flash, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'Horizon' 


@app.route('/', methods=['GET', 'POST'])
def frontpage():
    if not session.get('isLoggedIn'):
        session['isLoggedIn'] = False
    return render_template('userFrontPage.html', isLoggedIn=session['isLoggedIn'])

@app.route('/account', methods=['GET', 'POST'])
def accountpage():
    return render_template('userAccount.html')


@app.route('/orders', methods=['GET', 'POST'])
def orderspage():
    return render_template('userAccount.html')


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