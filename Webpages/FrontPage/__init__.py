from flask import Flask, Blueprint, render_template
from pymongo import MongoClient
from flask_login import LoginManager, UserMixin 

app = Flask(__name__, template_folder='templates', static_folder='css')