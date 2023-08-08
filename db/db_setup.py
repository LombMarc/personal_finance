from personal_finance.app import app, db
from personal_finance.models.expenseIncome import ExpenseIncome
from personal_finance.models.category import CategoryAvailable

#initialize database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == "__main__":
    init_db()
