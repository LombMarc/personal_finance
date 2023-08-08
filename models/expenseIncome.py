from personal_finance.app import db

class ExpenseIncome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(255),nullable=False)
    date = db.Column(db.DateTime,nullable=False)

    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, category={self.category}, date={self.date})>"