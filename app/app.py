import sqlite3
from flask import render_template,request,flash,redirect,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,logout_user,current_user, UserMixin, LoginManager
from flask import Flask


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '1036359838298206420470379712328124'
db = 'tracker.db'



class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash


@login_manager.user_loader
def load_user(user_id):
    # Query your database to get the User by ID
    user_data = query_db(db, "SELECT * FROM users WHERE id = ?", user_id)

    if not user_data:
        return None

    user = User(user_data[0]['id'], user_data[0]['username'], user_data[0]['hash'])
    return user

def query_db(db,query, *args):
    try:
        con = sqlite3.connect(db)
        cur = con.cursor()
        if args:
            cur.execute(query,args)
        else:
            cur.execute(query)
        #fetch tuple of results
        rows = cur.fetchall()
        #get cols name from description
        cols = [c[0] for c in cur.description]
        #iterate through each tuple trnasformin into a dictionary
        res = []
        for row in rows:
            res.append({c:row[i] for i, c in enumerate(cols)})
        cur.close()
        con.close()
        return res
    except Exception as e:
        print("An error occurred when getting data to db: ",e)

def insert_db(db, query, *args):
    try:
        con = sqlite3.connect(db)
        cur = con.cursor()
        if args:
            cur.execute(query, args)
        else:
            cur.execute(query)
        con.commit()
        cur.close()
        con.close()
        return 0
    except Exception as e:
        print("An error occurred when inserting data into the database: ", e)
        return -1  # Return a code indicating an error

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
                flash("Wrong email or password",category='error')
        else:
            flash("Email is not registred",category="error")
    return render_template("login.html", user= current_user)


@app.route("/logout")
@login_required
def logout():
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
            hash = generate_password_hash(pw1,"scrypt")
            insert_db(db,"INSERT INTO users (username, hash) VALUES (?, ?)", username,hash)

            user = query_db(db,"SELECT * FROM users WHERE username = ?",username)
            user = User(id=user[0]['id'], username=user[0]['username'], password_hash=user[0]['hash'])
            user_id = User.get_id()
            #add default expense category
            query = (f"""INSERT INTO user_categories (user_id, category_id) VALUES
                            ({user_id}, 1), -- Paycheck
                            ({user_id}, 2), -- Bonus
                            ({user_id}, 3), -- Grocery
                            ({user_id}, 4), -- Fun
                            ({user_id}, 5), -- Bills
                            ({user_id}, 6); -- Taxes""")
            insert_db()
            flash("Account created", category='success')
            login_user(user, remember=True)
            return redirect(url_for("home"))
    return render_template("signup.html",user=current_user)


@app.route('/',methods=["GET","POST"])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    list_category = ["Paycheck","Grocery","Health","Clothing","Bills","Fun"]
    user_id =current_user.id
    category = query_db(db,"SELECT category FROM categories AS cat INNER JOIN user_categories AS uca on uca.category_id = cat.id WHERE uca.user_id = ?;",user_id)
    #get this list from the SQL table, initialize it with just 1 value then let user add what they want
    if request.method=="POST":
        if "submit_expense" in request.form:
            amount = request.form.get("expense")
            category_exp = request.form.get("category_exp")
            date = request.form.get("dateInsertion")
            try:
                amount = float(amount)
            except:
                flash("Insert a number",category="error")
            flash("Transaction inserted", category="success")
        elif "submit_category" in request.form:
            custom_category= request.form.get("category_add")
            if custom_category=="":
                flash("Insert custom category","error")
            else:
                insert_db(db,"INSERT INTO categories (category) VALUES (?);",custom_category)
                cat_id = query_db(db,"SELECT id FROM categories WHERE category = ?",custom_category)[0].get('id')
                insert_db(db, "INSERT INTO user_categories (user_id, category_id) VALUES (?,?);", user_id, cat_id)
                flash("Custom category inserted","success")

    return render_template('home.html',options=[i.get('category') for i in category],user=current_user)

@app.route("/summary",methods=["GET"])
def summary():
    #code to make the query and group by to display a table in html
    return render_template("summary.html",user=current_user)

if __name__ == '__main__':
    app.run(debug=True)