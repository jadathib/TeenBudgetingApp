from flask import Flask, render_template,request, redirect, flash
from cs50 import SQL
from models import db, User, Transactions
from sqlalchemy import exc, desc
from milestones import *
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import shutil 

app = Flask(__name__)
# shutil.copyfile('userbalances.db', '/tmp/userbalances.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userbalances.db'
app.secret_key = b'\x1bt!"e\xf7)Q5\xebz"f\xfa\xe6K'

# Initialization of login manager
login_manager = LoginManager()
login_manager.init_app(app)
# Initialization of database
db.init_app(app)

@app.before_first_request
def initialize_user_database():
# with app.app_context():
    # db.create_all()
    try:
        db.create_all()
        user1 = User(username='test', checkingBalance=1.00, savingBalance=0.00)
        if not bool(User.query.filter_by(username='test').first()):
            db.session.add(user1)
            User.query.get("test").checkingBalance = 4.00
            db.session.commit()
    except exc.IntegrityError as e:
        errorInfo = e.orig.args
        print(errorInfo)



@app.before_first_request
def initialize_transactions_database():
# with app.app_context():
    # db.create_all()
    try:
        db.create_all()
        transaction1 = Transactions(username='test', date='1/31/2021', purpose='deposit', amount=10.00, savingPercent=0.0)
        transaction2 = Transactions(username='test', date='2/10/2021', purpose='deposit', amount=10.00, savingPercent=0.0)
        if not bool(Transactions.query.filter_by(username='test').first()):
            db.session.add(transaction1)
            db.session.add(transaction2)
            #print(Transactions.query.filter_by(username='test').all())
            db.session.commit()
    except exc.IntegrityError as e:
        errorInfo = e.orig.args
        print(errorInfo)

# Database schema is as shown
'''
    Table Name: transactions
    Columns: amount     date        type        savingPercent
    Datatype: Real   Integer     Integer        Real
    Explanation:
        Amount is stored as a real (floating point) number
        Date is stored as an integer representing the date & time in unix time (easier to convert it to local time if stored as unix epoch or utc?)
        Type is stored as an integer of 0 or 1 to represent boolean values (sqlite doesn't have native boolean data type) 0 means deposit & 1 means withdrawal
        savingPercent is stored as a real (floating point) number that should be between 0.1 & 1 (check this in logic)
'''


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/checking', methods=["GET", "Post"])
@login_required
def checking():
    if request.method=="GET":
        checkBalance = current_user.checkingBalance
        return render_template('checking.html',checkBalance=checkBalance)
    else:
        return redirect('/')

@app.route('/savings', methods=["GET","POST"])
@login_required
def savings():
    if request.method == "GET":
        try:
            firstSavingsDate = Transactions.query.filter_by(username=current_user.username).order_by(Transactions.date.desc()).all()[0]
            lastSavingsDate = Transactions.query.filter_by(username=current_user.username).order_by(Transactions.date.desc()).all()[-1]
        except IndexError:
            firstSavingsDate = "None"
            lastSavingsDate = "None"
        savingsBalance = current_user.savingBalance
        # Milestones: First day of savings, $50, $100, $200
        milestones = getMilestones(current_user.username)
        return render_template('savings.html',firstSavingsDate=firstSavingsDate, savingBalance=savingsBalance, lastSavingsDate=lastSavingsDate, milestones=milestones)
    else:
        return redirect('/')

@app.route('/transactions', methods=["GET","POST"])
@login_required
def transactions():
    name = current_user.username
    transactionsToDisplay = Transactions.query.filter_by(username=name).order_by(Transactions.date.desc()).all()
    return render_template('transactions.html', transactionHistory=transactionsToDisplay)


@app.route('/deposits', methods=["GET","POST"])
@login_required
def modifyDeposits():
    if request.method == "POST":
        depositAmount = float(request.form.get('amount'))
        transactionDate = request.form.get('date')
        percentToSavings = float(request.form.get('savingPercent'))
        newTransaction = Transactions(username=current_user.username, date=transactionDate, purpose='deposit', 
            amount=depositAmount, savingPercent=percentToSavings)
        temp = float(percentToSavings / 100)
        temp2 = depositAmount - (depositAmount * temp)
        current_user.checkingBalance = current_user.checkingBalance + temp2
        current_user.savingBalance = current_user.savingBalance + depositAmount * temp
        db.session.add(newTransaction)
        db.session.commit()
        return render_template('deposits.html', statusMessage='Deposit Successful')
    else:
        return render_template('deposits.html')

@app.route('/expenses', methods=["GET","POST"])
@login_required
def modifyExpenses():
    if request.method == "POST":
        amountToDeduct = float(request.form.get('amount'))
        date = request.form.get('date')
        category = request.form.get('categories')

        newTransaction = Transactions(username=current_user.username, date=date, purpose='withdrawal', amount=amountToDeduct,
        category=category)
        
        currentUser = current_user
        currentUser.checkingBalance = currentUser.checkingBalance - amountToDeduct
        db.session.add(newTransaction)
        db.session.commit()
        return render_template('expenses.html', statusMessage='Expense Recorded')
    else:
        return render_template('expenses.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    user = User.query.filter_by(username=request.form.get('username')).first()
    if request.method == 'POST':
        if user:
            login_user(user)
            flash('Logged in successfully!')
            return redirect('/')
        else:
            return render_template('login.html', status='NOT FOUND!')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    newname = request.form.get('username')
    if request.method == 'POST':
        if not User.query.get(newname): # Not an existing user
            user = User(username=newname)
            login_user(user)
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        else:
            return render_template('register.html', status="Already exists!")
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)