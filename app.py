from flask import Flask, render_template,request, redirect, flash
from cs50 import SQL
from models import db, User, Transactions
from sqlalchemy import exc, desc
from milestones import *
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
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

with app.app_context():
    db.create_all()
    test = str(Transactions.query.filter_by(username='test').all())
    print(test)

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
    if current_user.is_active:
        return str(current_user)
    return render_template('index.html')


@app.route('/checking', methods=["GET", "Post"])
#No problem working well
def checking():
    if request.method=="GET":
        checkBalance = User.query.get('test').checkingBalance
        return render_template('checking.html',checkBalance=checkBalance)
    else:
        return redirect('/modifybalance')

@app.route('/savings', methods=["GET","POST"])
def savings():
    if request.method == "GET":
        # return str(Transactions.query.filter_by(username='test').all())
        firstSavingsDate = Transactions.query.order_by(Transactions.date.desc()).all()[0]
        lastSavingsDate = Transactions.query.order_by(Transactions.date.desc()).all()[-1]
        savingsBalance = User.query.get('test').savingBalance
        # Milestones: First day of savings, $50, $100, $200
        milestones = getMilestones(Transactions)
        return render_template('savings.html',firstSavingsDate=firstSavingsDate, savingBalance=savingsBalance, lastSavingsDate=lastSavingsDate, milestones=milestones)
    else:
        return redirect('/modifybalance')

@app.route('/transactions', methods=["GET","POST"])
def transactions():
    transactionsToDisplay = Transactions.query.filter_by(username='test').order_by(Transactions.date.desc()).all()
    return render_template('transactions.html', transactionHistory=transactionsToDisplay)


@app.route('/deposits', methods=["GET","POST"])
def modifyDeposits():
    if request.method == "POST":
        depositAmount = float(request.form.get('amount'))
        transactionDate = request.form.get('date')
        percentToSavings = float(request.form.get('savingPercent'))
        newTransaction = Transactions(username='test', date=transactionDate, purpose='deposit', 
            amount=depositAmount, savingPercent=percentToSavings)
        currentUser = User.query.get('test')
        temp = float(percentToSavings / 100)
        temp2 = depositAmount - (depositAmount * temp)
        currentUser.checkingBalance = currentUser.checkingBalance + temp2
        currentUser.savingBalance = currentUser.savingBalance + depositAmount * temp
        db.session.add(newTransaction)
        db.session.commit()
        return render_template('deposits.html', statusMessage='Deposit Successful')
    else:
        return render_template('deposits.html')

@app.route('/expenses', methods=["GET","POST"])
def modifyExpenses():
    if request.method == "POST":
        amountToDeduct = float(request.form.get('amount'))
        date = request.form.get('date')
        category = request.form.get('category')

        newTransaction = Transactions(username='test', date=date, purpose='withdrawal', amount=amountToDeduct,
        category=category)

        currentUser = User.query.get('test')
        currentUser.checkingBalance = currentUser.checkingBalance - amountToDeduct
        db.session.add(newTransaction)
        db.session.commit()
        return render_template('expenses.html', statusMessage='Expense Recorded')
    else:
        return render_template('expenses.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = User.query.filter_by(username='test').first()
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