from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def frontpage():
    return render_template('userFrontPage.html')

@app.route('/account', methods=['GET', 'POST'])
def accountpage():
    return render_template('userAccount.html')


@app.route('/orders', methods=['GET', 'POST'])
def orderspage():
    return render_template('userAccount.html')


@app.route('/reservations', methods=['GET', 'POST'])
def reservationspage():
    return render_template('userAccount.html')


@app.route('/privicy-policy', methods=['GET', 'POST'])
def privicypolpage():
    return render_template('userAccount.html')

#page list: front page, account, login, sign up, reset password, orders, reservations, privacy policy




app.run(debug=True)