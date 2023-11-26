import datetime
import os
from flask import Flask,render_template,request,flash,redirect,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,logout_user,current_user, LoginManager
from helpers import query_db, insert_db, create_summary_figures, User, create_csv_file, create_history_figure

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
#app configuration
app.config['SECRET_KEY'] = '1036359838298206420470379712328124'
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 3}
db = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tracker.db')

@login_manager.user_loader
def load_user(user_id):
    # Query your database to get the User by ID
    user_data = query_db(db, "SELECT * FROM users WHERE id = ?", user_id)
    if not user_data:
        return None
    user = User(user_data[0]['id'], user_data[0]['username'], user_data[0]['hash'])
    return user

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        #insert logic to check for login
        user = query_db(db,"SELECT * FROM users WHERE username = ?",username)
        if len(user) == 1:
            user = User(id=user[0]['id'], username=user[0]['username'], password_hash=user[0]['hash'])
            if check_password_hash(user.password_hash,password):
                flash("Logged in succesfully!",category='success')
                login_user(user,remember=True)
                return redirect("/")
            else:
                flash("Wrong username or password",category='error')
        else:
            flash("Username is not registred",category="error")
    return render_template("login.html", user= current_user)

@app.route("/logout")
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    logout_user()
    flash("logged out succesfully",category="success")
    return redirect("/")

@app.route("/sign-up",methods=['POST','GET'])
def sing_up():
    if request.method =='POST':
        username = request.form.get('username')
        pw1 = request.form.get('password')
        pw2 = request.form.get('passwordR')
        if len(query_db(db,"SELECT * FROM users WHERE username = ?",username)) != 0:
            flash("Username is already registred",category='error')
        elif pw1 != pw2:
            flash("The confirmation passowrd is different to the password inserted.", category='error')
        elif not (any(c.isupper() for c in pw1) and
                 any(c.isdigit() for c in pw1) and
                 any(c in '!@#$%^&*()_-+={}[]|\:;"<>,.?/' for c in pw1) and
                 len(pw1) >= 8):
            flash(
                "Password must contain at least 1 uppercase letter, 1 digit, 1 special character, and be at least 8 characters long.",
                category='error')
        else:
            hash = generate_password_hash(pw1)
            insert_db(db,"INSERT INTO users (username, hash) VALUES (?, ?)", username,hash)

            user = query_db(db,"SELECT * FROM users WHERE username = ?",username)
            user_id = user[0]['id']
            user = User(id=user[0]['id'], username=user[0]['username'], password_hash=user[0]['hash'])

            #add default expense category
            query = (f"""INSERT INTO user_categories (user_id, category_id) VALUES
                            ({user_id}, 1), -- Paycheck
                            ({user_id}, 2), -- Bonus
                            ({user_id}, 3), -- Grocery
                            ({user_id}, 4), -- Fun
                            ({user_id}, 5), -- Bills
                            ({user_id}, 6); -- Taxes""")
            insert_db(db,query)
            flash("Account created", category='success')
            login_user(user, remember=True)
            return redirect(url_for("home"))
    return render_template("signup.html",user=current_user)

@app.route('/',methods=["GET","POST"])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    user_id = current_user.id
    category = query_db(db,"SELECT category FROM categories AS cat INNER JOIN user_categories AS uca on uca.category_id = cat.id WHERE uca.user_id = ?;",user_id)
    #get this list from the SQL table, initialize it with just 1 value then let user add what they want
    if request.method=="POST":
        if "submit_expense" in request.form:
            amount = request.form.get("expense")
            category_exp = request.form.get("category_exp")
            date = request.form.get("dateInsertion")
            if date == "":
                date = datetime.date.today().strftime("%Y-%m-%d")
            try:
                amount = float(amount)
            except:
                flash("Insert a number",category="error")
            try:
                insert_db(db,"INSERT INTO transactions (user_id,category,amount,time_inserted) VALUES (?,?,?,?)",user_id,category_exp,amount,date)
                flash("Transaction inserted", category="success")
            except:
                flash("Error occurred when inserting data",category="error")
            return redirect(url_for("home"))
        if "download-data" in request.form:
            query = """
                    SELECT amount, category, time_inserted
                    FROM transactions
                    WHERE user_id = ?;
                    """
            res = query_db(db,query,user_id)
            return create_csv_file(res)
    wealth = create_history_figure(user_id,year = datetime.date.today().year,db=db)
    return render_template('home.html',options=[i.get('category').capitalize() for i in category[::-1]],user=current_user, month_sum = wealth)

