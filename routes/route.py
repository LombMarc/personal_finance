from flask import render_template, request, redirect, url_for
from personal_finance.app import app, db
from personal_finance.models.expenseIncome import ExpenseIncome
from personal_finance.models.category import CategoryAvailable



# Route for the home page
@app.route('/', methods=['GET'])
def root():
    return render_template('login.html')

@app.route('/home',methods=['POST'])
def home():
    username = request.form['username']
    pw = request.form['key']
    if username=='Admin' and pw=='Admin':
        return render_template('home.html')


@app.route('/manage_categories', methods=['GET'])
def manage_categories():
    return render_template('manage_categories.html')


@app.route('/add_expense_income', methods=['GET', 'POST'])
def add_expense_income():
    return render_template('add_expense_income.html')

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


app.run(debug=True)


