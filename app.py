from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/PF.db'  # Set the URI for your SQLite database
db = SQLAlchemy(app)

from personal_finance.routes.route import *