@app.route('/categories',methods=["GET","POST"])
def categories():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    user_id = current_user.id
    category = query_db(db,"SELECT category FROM categories AS cat INNER JOIN user_categories AS uca on uca.category_id = cat.id WHERE uca.user_id = ?;",user_id)
    if request.method=="POST":
        if "submit_category" in request.form:
            custom_category= request.form.get("category_add").upper()
            is_wealth = 0 if request.form.get("is-wealth") is None else 1
            #check for blank input
            if custom_category=="":
                flash("Insert custom category","error")
            #check if the category was already introduced by the user
            elif custom_category in [i['category'].upper() for i in category]:
                flash("Category already exist", "error")
            else:
                #check if the category already exist
                num = query_db(db, """SELECT COUNT(category_id) as num FROM user_categories WHERE category_id = (
                                    SELECT id FROM categories WHERE category COLLATE NOCASE = ?
                                );""", custom_category)[0]['num']
                #insert only if it is not present
                if num == 0:
                    insert_db(db,"INSERT INTO categories (category, is_wealth) VALUES (?,?);",custom_category, is_wealth)
                #insert into many to many table
                cat_id = query_db(db,"SELECT id FROM categories WHERE category COLLATE NOCASE = ?",custom_category)[0].get('id')
                insert_db(db, "INSERT INTO user_categories (user_id, category_id) VALUES (?,?);", user_id, cat_id)

                flash("Custom category inserted","success")
                return redirect(url_for("categories"))

        if "remove_cat" in request.form:
            to_remove = request.form.get("remove_cat").upper()
            #check if the categories is used by just one user
            num = query_db(db,"""SELECT COUNT(category_id) as num FROM user_categories WHERE category_id = (
                    SELECT id FROM categories WHERE category = ?
                );""",to_remove)[0]['num']
            if num != 1:
                query = """
                    DELETE FROM user_categories 
                    WHERE user_id = ? AND category_id = (
                        SELECT id FROM categories WHERE category = ?
                    );
                """
                insert_db(db,query,user_id,to_remove)
                flash("Category removed", "success")
            elif num == 1:

                query = """
                            DELETE FROM user_categories 
                                    WHERE user_id = ? and category_id = (
                                        SELECT id FROM categories WHERE category COLLATE NOCASE = ?
                                    );
                                """
                insert_db(db, query, user_id, to_remove)
                query = """
                        DELETE FROM categories
                        WHERE category COLLATE NOCASE = ?
                """
                insert_db(db, query, to_remove)
                flash("Category removed", "success")
            return redirect("categories")


    return render_template('categories.html',list_category = [i.get('category').lower().capitalize() for i in category] ,user=current_user)


@app.route("/summary",methods=["GET","POST"])
def summary():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if request.method == 'POST':
        user_id = current_user.id
        query = """
        SELECT category,strftime('%m', time_inserted) as month, SUM(amount) AS tot , strftime('%Y', time_inserted) as year
        FROM transactions 
        WHERE user_id = ?
        GROUP BY category, month
        HAVING month = ? AND year = ?
        ORDER BY tot DESC;
        """
        month = request.form.get("month")
        year = request.form.get("year")
        data = query_db(db,query,user_id,month,year)
        if not data:
            flash("No data to display", category="error")
            return redirect("/summary")
        categories = [row['category'] for row in data]
        amounts = [row['tot'] for row in data]
        fig, fig_mon = create_summary_figures(data, user_id, month, year,db=db)

        return render_template("summary.html", user=current_user, result_rows=data, categories=categories,
                               amounts=amounts,json_char = fig, month_sum = fig_mon)

    user_id = current_user.id
    #query for the specific month
    query = """
            SELECT category,strftime('%m', time_inserted) as month, SUM(amount) AS tot , strftime('%Y', time_inserted) as year
                FROM transactions 
                WHERE user_id = ?
                GROUP BY category, month
                HAVING month = ? AND year = ?
                ORDER BY tot DESC;
            """
    month = datetime.date.today().strftime("%m")
    year = datetime.date.today().strftime("%Y")
    data = query_db(db, query, user_id, month, year)
    fig, fig_mon = create_summary_figures(data, user_id,month,year,db)
    return render_template("summary.html", user=current_user, result_rows=data, json_char = fig, month_sum = fig_mon)


if __name__ == '__main__':
    db = "tracker.db"
    app.run(debug=True)