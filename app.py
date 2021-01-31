from flask import Flask, render_template,request, redirect
from cs50 import SQL
from models import db, User, Transactions
from sqlalchemy import exc, desc


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userbalances.db'
# Initialization of database
db.init_app(app)

@app.before_first_request
def initialize_user_database():
# with app.app_context():
    # db.create_all()
    try:
        db.create_all()
        user1 = User(username='test', checkingBalance=1.00, savingBalance=0.00, savingPercent=0.00)
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
        transaction1 = Transactions(username='test', date='1/31/2021', purpose='deposit', amount=10.00)
        transaction2 = Transactions(username='test', date='2/10/2021', purpose='deposit', amount=10.00)
        if not bool(Transactions.query.filter_by(username='test').first()):
            db.session.add(transaction1)
            db.session.add(transaction2)
            Transactions.query.get("test").checkingBalance = 4.00
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
#No problem working well
def checking():
    if request.method=="GET":
        checkBalance = User.query.get('test').checkingBalance
        #return str(checkBalance)
        return render_template('checking.html',checkBalance=checkBalance)
    else:
        return redirect('/modifybalance')

@app.route('/savings', methods=["GET","POST"])
#Only showing either firstSavingsDat OR savingsBalance, does not show both
#How to show first savings date and last savings date?
def savings():
    if request.method == "GET":
        firstSavingsDate = Transactions.query.get('test').date
        lastSavingsDate = Transactions.query.order_by(Transactions.date.desc()).all()[-1]
        savingsBalance = User.query.get('test').savingBalance
        #return str(firstSavingsDate)
        #return str(savingsBalance)
        return render_template('savings.html',firstSavingsDate=firstSavingsDate, savingsBalance=savingsBalance)
    else:
        return redirect('/modifybalance')

@app.route('/transactions', methods=["GET","POST"])
#only showing one transaction
def transactions():
    if request.method == 'GET':
        transactionsToDisplay = Transactions.query.filter_by(username='test').all()
        return str(transactionToDisplay)
    else:
        return redirect('/modifybalance')

@app.route('/deposits', methods=["GET","POST"])
#Testing with HTML file needed, gives 404 when run
def modifyDeposits():
    if request.method == "POST":
        depositAmount = request.args.get('amount')
        date = request.args.get('depositDate')
        percentToSavings = request.args.get('percentToSave')
        return render_template('deposits.html')
    else:
        return redirect('index.html')

@app.route('/expenses', methods=["GET","POST"])
#Testing with HTML file needed, gives 404 when run
def modifyExpenses():
    if request.method == "POST":
        amountToDeduct = request.args.get('amountToDeduct')
        date = request.args.get('expenseDate')
        category = request.args.get('expenseCategory')
        return render_template('expenses.html')
    else:
        return redirect('index.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)