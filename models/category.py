from personal_finance.app import db

class CategoryAvailable(db.Model):
    id_category = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255),nullable=False)

    def __repr__(self):
        return f"<Category_available(id={self.id}, category={self.category})>"