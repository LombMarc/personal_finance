from personal_finance.app import db,app
from personal_finance.models.model import CategoryAvailable

#create db file
with app.app_context():
    db.create_all()

    #add default category
    for cat in ['Paycheck','Bonus','Grocery','Insurance','Transportation','Bills','Savings','Investment']:
        db.session.add(CategoryAvailable(category = cat))

    db.session.commit()
    print("initial commit for  category completed")
