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
#Only showing either firstSavingsDat OR savingsBalance, does not show both
#How to show first savings date and last savings date?
def savings():
    if request.method == "GET":
        # return str(Transactions.query.filter_by(username='test').all())
        firstSavingsDate = Transactions.query.order_by(Transactions.date.desc()).all()[0]
        lastSavingsDate = Transactions.query.order_by(Transactions.date.desc()).all()[-1]
        savingsBalance = User.query.get('test').savingBalance
        # return str(lastSavingsDate)
        # return str(savingsBalance)
        return render_template('savings.html',firstSavingsDate=firstSavingsDate, savingBalance=savingsBalance)
    else:
        return redirect('/modifybalance')

@app.route('/transactions', methods=["GET","POST"])
def transactions():
    transactionsToDisplay = Transactions.query.filter_by(username='test').order_by(Transactions.date.desc()).all()
    return render_template('transactions.html', transactionHistory=transactionsToDisplay)

@app.route('/deposits', methods=["GET","POST"])
#date gets passed as None even though values are passed
#How to modifty the checking amount of the existing user?
def modifyDeposits():
    if request.method == "POST":
        depositAmount = float(request.form.get('amount'))
        transactionDate = request.form.get('date')
        percentToSavings = float(request.form.get('savingPercent'))
        #return str(type(percentToSavings))
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
#cannot open expenses page get 404
def modifyExpenses():
    if request.method == "POST":
        amountToDeduct = request.args.get('amount')
        date = request.args.get('date')
        category = request.args.get('expenseCategory')
        return render_template('expenses.html')
    else:
        return redirect('index.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)