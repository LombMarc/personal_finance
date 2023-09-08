from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


if not os.path.exists('db'):
    os.makedirs('db')

abs_path = os.path.abspath("db")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ abs_path + '/expense.db'  # Set the URI for your SQLite database
db = SQLAlchemy(app)

from personal_finance.models.model import *


from flask import render_template, request, redirect, url_for

# Route for the login page
@app.route('/', methods=['GET'])
def root():
    return render_template('login.html')

#rout to home page after login info
@app.route('/home',methods=['POST'])
def home():
    username = request.form['username']
    pw = request.form['key']
    if username=='Admin' and pw=='Admin':
        return render_template('home.html')

#route to manage categories page
@app.route('/manage_categories', methods=['GET'])
def manage_categories():
    return render_template('manage_categories.html')

#route to add expenses page
@app.route('/add_expense_income', methods=['GET', 'POST'])
def add_expense_income():
    return render_template('add_expense_income.html')

#route to display data page
@app.route('/display_data', methods=['GET'])
def display_data():
    return render_template('display_data.html')

# Route to add a new category
@app.route('/manage_categories', methods=['POST'])
def add_category():
    category_name = request.form['new_category']

    # Create a new CategoryAvailable instance
    new_category = CategoryAvailable(category=category_name)

    # Add the new category to the database
    db.session.add(new_category)
    db.session.commit()

    return redirect(url_for('home'))

'''




# Route to add an expense/income
@app.route('/add_expense_income', methods=['POST'])
def add_expense_income():
    amount = float(request.form['amount'])
    category = request.form['category']
    date = request.form['date']

    new_expense_income = ExpenseIncome(amount=amount, category=category, date=date)
    db.session.add(new_expense_income)
    db.session.commit()

    return "Expense/Income added successfully."
'''

if __name__=='__main__':
    app.run(debug=True)





