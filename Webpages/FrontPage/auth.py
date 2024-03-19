from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, LoginManager, UserMixin, login_required
from bson.objectid import ObjectId
from bson import json_util
import json


auth = Blueprint('auth', __name__)
login_manager = LoginManager(app)


# THIS CODE NEEDS UPDATING FOR DATABASE
@login_manager.user_loader
def load_user(user_id):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
        is_admin = user.get("is_admin", False)  # use `get` to retrieve the value or return False if the key doesn't exist
        return User(user["_id"], user["email"], user["name"], is_admin)

# THIS CODE NEEDS UPDATING
class User(UserMixin):
    def __init__(self, _id, email, name, username, is_admin):
        self.id = _id
        self.email = email
        self.name = name
        self.is_admin = is_admin
        self.username = username

    def is_authenticated(self):
        return True

    def is_submitted():
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('error.html'), 401


#JSON ENCODER
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)
app.json_encoder = MyEncoder


#HOME ROUTE
@auth.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

#CONTACT ROUTE
@auth.route("/account", methods=['GET', 'POST'])
def account():
    return render_template("account.html")

#DESTINATION ROUTE
@auth.route("/orders", methods=['GET', 'POST'])
def orders():
    return render_template("orders.html")

@auth.route("/reservations", methods=['GET', 'POST'])
def reservations():
    return render_template("reservations.html")

@auth.route("/privacy", methods=['GET', 'POST'])
def privacy():
    return render_template("privacy.html")


@auth.route("/reset", methods=['GET', 'POST'])
def reset():
    return render_template("reset.html")

@auth.route("/error", methods=['GET', 'POST'])
def error():
    return render_template("error.html")



# THIS CODE NEEDS UPDATING FOR DATABASE
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        error = None

        existing_user = user_collection.find_one({"email": email})
        if existing_user:
            error = 'Email already exists.'
            flash(error, 'danger')
            return redirect(url_for('auth.login'))
        
        elif email and len(email) < 4:
            error = 'Email must be greater than 3 characters.'
            flash(error, 'danger')
            return redirect(url_for('auth.login'))
        
        elif name and len(name) < 2:
            error = 'First name must be greater than 1 character.'
            flash(error, 'danger')
            return redirect(url_for('auth.login'))
            
        elif password != password2:
            error = 'Passwords do not match'
            flash(error, 'danger')
            return redirect(url_for('auth.login'))
        elif password and len(password) < 7:
            error = 'Password must be at least 7 characters.'
            flash(error, 'danger')
            return redirect(url_for('auth.login'))
        
        elif email and name and password:
            password = generate_password_hash(password)
            new_user = {"email": email, "name": name, "password": password}
            if email == "admin@horizontravel.com":
                new_user["is_admin"] = True
                admin_collection.insert_one(new_user)

            else:
                user_collection.insert_one(new_user)
            flash('You have successfully registered!', category='success')
            if new_user.get("is_admin"):
                login_user(User(new_user["_id"], new_user["email"], new_user["name"], is_admin=True), remember=True)
                return redirect(url_for('admin'))
            else:
                login_user(User(new_user["_id"], new_user["email"], new_user["name"], is_admin=False), remember=True)
                return redirect(url_for('booking.createBooking'))
        if error:
            flash(error, 'error')
            return redirect(url_for('auth.login'))
        return redirect(url_for('booking.createBooking'))
    return render_template("account.html", user=current_user)


# THIS CODE NEEDS UPDATING FOR DATABASE
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = user_collection.find_one({"email": email})
        if user and password and check_password_hash(user["password"], password):
            if user.get("is_admin"):
                login_user(User(user["_id"], user["email"], user["name"], user["is_admin"]), remember=True)
                return redirect(url_for('auth.admin'))
            else:
                flash('Logged in successfully!', category='success')
                login_user(User(user["_id"], user["email"], user["name"], is_admin=False), remember=True)
            return redirect(url_for('booking.createBooking'))
        else:
            error = 'Incorrect email or password, try again.'
            flash(error, 'danger')
            return redirect(url_for('auth.login'))
    return render_template("login.html", user=current_user)


#LOGOUT # THIS CODE NEEDS UPDATING FOR DATABASE
@auth.route('/logout')
def logout():
    logout_user()
    error = 'You have successfully logged out.'
    flash(error, 'danger')
    flash('You have successfully logged out.', category='success')
    return redirect(url_for('auth.home'))


@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('error.html'))
    return render_template('admin.html', user=current_user, bookings=bookings, sort_by=sort_by, sort_order=sort_order)

